import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_progress_view():
    st.header("📊 Nutrition Progress")
    
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
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
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Today's Progress", "📈 Weekly Trends", "🎯 Goal Analysis"])
    
    with tab1:
        show_daily_progress(data_storage, nutrition_calc, daily_goals)
    
    with tab2:
        show_weekly_trends(data_storage, nutrition_calc, daily_goals)
    
    with tab3:
        show_goal_analysis(data_storage, nutrition_calc, daily_goals)

def show_daily_progress(data_storage, nutrition_calc, daily_goals):
    st.subheader(f"📋 Today's Progress - {st.session_state.current_date.strftime('%B %d, %Y')}")
    
    date_str = st.session_state.current_date.isoformat()
    daily_totals = data_storage.get_daily_totals(date_str)
    
    if not daily_totals:
        st.info("No food entries for today. Use the 'Add Food' tab to start tracking!")
        return
    
    # Macronutrient progress - mobile-responsive 2x2 grid
    st.subheader("🥗 Macronutrients")
    
    macros = ['calories', 'protein', 'carbohydrates', 'fat']
    
    # First row: Calories and Protein
    col1, col2 = st.columns(2)
    for i, macro in enumerate(macros[:2]):
        with [col1, col2][i]:
            consumed = daily_totals.get(macro, 0)
            goal = daily_goals.get(macro, 1)
            percentage = nutrition_calc.calculate_nutrient_percentage(consumed, goal)
            
            progress_value = max(0.0, min(percentage / 100, 1.0))
            display_name = macro.replace('_', ' ').title()
            unit = nutrition_calc.get_nutrient_unit(macro)
            
            st.metric(
                display_name,
                f"{consumed:.1f}{unit}",
                f"{percentage:.0f}% of goal"
            )
            st.progress(progress_value)
            st.caption(f"Goal: {goal:.1f}{unit}")
    
    # Second row: Carbs and Fat
    col3, col4 = st.columns(2)
    for i, macro in enumerate(macros[2:]):
        with [col3, col4][i]:
            consumed = daily_totals.get(macro, 0)
            goal = daily_goals.get(macro, 1)
            percentage = nutrition_calc.calculate_nutrient_percentage(consumed, goal)
            
            progress_value = max(0.0, min(percentage / 100, 1.0))
            display_name = macro.replace('_', ' ').title()
            unit = nutrition_calc.get_nutrient_unit(macro)
            
            st.metric(
                display_name,
                f"{consumed:.1f}{unit}",
                f"{percentage:.0f}% of goal"
            )
            st.progress(progress_value)
            st.caption(f"Goal: {goal:.1f}{unit}")
    
    # Vitamin and Mineral Progress
    nutrient_categories = nutrition_calc.get_nutrient_categories()
    
    for category, nutrients in nutrient_categories.items():
        if category == "Macronutrients":
            continue
            
        # Filter nutrients that have data
        category_data = []
        for nutrient in nutrients:
            if nutrient in daily_totals and daily_totals[nutrient] > 0:
                consumed = daily_totals[nutrient]
                goal = daily_goals.get(nutrient, nutrition_calc.daily_values.get(nutrient, 1))
                percentage = nutrition_calc.calculate_nutrient_percentage(consumed, goal)
                status, emoji = nutrition_calc.get_nutrient_status(percentage)
                
                category_data.append({
                    'nutrient': nutrient,
                    'consumed': consumed,
                    'goal': goal,
                    'percentage': percentage,
                    'status': status,
                    'emoji': emoji
                })
        
        if category_data:
            with st.expander(f"{category} ({len(category_data)} nutrients tracked)"):
                show_nutrient_progress_bars(category_data, nutrition_calc)

def show_nutrient_progress_bars(nutrients_data, nutrition_calc):
    """Display progress bars for a list of nutrients"""
    for nutrient_info in nutrients_data:
        nutrient = nutrient_info['nutrient']
        consumed = nutrient_info['consumed']
        goal = nutrient_info['goal']
        percentage = nutrient_info['percentage']
        status = nutrient_info['status']
        emoji = nutrient_info['emoji']
        
        display_name = nutrition_calc.get_nutrient_display_name(nutrient)
        unit = nutrition_calc.get_nutrient_unit(nutrient)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Material Design progress bar colors
            if percentage < 50:
                bar_color = "#F44336"  # Material Red
            elif percentage < 75:
                bar_color = "#FF9800"  # Material Orange
            elif percentage < 100:
                bar_color = "#FFC107"  # Material Amber
            else:
                bar_color = "#4CAF50"  # Material Green
            
            progress_html = f"""
            <div style="background-color: #E0E0E0; border-radius: 12px; padding: 2px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.12);">
                <div style="background: linear-gradient(90deg, {bar_color} 0%, {bar_color}E6 100%); 
                     width: {min(percentage, 100):.1f}%; height: 24px; border-radius: 10px; 
                     display: flex; align-items: center; justify-content: center; 
                     color: white; font-weight: 500; font-size: 12px; font-family: 'Roboto', sans-serif;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.3s ease;">
                    {percentage:.0f}%
                </div>
            </div>
            """
            
            st.markdown(f"**{display_name}**")
            st.markdown(progress_html, unsafe_allow_html=True)
        
        with col2:
            st.write(f"{consumed:.1f}{unit}")
            st.caption(f"of {goal:.1f}{unit}")
        
        with col3:
            st.write(f"{emoji} {status}")

def show_weekly_trends(data_storage, nutrition_calc, daily_goals):
    st.subheader("📈 Weekly Nutrition Trends")
    
    # Get 7 days of data
    from datetime import timedelta
    
    end_date = st.session_state.current_date
    start_date = end_date - timedelta(days=6)
    
    # Collect data
    dates = []
    calories_data = []
    protein_data = []
    vitamin_c_data = []
    iron_data = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        daily_totals = data_storage.get_daily_totals(date_str)
        
        dates.append(current_date.strftime('%m/%d'))
        calories_data.append(daily_totals.get('calories', 0))
        protein_data.append(daily_totals.get('protein', 0))
        vitamin_c_data.append(daily_totals.get('vitamin_c', 0))
        iron_data.append(daily_totals.get('iron', 0))
        
        current_date += timedelta(days=1)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Calories', 'Protein', 'Vitamin C', 'Iron'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Add traces with Material Design colors
    fig.add_trace(
        go.Scatter(x=dates, y=calories_data, name='Calories', 
                  line=dict(color='#1976D2', width=3), 
                  marker=dict(size=6, color='#1976D2')),
        row=1, col=1
    )
    fig.add_hline(y=daily_goals['calories'], line_dash="dash", line_color="#4CAF50", line_width=2, row=1, col=1)
    
    fig.add_trace(
        go.Scatter(x=dates, y=protein_data, name='Protein', 
                  line=dict(color='#03DAC6', width=3), 
                  marker=dict(size=6, color='#03DAC6')),
        row=1, col=2
    )
    fig.add_hline(y=daily_goals['protein'], line_dash="dash", line_color="#4CAF50", line_width=2, row=1, col=2)
    
    fig.add_trace(
        go.Scatter(x=dates, y=vitamin_c_data, name='Vitamin C', 
                  line=dict(color='#FF9800', width=3), 
                  marker=dict(size=6, color='#FF9800')),
        row=2, col=1
    )
    fig.add_hline(y=daily_goals.get('vitamin_c', 90), line_dash="dash", line_color="#4CAF50", line_width=2, row=2, col=1)
    
    fig.add_trace(
        go.Scatter(x=dates, y=iron_data, name='Iron', 
                  line=dict(color='#9C27B0', width=3), 
                  marker=dict(size=6, color='#9C27B0')),
        row=2, col=2
    )
    fig.add_hline(y=daily_goals.get('iron', 8), line_dash="dash", line_color="#4CAF50", line_width=2, row=2, col=2)
    
    fig.update_layout(
        height=500, 
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Calories", row=1, col=1)
    fig.update_yaxes(title_text="Protein (g)", row=1, col=2)
    fig.update_yaxes(title_text="Vitamin C (mg)", row=2, col=1)
    fig.update_yaxes(title_text="Iron (mg)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Weekly summary stats - mobile-responsive 2x2 grid
    st.subheader("📊 Weekly Summary")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        avg_calories = sum(calories_data) / 7
        goal_calories = daily_goals['calories']
        st.metric(
            "Avg Daily Calories",
            f"{avg_calories:.0f}",
            f"{((avg_calories/goal_calories-1)*100):+.0f}% vs goal"
        )
    
    with col2:
        avg_protein = sum(protein_data) / 7
        goal_protein = daily_goals['protein']
        st.metric(
            "Avg Daily Protein",
            f"{avg_protein:.1f}g",
            f"{((avg_protein/goal_protein-1)*100):+.0f}% vs goal"
        )
    
    with col3:
        days_tracked = sum(1 for c in calories_data if c > 0)
        st.metric("Days Tracked", f"{days_tracked}/7")
    
    with col4:
        avg_vitamin_c = sum(vitamin_c_data) / 7
        goal_vitamin_c = daily_goals.get('vitamin_c', 90)
        st.metric(
            "Avg Vitamin C",
            f"{avg_vitamin_c:.1f}mg",
            f"{((avg_vitamin_c/goal_vitamin_c-1)*100):+.0f}% vs goal"
        )

def show_goal_analysis(data_storage, nutrition_calc, daily_goals):
    st.subheader("🎯 Goal Achievement Analysis")
    
    # Get summary for the last 7 days
    summary = data_storage.get_nutrition_summary(days=7)
    
    if summary['total_days'] == 0:
        st.info("No nutrition data available for analysis. Start tracking your meals to see insights!")
        return
    
    st.write(f"Analysis based on **{summary['total_days']} days** of tracking")
    
    # Calculate achievement percentages for all nutrients
    achievements = []
    
    for nutrient, avg_consumed in summary['avg_nutrients'].items():
        goal = daily_goals.get(nutrient, nutrition_calc.daily_values.get(nutrient))
        if goal and goal > 0:
            percentage = (avg_consumed / goal) * 100
            achievements.append({
                'nutrient': nutrient,
                'avg_consumed': avg_consumed,
                'goal': goal,
                'percentage': percentage,
                'category': get_nutrient_category(nutrient, nutrition_calc)
            })
    
    # Sort by percentage
    achievements.sort(key=lambda x: x['percentage'])
    
    # Show nutrients needing attention (< 75% of goal)
    low_nutrients = [a for a in achievements if a['percentage'] < 75]
    good_nutrients = [a for a in achievements if 75 <= a['percentage'] <= 125]
    high_nutrients = [a for a in achievements if a['percentage'] > 125]
    
    # Mobile-friendly layout for goal analysis
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚠️ Nutrients Below Target")
        if low_nutrients:
            for nutrient in low_nutrients[:10]:  # Show top 10
                display_name = nutrition_calc.get_nutrient_display_name(nutrient['nutrient'])
                unit = nutrition_calc.get_nutrient_unit(nutrient['nutrient'])
                
                st.write(f"**{display_name}**: {nutrient['percentage']:.0f}% of goal")
                st.caption(f"{nutrient['avg_consumed']:.1f}{unit} / {nutrient['goal']:.1f}{unit}")
        else:
            st.success("All tracked nutrients are meeting targets! 🎉")
    
    with col2:
        st.subheader("✅ Nutrients On Target")
        if good_nutrients:
            for nutrient in good_nutrients[:10]:  # Show top 10
                display_name = nutrition_calc.get_nutrient_display_name(nutrient['nutrient'])
                unit = nutrition_calc.get_nutrient_unit(nutrient['nutrient'])
                
                st.write(f"**{display_name}**: {nutrient['percentage']:.0f}% of goal")
                st.caption(f"{nutrient['avg_consumed']:.1f}{unit} / {nutrient['goal']:.1f}{unit}")
        else:
            st.info("No nutrients in the target range.")
    
    # Achievement overview chart
    if achievements:
        st.subheader("📊 Overall Achievement Overview")
        
        # Create categories for the chart
        chart_data = []
        for achievement in achievements:
            chart_data.append({
                'Nutrient': nutrition_calc.get_nutrient_display_name(achievement['nutrient'])[:20],
                'Achievement %': achievement['percentage'],
                'Category': achievement['category']
            })
        
        df = pd.DataFrame(chart_data)
        
        # Create horizontal bar chart
        fig = px.bar(
            df, 
            x='Achievement %', 
            y='Nutrient',
            color='Category',
            title="Nutrient Goal Achievement (Last 7 Days Average)",
            orientation='h',
            height=500
        )
        
        # Add target line
        fig.add_vline(x=100, line_dash="dash", line_color="green", 
                     annotation_text="Goal (100%)")
        
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if low_nutrients:
        st.write("**To improve your nutrition:**")
        
        # Group recommendations by category
        recommendations = {
            'Vitamins': [],
            'Minerals': [],
            'Macronutrients': []
        }
        
        for nutrient in low_nutrients[:5]:  # Top 5 deficient nutrients
            category = nutrient['category']
            nutrient_name = nutrition_calc.get_nutrient_display_name(nutrient['nutrient'])
            recommendations[category].append(nutrient_name)
        
        for category, nutrients in recommendations.items():
            if nutrients:
                st.write(f"**{category}:** Focus on foods rich in {', '.join(nutrients)}")
    
    else:
        st.success("Great job! You're meeting most of your nutritional goals. Keep up the excellent work! 🌟")

def get_nutrient_category(nutrient, nutrition_calc):
    """Get the category for a nutrient"""
    categories = nutrition_calc.get_nutrient_categories()
    
    for category, nutrients in categories.items():
        if nutrient in nutrients:
            return category
    
    return "Other"
