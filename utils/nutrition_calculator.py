import math
from typing import Dict, Tuple

class NutritionCalculator:
    def __init__(self):
        # Daily reference values for nutrients (adult recommendations)
        self.daily_values = {
            # Macronutrients (calculated based on calories)
            'calories': 2000,
            'protein': 50,  # grams
            'fat': 65,      # grams
            'carbohydrates': 300,  # grams
            'fiber': 25,    # grams
            'sugar': 50,    # grams
            
            # Vitamins
            'vitamin_a': 900,      # mcg RAE
            'vitamin_c': 90,       # mg
            'vitamin_d': 20,       # mcg
            'vitamin_e': 15,       # mg
            'vitamin_k': 120,      # mcg
            'vitamin_b1': 1.2,     # mg (thiamin)
            'vitamin_b2': 1.3,     # mg (riboflavin)
            'vitamin_b3': 16,      # mg (niacin)
            'vitamin_b5': 5,       # mg (pantothenic acid)
            'vitamin_b6': 1.3,     # mg
            'vitamin_b12': 2.4,    # mcg
            'folate': 400,         # mcg
            
            # Minerals
            'calcium': 1000,       # mg
            'iron': 8,             # mg
            'magnesium': 400,      # mg
            'phosphorus': 700,     # mg
            'potassium': 3500,     # mg
            'sodium': 2300,        # mg (upper limit)
            'zinc': 11,            # mg
            'copper': 0.9,         # mg
            'manganese': 2.3,      # mg
            'selenium': 55,        # mcg
            
            # Other
            'cholesterol': 300,    # mg (upper limit)
            'saturated_fat': 20,   # grams
        }
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate BMI"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def calculate_bmr(self, weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        return bmr * multiplier
    
    def calculate_daily_goals(self, tdee: float, goal: str, gender: str, age: int) -> Dict[str, float]:
        """Calculate personalized daily nutrition goals"""
        # Adjust calories based on goal
        if goal == 'lose':
            calories = tdee - 500  # 500 calorie deficit
        elif goal == 'gain':
            calories = tdee + 500  # 500 calorie surplus
        else:
            calories = tdee
        
        # Calculate macronutrients based on calories
        protein_grams = (calories * 0.15) / 4  # 15% of calories from protein
        fat_grams = (calories * 0.30) / 9      # 30% of calories from fat
        carb_grams = (calories * 0.55) / 4     # 55% of calories from carbs
        
        goals = self.daily_values.copy()
        goals.update({
            'calories': calories,
            'protein': protein_grams,
            'fat': fat_grams,
            'carbohydrates': carb_grams,
        })
        
        # Adjust some nutrients based on gender and age
        if gender.lower() == 'female':
            goals['iron'] = 18 if age < 51 else 8
            goals['folate'] = 400
        
        if age > 70:
            goals['vitamin_d'] = 20
            goals['calcium'] = 1200
        
        return goals
    
    def calculate_nutrient_percentage(self, consumed: float, goal: float) -> float:
        """Calculate percentage of daily goal achieved"""
        if goal == 0:
            return 0
        return min((consumed / goal) * 100, 200)  # Cap at 200%
    
    def scale_nutrients_by_portion(self, nutrients: Dict[str, float], portion_grams: float, 
                                 reference_portion: float = 100) -> Dict[str, float]:
        """Scale nutrient values based on portion size"""
        scaling_factor = portion_grams / reference_portion
        return {nutrient: value * scaling_factor for nutrient, value in nutrients.items()}
    
    def get_nutrient_status(self, percentage: float) -> Tuple[str, str]:
        """Get status and color for nutrient percentage"""
        if percentage < 25:
            return "Very Low", "🔴"
        elif percentage < 50:
            return "Low", "🟠"
        elif percentage < 75:
            return "Moderate", "🟡"
        elif percentage < 100:
            return "Good", "🟢"
        elif percentage < 150:
            return "Excellent", "💚"
        else:
            return "High", "🔵"
    
    def calculate_meal_calories(self, nutrients: Dict[str, float]) -> float:
        """Calculate calories from macronutrients"""
        protein_cal = nutrients.get('protein', 0) * 4
        fat_cal = nutrients.get('fat', 0) * 9
        carb_cal = nutrients.get('carbohydrates', 0) * 4
        
        return protein_cal + fat_cal + carb_cal
    
    def get_nutrient_categories(self) -> Dict[str, list]:
        """Get nutrients organized by categories"""
        return {
            "Macronutrients": [
                'calories', 'protein', 'fat', 'carbohydrates', 'fiber', 'sugar'
            ],
            "Vitamins": [
                'vitamin_a', 'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k',
                'vitamin_b1', 'vitamin_b2', 'vitamin_b3', 'vitamin_b5', 
                'vitamin_b6', 'vitamin_b12', 'folate'
            ],
            "Minerals": [
                'calcium', 'iron', 'magnesium', 'phosphorus', 'potassium', 
                'sodium', 'zinc', 'copper', 'manganese', 'selenium'
            ],
            "Other": [
                'cholesterol', 'saturated_fat'
            ]
        }
    
    def get_nutrient_display_name(self, nutrient: str) -> str:
        """Get display-friendly nutrient names"""
        display_names = {
            'vitamin_a': 'Vitamin A',
            'vitamin_c': 'Vitamin C', 
            'vitamin_d': 'Vitamin D',
            'vitamin_e': 'Vitamin E',
            'vitamin_k': 'Vitamin K',
            'vitamin_b1': 'Thiamin (B1)',
            'vitamin_b2': 'Riboflavin (B2)',
            'vitamin_b3': 'Niacin (B3)',
            'vitamin_b5': 'Pantothenic Acid (B5)',
            'vitamin_b6': 'Vitamin B6',
            'vitamin_b12': 'Vitamin B12',
            'saturated_fat': 'Saturated Fat'
        }
        
        return display_names.get(nutrient, nutrient.replace('_', ' ').title())
    
    def get_nutrient_unit(self, nutrient: str) -> str:
        """Get the unit for each nutrient"""
        units = {
            'calories': 'kcal',
            'protein': 'g',
            'fat': 'g', 
            'carbohydrates': 'g',
            'fiber': 'g',
            'sugar': 'g',
            'vitamin_a': 'mcg',
            'vitamin_c': 'mg',
            'vitamin_d': 'mcg',
            'vitamin_e': 'mg',
            'vitamin_k': 'mcg',
            'vitamin_b1': 'mg',
            'vitamin_b2': 'mg',
            'vitamin_b3': 'mg',
            'vitamin_b5': 'mg',
            'vitamin_b6': 'mg',
            'vitamin_b12': 'mcg',
            'folate': 'mcg',
            'calcium': 'mg',
            'iron': 'mg',
            'magnesium': 'mg',
            'phosphorus': 'mg',
            'potassium': 'mg',
            'sodium': 'mg',
            'zinc': 'mg',
            'copper': 'mg',
            'manganese': 'mg',
            'selenium': 'mcg',
            'cholesterol': 'mg',
            'saturated_fat': 'g'
        }
        
        return units.get(nutrient, '')
