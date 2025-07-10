# Nutrient Tracker Application

## Overview

This is a comprehensive nutrition tracking application built with Streamlit that allows users to monitor their daily food intake, track body measurements, and analyze nutritional progress. The application integrates with the USDA Food Data Central API to provide accurate nutritional information for a wide variety of foods.

## User Preferences

Preferred communication style: Simple, everyday language.
Mobile-first design: Interface optimized for mobile devices with responsive layouts.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Pattern**: Multi-page application using Streamlit tabs for navigation
- **Responsive Design**: Mobile-first interface with responsive layouts, optimized tab navigation, and centered layout
- **Mobile Optimizations**: Custom CSS for mobile-friendly tabs, metrics, buttons, and form inputs
- **Visualization**: Plotly for interactive charts with mobile-optimized dimensions and margins
- **State Management**: Streamlit session state for maintaining user data and application state

### Backend Architecture
- **Language**: Python
- **Structure**: Modular design with separate utility modules and page components
- **Data Processing**: Pandas for data manipulation and analysis
- **API Integration**: Custom wrapper for USDA Food Data Central API

### Data Storage Solutions
- **Authenticated Users**: PostgreSQL database with persistent storage across sessions
- **Guest Users**: Streamlit session state (in-memory storage for demonstration)
- **Database Schema**: Users, food_entries, and measurements tables with proper relationships
- **Data Migration**: Automatic switching between session and database storage based on authentication status

### Authentication and Authorization
- **OAuth Integration**: Google OAuth 2.0 for secure user authentication
- **User Management**: Multi-user support with individual data isolation
- **Database Storage**: User profiles and data permanently stored in PostgreSQL
- **Guest Mode**: Session-based storage for users who prefer not to authenticate
- **Security**: Secure authentication flow with proper state validation

## Key Components

### Core Modules

1. **app.py** - Main application entry point
   - Streamlit configuration and page routing
   - Session state initialization
   - User profile management

2. **pages/calendar_view.py** - Daily nutrition calendar
   - Date navigation and selection
   - Daily nutrition summaries
   - Progress visualization for selected dates

3. **pages/food_search.py** - Food search and logging
   - USDA API integration for food lookup
   - Food selection and portion size entry
   - Nutritional information display

4. **pages/measurements.py** - Body measurement tracking
   - Current stats display
   - Measurement entry forms
   - Historical data visualization

5. **pages/progress.py** - Progress analysis and reporting
   - Daily progress tracking
   - Weekly trend analysis
   - Goal achievement metrics

### Utility Classes

1. **utils/data_storage.py** - Data management layer
   - Session-based storage operations
   - Daily entry management
   - Nutritional totals calculation

2. **utils/nutrition_calculator.py** - Nutritional calculations
   - BMI, BMR, and TDEE calculations
   - Daily nutritional goal setting
   - Reference daily values for nutrients

3. **utils/usda_api.py** - External API integration
   - USDA Food Data Central API wrapper
   - Food search functionality
   - Error handling and data formatting

## Data Flow

1. **User Input** → Food search queries and measurement data
2. **API Processing** → USDA API calls for food nutritional data
3. **Data Storage** → Session state storage of user entries
4. **Calculation** → Nutritional analysis and goal tracking
5. **Visualization** → Plotly charts and progress displays
6. **User Interface** → Streamlit components for data presentation

## External Dependencies

### Third-Party APIs
- **USDA Food Data Central API**: Primary source for food nutritional data
  - Provides comprehensive nutrient profiles
  - Supports food search functionality
  - Requires API key (defaults to DEMO_KEY)

### Python Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualization
- **requests**: HTTP client for API calls
- **datetime**: Date and time handling

### Environment Configuration
- **USDA_API_KEY**: Environment variable for API authentication
- **Streamlit configuration**: Page layout and UI settings

## Deployment Strategy

### Current Setup
- **Platform**: Designed for Streamlit deployment
- **Configuration**: Single-file deployment with `app.py` as entry point
- **Dependencies**: Standard Python package requirements
- **Environment**: Requires Python 3.7+ with specified package dependencies

### Scalability Considerations
- **Data Persistence**: Current session-based storage is not suitable for production
- **Database Integration**: Would benefit from persistent database (PostgreSQL recommended)
- **User Management**: Requires authentication system for multi-user deployment
- **API Rate Limiting**: May need caching layer for USDA API calls

### Production Readiness
- **Current State**: Prototype/demonstration application
- **Required Improvements**:
  - Persistent data storage implementation
  - User authentication and authorization
  - Error handling and logging enhancements
  - API rate limiting and caching
  - Data backup and recovery mechanisms

The application follows a clean architectural pattern with separation of concerns, making it suitable for further development and scaling to a production environment with the addition of persistent storage and user management systems.

## Recent Changes

### Mobile-Friendly Interface Updates (July 10, 2025)
- **Layout Optimization**: Changed from wide to centered layout for better mobile experience
- **Tab Navigation**: Shortened tab labels and improved mobile tab styling with horizontal scrolling
- **Responsive Grids**: Updated all column layouts from 4-column to 2x2 grids for mobile compatibility
- **Button Improvements**: Added full-width buttons with `use_container_width=True` for better mobile interaction
- **Chart Optimization**: Reduced chart heights and added proper margins for mobile viewing
- **Typography**: Improved font sizes and input field sizing for mobile devices
- **CSS Enhancements**: Added comprehensive mobile-first CSS with viewport meta tags and responsive breakpoints
- **Form Layout**: Reorganized measurement forms with clearer sections and mobile-friendly input grouping
- **Food Search**: Improved search result display with compact layouts and better mobile interaction patterns

### Material Design Implementation (July 10, 2025)
- **Design System**: Implemented Google Material Design principles throughout the application
- **Color Palette**: Updated to Material Design color scheme with primary blue (#1976D2), secondary teal (#03DAC6), and semantic colors
- **Typography**: Integrated Roboto font family with proper font weights and hierarchy
- **Component Styling**: Enhanced tabs with Material Design specifications including hover states and active indicators
- **Card Design**: Applied Material Design elevation and shadow system to metrics and content cards
- **Button Enhancement**: Implemented Material Design button styles with proper elevation, ripple effects, and state transitions
- **Input Fields**: Updated form inputs with Material Design styling including focus states and borders
- **Progress Bars**: Enhanced with Material Design colors and gradient styling
- **Charts**: Updated all Plotly charts with Material Design color palette for consistency
- **Navigation**: Improved tab navigation with Material Design principles including proper spacing and typography
- **Elevation System**: Applied consistent shadow and elevation levels throughout the interface

### Database and Authentication Implementation (July 10, 2025)
- **PostgreSQL Integration**: Set up production-ready database with proper schema and relationships
- **Google OAuth 2.0**: Implemented secure authentication flow with Google account integration
- **User Management**: Created comprehensive user registration and profile management system
- **Data Persistence**: Added permanent storage for authenticated users with seamless data migration
- **Dual Storage Mode**: Session storage for guests, database storage for authenticated users
- **Security Features**: Proper OAuth state validation, secure session management, and data isolation
- **Database Schema**: Users, food_entries, and measurements tables with indexes for performance
- **Error Handling**: Comprehensive error handling for authentication failures and database operations

### Google OAuth Setup Instructions
To enable Google authentication, configure OAuth 2.0 credentials in Google Cloud Console:
1. Create or select a Google Cloud Project
2. Enable Google+ API or Google Identity services
3. Create OAuth 2.0 Client ID credentials
4. Add authorized redirect URI: `https://your-repl-domain.repl.co`
5. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables
6. Users can then sign in with Google accounts for permanent data storage