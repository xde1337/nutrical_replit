import requests
import os
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional

class USDAFoodAPI:
    def __init__(self):
        self.api_key = os.getenv("USDA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        
    def search_foods(self, query: str, page_size: int = 20) -> List[Dict]:
        """Search for foods in the USDA database"""
        if not query or len(query.strip()) < 2:
            return []
            
        url = f"{self.base_url}/foods/search"
        params = {
            "query": query.strip(),
            "pageSize": page_size,
            "api_key": self.api_key,
            "dataType": ["Foundation", "SR Legacy"]
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            # Format the response for easier use
            formatted_foods = []
            for food in foods:
                formatted_food = {
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description", "Unknown"),
                    "brand_owner": food.get("brandOwner", ""),
                    "data_type": food.get("dataType", ""),
                    "serving_size": food.get("servingSize", 100),
                    "serving_size_unit": food.get("servingSizeUnit", "g")
                }
                formatted_foods.append(formatted_food)
                
            return formatted_foods
            
        except requests.RequestException as e:
            st.error(f"Error searching foods: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return []
    
    def get_food_details(self, fdc_id: int) -> Optional[Dict]:
        """Get detailed nutrition information for a specific food"""
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            food_data = response.json()
            
            # Extract nutrients
            nutrients = {}
            for nutrient in food_data.get("foodNutrients", []):
                nutrient_info = nutrient.get("nutrient", {})
                nutrient_name = nutrient_info.get("name", "")
                nutrient_unit = nutrient_info.get("unitName", "")
                amount = nutrient.get("amount", 0)
                
                if nutrient_name and amount is not None:
                    nutrients[nutrient_name] = {
                        "amount": amount,
                        "unit": nutrient_unit
                    }
            
            return {
                "fdc_id": food_data.get("fdcId"),
                "description": food_data.get("description", ""),
                "nutrients": nutrients,
                "serving_size": food_data.get("servingSize", 100),
                "serving_size_unit": food_data.get("servingSizeUnit", "g")
            }
            
        except requests.RequestException as e:
            st.error(f"Error fetching food details: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_nutrient_mapping(self) -> Dict[str, str]:
        """Return a mapping of USDA nutrient names to standardized names"""
        return {
            "Energy": "calories",
            "Protein": "protein",
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbohydrates",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugar",
            "Sodium, Na": "sodium",
            "Calcium, Ca": "calcium",
            "Iron, Fe": "iron",
            "Magnesium, Mg": "magnesium",
            "Phosphorus, P": "phosphorus",
            "Potassium, K": "potassium",
            "Zinc, Zn": "zinc",
            "Copper, Cu": "copper",
            "Manganese, Mn": "manganese",
            "Selenium, Se": "selenium",
            "Vitamin C, total ascorbic acid": "vitamin_c",
            "Thiamin": "vitamin_b1",
            "Riboflavin": "vitamin_b2",
            "Niacin": "vitamin_b3",
            "Pantothenic acid": "vitamin_b5",
            "Vitamin B-6": "vitamin_b6",
            "Folate, total": "folate",
            "Vitamin B-12": "vitamin_b12",
            "Vitamin A, RAE": "vitamin_a",
            "Vitamin E (alpha-tocopherol)": "vitamin_e",
            "Vitamin D (D2 + D3)": "vitamin_d",
            "Vitamin K (phylloquinone)": "vitamin_k",
            "Cholesterol": "cholesterol",
            "Fatty acids, total saturated": "saturated_fat",
            "Fatty acids, total monounsaturated": "monounsaturated_fat",
            "Fatty acids, total polyunsaturated": "polyunsaturated_fat"
        }
    
    def normalize_nutrients(self, nutrients: Dict) -> Dict:
        """Convert USDA nutrient names to standardized names"""
        mapping = self.get_nutrient_mapping()
        normalized = {}
        
        for usda_name, nutrient_data in nutrients.items():
            standard_name = mapping.get(usda_name)
            if standard_name:
                normalized[standard_name] = nutrient_data["amount"]
        
        return normalized
