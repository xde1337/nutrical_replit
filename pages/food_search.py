import streamlit as st
from utils.usda_api import USDAFoodAPI

def show_food_search():
    st.header("🔍 Add Food to Diary")
    
    # Initialize USDA API
    if 'usda_api' not in st.session_state:
        st.session_state.usda_api = USDAFoodAPI()
    
    usda_api = st.session_state.usda_api
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    
    # Date selection for logging
    date_str = st.session_state.current_date.isoformat()
    st.write(f"Adding food for: **{st.session_state.current_date.strftime('%B %d, %Y')}**")
    
    # Search interface
    st.subheader("Search Foods")
    
    search_query = st.text_input(
        "Search for food",
        placeholder="e.g., 'chicken breast', 'apple', 'brown rice'",
        help="Enter a food name to search the USDA database"
    )
    
    if search_query and len(search_query.strip()) >= 2:
        with st.spinner("Searching USDA database..."):
            search_results = usda_api.search_foods(search_query.strip())
        
        if search_results:
            st.subheader(f"Search Results ({len(search_results)} found)")
            
            for i, food in enumerate(search_results):
                # Shorter descriptions for mobile
                desc = food['description']
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                
                with st.expander(f"{desc}"):
                    # Mobile-friendly single column layout
                    st.write(f"**Food:** {food['description']}")
                    if food['brand_owner']:
                        st.write(f"**Brand:** {food['brand_owner']}")
                    st.write(f"**Type:** {food['data_type']}")
                    st.write(f"**Serving:** {food['serving_size']} {food['serving_size_unit']}")
                    
                    # Full-width select button for mobile
                    if st.button(f"✅ Select This Food", key=f"select_{food['fdc_id']}", use_container_width=True):
                        st.session_state.selected_food = food
                        st.rerun()
        else:
            st.warning("No foods found. Try a different search term.")
    elif search_query and len(search_query.strip()) < 2:
        st.info("Please enter at least 2 characters to search.")
    
    # Food details and portion selection
    if 'selected_food' in st.session_state and st.session_state.selected_food:
        show_food_details()

def show_food_details():
    usda_api = st.session_state.usda_api
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    
    selected_food = st.session_state.selected_food
    
    st.divider()
    st.subheader("📋 Food Details & Portion")
    
    # Check if we have cached data
    cached_data = data_storage.get_cached_food_data(selected_food['fdc_id'])
    
    if cached_data:
        food_details = cached_data
    else:
        with st.spinner("Loading detailed nutrition information..."):
            food_details = usda_api.get_food_details(selected_food['fdc_id'])
        
        if food_details:
            # Cache the data
            data_storage.cache_food_data(selected_food['fdc_id'], food_details)
        else:
            st.error("Could not load detailed nutrition information. Please try another food.")
            return
    
    # Display food info
    st.write(f"**Selected Food:** {food_details['description']}")
    
    # Mobile-friendly portion input
    portion_size = st.number_input(
        "Portion Size (grams)",
        min_value=1.0,
        max_value=2000.0,
        value=float(food_details.get('serving_size', 100)),
        step=1.0,
        help="Enter the amount you consumed in grams"
    )
    
    meal_type = st.selectbox(
        "Meal Type",
        ["Breakfast", "Lunch", "Dinner", "Snack"],
        help="Categorize this food entry"
    )
    
    # Full-width add button for mobile
    if st.button("🍽️ Add to Diary", type="primary", use_container_width=True):
        add_food_to_diary(food_details, portion_size, meal_type)
    
    # Show nutrition preview
    if food_details.get('nutrients'):
        show_nutrition_preview(food_details, portion_size)

def show_nutrition_preview(food_details, portion_size):
    nutrition_calc = st.session_state.nutrition_calculator
    
    st.subheader("🥗 Nutrition Preview")
    
    # Get normalized nutrients
    normalized_nutrients = st.session_state.usda_api.normalize_nutrients(food_details['nutrients'])
    
    # Scale nutrients based on portion size
    reference_portion = food_details.get('serving_size', 100)
    scaled_nutrients = nutrition_calc.scale_nutrients_by_portion(
        normalized_nutrients, portion_size, reference_portion
    )
    
    # Mobile-responsive nutrient display: 2x2 grid
    col1, col2 = st.columns(2)
    
    with col1:
        calories = scaled_nutrients.get('calories', 0)
        st.metric("Calories", f"{calories:.1f}")
        
        carbs = scaled_nutrients.get('carbohydrates', 0)
        st.metric("Carbs", f"{carbs:.1f}g")
    
    with col2:
        protein = scaled_nutrients.get('protein', 0)
        st.metric("Protein", f"{protein:.1f}g")
        
        fat = scaled_nutrients.get('fat', 0)
        st.metric("Fat", f"{fat:.1f}g")
    
    # Show detailed nutrients in expandable sections
    nutrient_categories = nutrition_calc.get_nutrient_categories()
    
    for category, nutrients in nutrient_categories.items():
        if category == "Macronutrients":  # Already shown above
            continue
            
        category_nutrients = {n: scaled_nutrients.get(n, 0) for n in nutrients if n in scaled_nutrients and scaled_nutrients[n] > 0}
        
        if category_nutrients:
            with st.expander(f"{category} ({len(category_nutrients)} nutrients)"):
                # Mobile-friendly 2-column layout for nutrients
                cols = st.columns(2)
                for i, (nutrient, amount) in enumerate(category_nutrients.items()):
                    with cols[i % 2]:
                        display_name = nutrition_calc.get_nutrient_display_name(nutrient)
                        unit = nutrition_calc.get_nutrient_unit(nutrient)
                        st.write(f"**{display_name}:** {amount:.1f}{unit}")

def add_food_to_diary(food_details, portion_size, meal_type):
    data_storage = st.session_state.data_storage
    nutrition_calc = st.session_state.nutrition_calculator
    
    # Get normalized and scaled nutrients
    normalized_nutrients = st.session_state.usda_api.normalize_nutrients(food_details['nutrients'])
    reference_portion = food_details.get('serving_size', 100)
    scaled_nutrients = nutrition_calc.scale_nutrients_by_portion(
        normalized_nutrients, portion_size, reference_portion
    )
    
    # Create food entry
    food_entry = {
        'fdc_id': food_details['fdc_id'],
        'food_name': food_details['description'],
        'portion_size': portion_size,
        'meal_type': meal_type,
        'nutrients': scaled_nutrients,
        'original_serving_size': reference_portion
    }
    
    # Add to diary
    date_str = st.session_state.current_date.isoformat()
    data_storage.add_food_entry(date_str, food_entry)
    
    # Clear selected food
    if 'selected_food' in st.session_state:
        del st.session_state.selected_food
    
    st.success(f"✅ Added {food_details['description']} ({portion_size}g) to your diary!")
    st.rerun()
