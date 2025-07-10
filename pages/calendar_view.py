import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def show_calendar_view():
    st.header("📅 Daily Nutrition Calendar")
    
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    
    # Mobile-friendly date selector
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("← Previous Day"):
            st.session_state.current_date -= timedelta(days=1)
            st.rerun()
    
    with col2:
        selected_date = st.date_input(
            "Select Date",
            value=st.session_state.current_date,
            max_value=date.today(),
            key="calendar_date_picker"
        )
        if selected_date != st.session_state.current_date:
            st.session_state.current_date = selected_date
            st.rerun()
    
    with col3:
        if st.button("Next Day →") and st.session_state.current_date < date.today():
            st.session_state.current_date += timedelta(days=1)
            st.rerun()
    
    date_str = st.session_state.current_date.isoformat()
    
    # Quick stats for the day
    daily_totals = data_storage.get_daily_totals(date_str)
    user_profile = st.session_state.user_profile
    
    # Calculate daily goals
    bmr = nutrition_calc.calculate_bmr(
        user_profile['weight_kg'], 
        user_profile['height_cm'], 
        user_profile['age'], 
        user_profile['gender']
    )
    tdee = nutrition_calc.calculate_tdee(bmr, user_profile['activity_level'])
    daily_goals = nutrition_calc.calculate_daily_goals(
        tdee, user_profile['goal'], user_profile['gender'], user_profile['age']
    )
    
    # Daily summary cards
    st.subheader(f"📊 Summary for {st.session_state.current_date.strftime('%B %d, %Y')}")
    
    # Mobile-responsive layout: 2x2 grid on mobile, 1x4 on desktop
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        calories_consumed = daily_totals.get('calories', 0)
        calories_goal = daily_goals['calories']
        calories_remaining = calories_goal - calories_consumed
        
        st.metric(
            "Calories",
            f"{calories_consumed:.0f}",
            f"{calories_remaining:+.0f} remaining"
        )
    
    with col2:
        protein_consumed = daily_totals.get('protein', 0)
        protein_goal = daily_goals['protein']
        protein_pct = (protein_consumed / protein_goal) * 100 if protein_goal > 0 else 0
        
        st.metric(
            "Protein",
            f"{protein_consumed:.1f}g",
            f"{protein_pct:.0f}% of goal"
        )
    
    with col3:
        carbs_consumed = daily_totals.get('carbohydrates', 0)
        carbs_goal = daily_goals['carbohydrates']
        carbs_pct = (carbs_consumed / carbs_goal) * 100 if carbs_goal > 0 else 0
        
        st.metric(
            "Carbs",
            f"{carbs_consumed:.1f}g",
            f"{carbs_pct:.0f}% of goal"
        )
    
    with col4:
        fat_consumed = daily_totals.get('fat', 0)
        fat_goal = daily_goals['fat']
        fat_pct = (fat_consumed / fat_goal) * 100 if fat_goal > 0 else 0
        
        st.metric(
            "Fat",
            f"{fat_consumed:.1f}g",
            f"{fat_pct:.0f}% of goal"
        )
    
    # Food entries for the day
    st.subheader("🍽️ Food Entries")
    
    entries = data_storage.get_daily_entries(date_str)
    
    if entries:
        for i, entry in enumerate(entries):
            # Shorter food name for mobile
            food_name = entry['food_name']
            if len(food_name) > 40:
                food_name = food_name[:37] + "..."
            
            with st.expander(f"{food_name} - {entry['portion_size']}g"):
                # Mobile-friendly layout: single column for food details
                st.write(f"**Calories:** {entry['nutrients'].get('calories', 0):.1f}")
                
                # Show key nutrients in a more compact format
                key_nutrients = ['protein', 'carbohydrates', 'fat']
                nutrient_summary = []
                
                for nutrient in key_nutrients:
                    amount = entry['nutrients'].get(nutrient, 0)
                    if amount > 0:
                        unit = nutrition_calc.get_nutrient_unit(nutrient)
                        nutrient_summary.append(f"{nutrient.title()}: {amount:.1f}{unit}")
                
                if nutrient_summary:
                    st.write("**Macros:** " + " | ".join(nutrient_summary))
                
                # Other nutrients in compact format
                other_nutrients = []
                for nutrient, amount in entry['nutrients'].items():
                    if nutrient not in ['calories'] + key_nutrients and amount > 0:
                        unit = nutrition_calc.get_nutrient_unit(nutrient)
                        display_name = nutrition_calc.get_nutrient_display_name(nutrient)
                        other_nutrients.append(f"{display_name}: {amount:.1f}{unit}")
                
                if other_nutrients:
                    with st.expander(f"View all nutrients ({len(other_nutrients)})"):
                        for nutrient_str in other_nutrients:
                            st.write(f"• {nutrient_str}")
                
                # Remove button - full width for mobile
                if st.button(f"🗑️ Remove {food_name[:15]}{'...' if len(entry['food_name']) > 15 else ''}", 
                           key=f"remove_{i}", 
                           use_container_width=True):
                    data_storage.remove_food_entry(date_str, entry['entry_id'])
                    st.rerun()
    else:
        st.info("No food entries for this date. Use the 'Add Food' tab to log your meals!")
    
    # Weekly summary chart
    if st.checkbox("Show Weekly Summary"):
        show_weekly_summary(data_storage, nutrition_calc, daily_goals)

def show_weekly_summary(data_storage, nutrition_calc, daily_goals):
    st.subheader("📈 Weekly Nutrition Trends")
    
    # Get data for the last 7 days
    end_date = st.session_state.current_date
    start_date = end_date - timedelta(days=6)
    
    dates = []
    calories_data = []
    protein_data = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        daily_totals = data_storage.get_daily_totals(date_str)
        
        dates.append(current_date.strftime('%m/%d'))
        calories_data.append(daily_totals.get('calories', 0))
        protein_data.append(daily_totals.get('protein', 0))
        
        current_date += timedelta(days=1)
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_calories = go.Figure()
        fig_calories.add_trace(go.Scatter(
            x=dates, 
            y=calories_data,
            mode='lines+markers',
            name='Calories Consumed',
            line=dict(color='#1976D2', width=3),
            marker=dict(size=8, color='#1976D2')
        ))
        fig_calories.add_hline(
            y=daily_goals['calories'], 
            line_dash="dash", 
            line_color="#4CAF50",
            line_width=2,
            annotation_text="Goal"
        )
        fig_calories.update_layout(
            title="Daily Calories",
            xaxis_title="Date",
            yaxis_title="Calories",
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_calories, use_container_width=True)
    
    with col2:
        fig_protein = go.Figure()
        fig_protein.add_trace(go.Scatter(
            x=dates, 
            y=protein_data,
            mode='lines+markers',
            name='Protein Consumed',
            line=dict(color='#03DAC6', width=3),
            marker=dict(size=8, color='#03DAC6')
        ))
        fig_protein.add_hline(
            y=daily_goals['protein'], 
            line_dash="dash", 
            line_color="#4CAF50",
            line_width=2,
            annotation_text="Goal"
        )
        fig_protein.update_layout(
            title="Daily Protein",
            xaxis_title="Date",
            yaxis_title="Protein (g)",
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_protein, use_container_width=True)
