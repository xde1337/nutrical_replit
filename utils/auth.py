import streamlit as st
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import json
from typing import Optional, Dict
from .database import DatabaseManager, User

class GoogleAuth:
    def __init__(self):
        # These would normally come from Google Cloud Console
        # Get current domain from Replit environment
        replit_domain = os.getenv('REPLIT_DOMAINS')
        if replit_domain:
            redirect_uri = f"https://{replit_domain.split(',')[0]}"
        else:
            redirect_uri = "http://localhost:5000"
            
        self.client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        self.scopes = ['openid', 'email', 'profile']
        self.db = DatabaseManager()
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        if not self.client_config["web"]["client_id"]:
            return None
            
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = self.client_config["web"]["redirect_uris"][0]
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state in session for validation
        st.session_state.oauth_state = state
        return authorization_url
    
    def handle_callback(self, code: str, state: str) -> Optional[Dict]:
        """Handle OAuth callback and return user info"""
        if not self.client_config["web"]["client_id"]:
            return None
            
        # Validate state
        if state != st.session_state.get('oauth_state'):
            return None
            
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.client_config["web"]["redirect_uris"][0]
            
            # Exchange code for token
            flow.fetch_token(code=code)
            
            # Get user info
            credentials = flow.credentials
            user_info = self._get_user_info(credentials)
            
            if user_info:
                # Create or update user in database
                user = self.db.create_or_update_user(
                    google_id=user_info['id'],
                    email=user_info['email'],
                    name=user_info['name'],
                    profile_picture=user_info.get('picture')
                )
                
                return {
                    'id': user.id,
                    'google_id': user.google_id,
                    'email': user.email,
                    'name': user.name,
                    'profile_picture': user.profile_picture
                }
                
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            return None
        
        return None
    
    def _get_user_info(self, credentials) -> Optional[Dict]:
        """Get user information from Google API"""
        try:
            import requests
            
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'}
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            st.error(f"Failed to get user info: {str(e)}")
            
        return None
    
    def logout(self):
        """Clear authentication session"""
        keys_to_remove = [
            'authenticated', 'user_info', 'oauth_state', 
            'user_id', 'current_user'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]

def show_auth_ui():
    """Show authentication UI"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background-color: var(--md-surface); 
                    border-radius: 12px; box-shadow: var(--md-elevation-2); margin: 2rem 0;">
            <h2 style="color: var(--md-on-surface); margin-bottom: 1rem;">Welcome to Nutrient Tracker</h2>
            <p style="color: var(--md-on-surface-variant); margin-bottom: 2rem;">
                Sign in with your Google account to start tracking your nutrition and health data.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        auth = GoogleAuth()
        
        # Check if we have Google OAuth credentials
        if not os.getenv('GOOGLE_CLIENT_ID'):
            replit_domain = os.getenv('REPLIT_DOMAINS', 'localhost:5000')
            if replit_domain != 'localhost:5000':
                redirect_uri = f"https://{replit_domain.split(',')[0]}"
            else:
                redirect_uri = "http://localhost:5000"
                
            st.error(f"""
            **Google OAuth Configuration Error (403)**
            
            The redirect URI is not authorized. Please add this URI to your Google Cloud Console:
            
            **Redirect URI to add:** `{redirect_uri}`
            
            Steps to fix:
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Navigate to: APIs & Services → Credentials
            3. Click on your OAuth 2.0 Client ID
            4. Under "Authorized redirect URIs", click "ADD URI"
            5. Add: `{redirect_uri}`
            6. Click "SAVE"
            """)
            
            st.info("You can continue as a guest user. Your data will be saved in your browser session.")
            
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_info = {
                    'id': 0,
                    'name': 'Guest User',
                    'email': 'guest@example.com'
                }
                st.rerun()
            return False
        
        # Show Google sign-in button
        auth_url = auth.get_authorization_url()
        if auth_url:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔐 Sign in with Google", use_container_width=True, type="primary"):
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
                    st.success("Redirecting to Google...")
                    st.stop()
        
        # Handle OAuth callback
        query_params = st.query_params
        if 'code' in query_params and 'state' in query_params:
            user_info = auth.handle_callback(query_params['code'], query_params['state'])
            if user_info:
                st.session_state.authenticated = True
                st.session_state.user_info = user_info
                st.session_state.user_id = user_info['id']
                # Clear query params
                st.query_params.clear()
                st.rerun()
        
        return False
    
    return True

def show_user_profile():
    """Show user profile in sidebar"""
    if st.session_state.get('authenticated') and st.session_state.get('user_info'):
        user_info = st.session_state.user_info
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 User Profile")
            
            if user_info.get('profile_picture'):
                st.image(user_info['profile_picture'], width=60)
            
            st.write(f"**{user_info['name']}**")
            st.write(f"📧 {user_info['email']}")
            
            if st.button("🚪 Sign Out", use_container_width=True):
                auth = GoogleAuth()
                auth.logout()
                st.rerun()

def require_auth():
    """Decorator to require authentication"""
    if not show_auth_ui():
        st.stop()
    
    # Show user profile in sidebar
    show_user_profile()
    
    return st.session_state.get('user_id', 0)