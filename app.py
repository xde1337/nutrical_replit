import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from utils.data_storage import DataStorage
from utils.database_storage import DatabaseDataStorage
from utils.nutrition_calculator import NutritionCalculator
from utils.auth import require_auth, show_auth_ui
import pages.calendar_view as calendar_view
import pages.food_search as food_search
import pages.measurements as measurements
import pages.progress as progress
import os

# Configure page
st.set_page_config(
    page_title="Nutrient Tracker",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def init_app():
    """Initialize app components"""
    # Check authentication first
    if not show_auth_ui():
        return False
    
    # Get user ID from authentication
    user_id = st.session_state.get('user_id', 0)
    
    # Initialize data storage based on authentication
    if 'data_storage' not in st.session_state or st.session_state.get('current_user_id') != user_id:
        if user_id > 0:
            # Authenticated user - use database storage
            st.session_state.data_storage = DatabaseDataStorage(user_id)
        else:
            # Guest user - use session storage
            st.session_state.data_storage = DataStorage()
        st.session_state.current_user_id = user_id

    if 'nutrition_calculator' not in st.session_state:
        st.session_state.nutrition_calculator = NutritionCalculator()

    # Initialize session state variables
    if 'current_date' not in st.session_state:
        st.session_state.current_date = date.today()

    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'age': 30,
            'gender': 'male',
            'weight_kg': 70,
            'height_cm': 175,
            'activity_level': 'moderate',
            'goal': 'maintain'
        }
    
    return True

def main():
    # Initialize app and check authentication
    if not init_app():
        return
    
    # Show user profile in sidebar for authenticated users
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
                from utils.auth import GoogleAuth
                auth = GoogleAuth()
                auth.logout()
                st.rerun()
    
    # Material Design CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Material Design Color Palette */
    :root {
        --md-primary: #1976D2;
        --md-primary-dark: #1565C0;
        --md-primary-light: #42A5F5;
        --md-secondary: #03DAC6;
        --md-surface: #FFFFFF;
        --md-background: #FAFAFA;
        --md-surface-variant: #F5F5F5;
        --md-on-surface: #1C1B1F;
        --md-on-surface-variant: #49454F;
        --md-outline: #E0E0E0;
        --md-success: #4CAF50;
        --md-warning: #FF9800;
        --md-error: #F44336;
        --md-elevation-1: 0px 1px 3px rgba(0,0,0,0.12), 0px 1px 2px rgba(0,0,0,0.24);
        --md-elevation-2: 0px 3px 6px rgba(0,0,0,0.16), 0px 3px 6px rgba(0,0,0,0.23);
        --md-elevation-3: 0px 10px 20px rgba(0,0,0,0.19), 0px 6px 6px rgba(0,0,0,0.23);
    }
    
    /* Global Typography */
    .main {
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--md-background);
    }
    
    /* Material Design Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: var(--md-surface);
        border-bottom: 1px solid var(--md-outline);
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        box-shadow: var(--md-elevation-1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--md-on-surface-variant);
        border-radius: 0;
        background: transparent;
        border: none;
        position: relative;
        transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        flex-shrink: 0;
        min-width: 90px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(25, 118, 210, 0.04);
        color: var(--md-primary);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--md-primary);
        background-color: rgba(25, 118, 210, 0.08);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background-color: var(--md-primary);
        border-radius: 3px 3px 0 0;
    }
    
    /* Material Design Cards for Metrics */
    .element-container .stMetric {
        background-color: var(--md-surface);
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        box-shadow: var(--md-elevation-1);
        border: 1px solid var(--md-outline);
        transition: box-shadow 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
    }
    
    .element-container .stMetric:hover {
        box-shadow: var(--md-elevation-2);
    }
    
    .stMetric .metric-label {
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--md-on-surface-variant);
        margin-bottom: 4px;
    }
    
    .stMetric .metric-value {
        font-size: 24px;
        font-weight: 400;
        color: var(--md-on-surface);
        line-height: 1.2;
    }
    
    /* Material Design Buttons */
    .stButton > button {
        background-color: var(--md-primary);
        color: white;
        border: none;
        border-radius: 24px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        box-shadow: var(--md-elevation-2);
        transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        width: 100%;
        min-height: 48px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        background-color: var(--md-primary-dark);
        box-shadow: var(--md-elevation-3);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: var(--md-elevation-1);
    }
    
    /* Material Design Ripple Effect */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s;
    }
    
    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }
    
    /* Secondary Button Style */
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        color: var(--md-primary);
        border: 1px solid var(--md-primary);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: rgba(25, 118, 210, 0.04);
        transform: translateY(-1px);
    }
    
    /* Material Design Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        border: 1px solid var(--md-outline);
        border-radius: 8px;
        padding: 16px;
        font-size: 16px;
        background-color: var(--md-surface);
        transition: border-color 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--md-primary);
        outline: none;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
    }
    
    /* Material Design Progress Bars */
    .stProgress > div > div > div {
        background-color: var(--md-primary);
        border-radius: 4px;
        height: 8px;
    }
    
    .stProgress > div > div {
        background-color: rgba(25, 118, 210, 0.12);
        border-radius: 4px;
        height: 8px;
    }
    
    /* Material Design Expanders */
    .streamlit-expanderHeader {
        background-color: var(--md-surface);
        border: 1px solid var(--md-outline);
        border-radius: 12px;
        padding: 16px;
        font-size: 14px;
        font-weight: 500;
        color: var(--md-on-surface);
        box-shadow: var(--md-elevation-1);
        transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
    }
    
    .streamlit-expanderHeader:hover {
        box-shadow: var(--md-elevation-2);
        background-color: rgba(25, 118, 210, 0.04);
    }
    
    .streamlit-expanderContent {
        background-color: var(--md-surface);
        border: 1px solid var(--md-outline);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 16px;
    }
    
    /* Material Design Headers */
    h1, h2, h3 {
        font-family: 'Roboto', sans-serif;
        color: var(--md-on-surface);
        font-weight: 400;
        line-height: 1.2;
    }
    
    h1 {
        font-size: 28px;
        font-weight: 300;
        margin-bottom: 8px;
    }
    
    h2 {
        font-size: 22px;
        font-weight: 400;
        margin: 32px 0 16px 0;
        border-bottom: 1px solid var(--md-outline);
        padding-bottom: 8px;
    }
    
    h3 {
        font-size: 18px;
        font-weight: 500;
        margin: 24px 0 12px 0;
        color: var(--md-primary);
    }
    
    /* Material Design Subheadings */
    .element-container h2 {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .element-container h3 {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Material Design Form Container */
    .stForm {
        background-color: var(--md-surface);
        border-radius: 12px;
        padding: 24px;
        box-shadow: var(--md-elevation-1);
        border: 1px solid var(--md-outline);
        margin: 16px 0;
    }
    
    /* Success/Warning/Error States */
    .stSuccess {
        background-color: #E8F5E8;
        border-left: 4px solid var(--md-success);
        border-radius: 8px;
        padding: 16px;
    }
    
    .stWarning {
        background-color: #FFF3E0;
        border-left: 4px solid var(--md-warning);
        border-radius: 8px;
        padding: 16px;
    }
    
    .stError {
        background-color: #FFEBEE;
        border-left: 4px solid var(--md-error);
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Mobile Material Design Adjustments */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 12px;
            padding: 0 16px;
            min-width: 80px;
        }
        
        .block-container {
            padding: 1rem;
        }
        
        .element-container .stMetric {
            padding: 12px;
            margin: 6px 0;
        }
        
        .stButton > button {
            padding: 10px 20px;
            min-height: 44px;
        }
        
        .stForm {
            padding: 16px;
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 11px;
            padding: 0 12px;
            min-width: 70px;
        }
        
        h1 {
            font-size: 20px;
        }
        
        h2 {
            font-size: 18px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add mobile viewport meta tag
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """, unsafe_allow_html=True)
    
    # Material Design header with better typography
    st.markdown("""
    <div style="text-align: left; margin-bottom: 24px;">
        <h1 style="font-size: 28px; font-weight: 400; color: var(--md-on-surface); margin: 0; 
                   display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 32px;">🥗</span>
            Nutrient Tracker
        </h1>
        <p style="font-size: 16px; color: var(--md-on-surface-variant); margin: 8px 0 0 44px; font-weight: 400;">
            Track your daily nutrition with comprehensive vitamin and mineral monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Material Design navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 TODAY", 
        "🔍 ADD FOOD", 
        "📊 PROGRESS", 
        "📏 BODY",
        "⚙️ SETTINGS"
    ])
    
    with tab1:
        calendar_view.show_calendar_view()
    
    with tab2:
        food_search.show_food_search()
    
    with tab3:
        progress.show_progress_view()
    
    with tab4:
        measurements.show_measurements()
    
    with tab5:
        show_settings()

def show_settings():
    st.header("⚙️ Settings")
    
    # Use single column on mobile, two columns on desktop
    if st.session_state.get('mobile_layout', True):
        col1 = st.container()
        col2 = st.container()
    else:
        col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        age = st.number_input("Age", min_value=10, max_value=120, value=st.session_state.user_profile['age'])
        gender = st.selectbox("Gender", ["male", "female"], index=0 if st.session_state.user_profile['gender'] == 'male' else 1)
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(st.session_state.user_profile['weight_kg']), step=0.1)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(st.session_state.user_profile['height_cm']), step=0.1)
    
    with col2:
        st.subheader("Activity & Goals")
        activity_levels = {
            'sedentary': 'Sedentary (little/no exercise)',
            'light': 'Light (light exercise 1-3 days/week)',
            'moderate': 'Moderate (moderate exercise 3-5 days/week)',
            'very_active': 'Very Active (hard exercise 6-7 days/week)',
            'extremely_active': 'Extremely Active (very hard exercise, physical job)'
        }
        
        activity_level = st.selectbox(
            "Activity Level",
            options=list(activity_levels.keys()),
            format_func=lambda x: activity_levels[x],
            index=list(activity_levels.keys()).index(st.session_state.user_profile['activity_level'])
        )
        
        goals = {
            'lose': 'Lose Weight',
            'maintain': 'Maintain Weight',
            'gain': 'Gain Weight'
        }
        
        goal = st.selectbox(
            "Goal",
            options=list(goals.keys()),
            format_func=lambda x: goals[x],
            index=list(goals.keys()).index(st.session_state.user_profile['goal'])
        )
    
    if st.button("Save Settings", type="primary"):
        st.session_state.user_profile.update({
            'age': age,
            'gender': gender,
            'weight_kg': weight,
            'height_cm': height,
            'activity_level': activity_level,
            'goal': goal
        })
        st.success("Settings saved successfully!")
        st.rerun()
    
    # Display calculated values
    st.subheader("Calculated Values")
    calc = st.session_state.nutrition_calculator
    
    # Responsive columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        bmi = calc.calculate_bmi(weight, height)
        st.metric("BMI", f"{bmi:.1f}")
        
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
    
    with col2:
        bmr = calc.calculate_bmr(weight, height, age, gender)
        st.metric("BMR", f"{bmr:.0f} cal")
    
    with col3:
        tdee = calc.calculate_tdee(bmr, activity_level)
        st.metric("TDEE", f"{tdee:.0f} cal")

if __name__ == "__main__":
    main()
