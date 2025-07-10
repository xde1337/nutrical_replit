import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

def show_measurements():
    st.header("📏 Body Measurements")
    
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Current Stats", "📈 Track Progress", "📋 History"])
    
    with tab1:
        show_current_stats()
    
    with tab2:
        show_add_measurement()
    
    with tab3:
        show_measurement_history()

def show_current_stats():
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    user_profile = st.session_state.user_profile
    
    st.subheader("📊 Current Statistics")
    
    # Get latest measurement or use profile data
    latest_measurement = data_storage.get_latest_measurement()
    
    if latest_measurement:
        weight = latest_measurement.get('weight_kg', user_profile['weight_kg'])
        height = latest_measurement.get('height_cm', user_profile['height_cm'])
        body_fat = latest_measurement.get('body_fat_percent')
        muscle_mass = latest_measurement.get('muscle_mass_kg')
        measurement_date = latest_measurement.get('date', 'Unknown')
    else:
        weight = user_profile['weight_kg']
        height = user_profile['height_cm']
        body_fat = None
        muscle_mass = None
        measurement_date = 'From profile'
    
    # Calculate derived metrics
    bmi = nutrition_calc.calculate_bmi(weight, height)
    bmr = nutrition_calc.calculate_bmr(weight, height, user_profile['age'], user_profile['gender'])
    tdee = nutrition_calc.calculate_tdee(bmr, user_profile['activity_level'])
    
    # Mobile-responsive metrics display: 2x2 grid
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        st.metric("Weight", f"{weight:.1f} kg", help=f"Last updated: {measurement_date}")
        st.metric("Height", f"{height:.1f} cm")
    
    with col2:
        st.metric("BMI", f"{bmi:.1f}")
        
        # BMI category
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
    
    with col3:
        st.metric("BMR", f"{bmr:.0f} cal/day", help="Basal Metabolic Rate")
        st.metric("TDEE", f"{tdee:.0f} cal/day", help="Total Daily Energy Expenditure")
    
    with col4:
        if body_fat is not None:
            st.metric("Body Fat", f"{body_fat:.1f}%")
        else:
            st.metric("Body Fat", "Not recorded")
            
        if muscle_mass is not None:
            st.metric("Muscle Mass", f"{muscle_mass:.1f} kg")
        else:
            st.metric("Muscle Mass", "Not recorded")
    
    # Body composition chart (if data available)
    if body_fat is not None:
        show_body_composition_chart(weight, body_fat, muscle_mass)

def show_body_composition_chart(weight, body_fat_percent, muscle_mass):
    st.subheader("🧬 Body Composition")
    
    # Calculate body composition
    fat_mass = weight * (body_fat_percent / 100)
    
    if muscle_mass is not None:
        other_mass = weight - fat_mass - muscle_mass
        labels = ['Muscle Mass', 'Fat Mass', 'Other (Bone, Organs, Water)']
        values = [muscle_mass, fat_mass, max(0, other_mass)]
    else:
        lean_mass = weight - fat_mass
        labels = ['Lean Mass', 'Fat Mass']
        values = [lean_mass, fat_mass]
    
    # Create pie chart with Material Design colors
    fig = px.pie(
        values=values,
        names=labels,
        title="Body Composition Breakdown",
        color_discrete_sequence=['#1976D2', '#F44336', '#4CAF50']
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

def show_add_measurement():
    st.subheader("📈 Record New Measurement")
    
    data_storage = st.session_state.data_storage
    user_profile = st.session_state.user_profile
    
    # Get current values for defaults
    latest = data_storage.get_latest_measurement()
    current_weight = latest.get('weight_kg', user_profile['weight_kg']) if latest else user_profile['weight_kg']
    current_height = latest.get('height_cm', user_profile['height_cm']) if latest else user_profile['height_cm']
    
    with st.form("measurement_form"):
        # Mobile-friendly single column layout
        st.subheader("Basic Measurements")
        
        measurement_date = st.date_input(
            "Measurement Date",
            value=date.today(),
            max_value=date.today()
        )
        
        # Primary measurements in columns for mobile
        col1, col2 = st.columns(2)
        
        with col1:
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                value=float(current_weight),
                step=0.1
            )
        
        with col2:
            height_cm = st.number_input(
                "Height (cm)",
                min_value=100.0,
                max_value=250.0,
                value=float(current_height),
                step=0.1
            )
        
        st.subheader("Body Composition (Optional)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            body_fat_percent = st.number_input(
                "Body Fat (%)",
                min_value=0.0,
                max_value=60.0,
                value=0.0,
                step=0.1,
                help="Leave as 0 if unknown"
            )
        
        with col4:
            muscle_mass_kg = st.number_input(
                "Muscle Mass (kg)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="Leave as 0 if unknown"
            )
        
        waist_cm = st.number_input(
            "Waist Circumference (cm)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=0.1,
            help="Optional - leave as 0 if unknown"
        )
        
        notes = st.text_area(
            "Notes",
            placeholder="Any additional notes about this measurement...",
            help="Optional notes about the measurement conditions, time of day, etc."
        )
        
        submitted = st.form_submit_button("📊 Record Measurement", type="primary", use_container_width=True)
        
        if submitted:
            measurement_data = {
                'date': measurement_date.isoformat(),
                'weight_kg': weight_kg,
                'height_cm': height_cm,
                'body_fat_percent': body_fat_percent if body_fat_percent > 0 else None,
                'muscle_mass_kg': muscle_mass_kg if muscle_mass_kg > 0 else None,
                'waist_cm': waist_cm if waist_cm > 0 else None,
                'notes': notes.strip() if notes.strip() else None
            }
            
            data_storage.add_measurement(measurement_data)
            
            # Update user profile with latest weight and height
            st.session_state.user_profile['weight_kg'] = weight_kg
            st.session_state.user_profile['height_cm'] = height_cm
            
            st.success("✅ Measurement recorded successfully!")
            st.rerun()

def show_measurement_history():
    st.subheader("📋 Measurement History")
    
    data_storage = st.session_state.data_storage
    measurements = data_storage.get_measurements_history()
    
    if not measurements:
        st.info("No measurements recorded yet. Use the 'Track Progress' tab to add your first measurement.")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(measurements)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Mobile-friendly display options
    col1, col2 = st.columns([1, 1])
    
    with col1:
        show_count = st.selectbox("Show last", [10, 20, 50, "All"], index=0)
        if show_count != "All":
            df_display = df.head(show_count)
        else:
            df_display = df
    
    with col2:
        chart_metric = st.selectbox(
            "Chart Metric",
            ["weight_kg", "body_fat_percent", "muscle_mass_kg", "waist_cm"],
            format_func=lambda x: {
                "weight_kg": "Weight",
                "body_fat_percent": "Body Fat %",
                "muscle_mass_kg": "Muscle Mass",
                "waist_cm": "Waist Circumference"
            }.get(x, x)
        )
    
    # Show chart
    if len(df) > 1 and chart_metric in df.columns:
        chart_data = df[df[chart_metric].notna()].copy()
        
        if not chart_data.empty:
            fig = px.line(
                chart_data,
                x='date',
                y=chart_metric,
                title=f"{chart_metric.replace('_', ' ').title()} Over Time",
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title=chart_metric.replace('_', ' ').title(),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No data available for {chart_metric.replace('_', ' ').title()}")
    
    # Show table
    st.subheader("📊 Detailed History")
    
    # Format the display dataframe
    display_df = df_display.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    # Rename columns for display
    column_names = {
        'date': 'Date',
        'weight_kg': 'Weight (kg)',
        'height_cm': 'Height (cm)',
        'body_fat_percent': 'Body Fat (%)',
        'muscle_mass_kg': 'Muscle Mass (kg)',
        'waist_cm': 'Waist (cm)',
        'notes': 'Notes'
    }
    
    # Select and rename columns that have data
    cols_to_show = ['date', 'weight_kg', 'height_cm']
    for col in ['body_fat_percent', 'muscle_mass_kg', 'waist_cm', 'notes']:
        if col in display_df.columns and display_df[col].notna().any():
            cols_to_show.append(col)
    
    display_df = display_df[cols_to_show].rename(columns=column_names)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export option
    if st.button("📥 Export Measurements as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"measurements_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
