from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from .database import DatabaseManager

class DatabaseDataStorage:
    """Database-backed data storage for authenticated users"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db = DatabaseManager()
    
    def add_food_entry(self, date_str: str, food_data: Dict):
        """Add a food entry for a specific date"""
        return self.db.add_food_entry(
            user_id=self.user_id,
            date=date_str,
            meal_type=food_data.get('meal_type', 'meal'),
            food_name=food_data.get('food_name', ''),
            fdc_id=food_data.get('fdc_id', 0),
            portion_size=food_data.get('portion_size', 0),
            portion_unit=food_data.get('portion_unit', 'g'),
            nutrients=food_data.get('nutrients', {})
        )
    
    def get_daily_entries(self, date_str: str) -> List[Dict]:
        """Get all food entries for a specific date"""
        entries = self.db.get_food_entries(user_id=self.user_id, date=date_str)
        
        # Convert to the format expected by the app
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                'id': entry['id'],
                'meal_type': entry['meal_type'],
                'food_name': entry['food_name'],
                'fdc_id': entry['fdc_id'],
                'portion_size': entry['portion_size'],
                'portion_unit': entry['portion_unit'],
                'nutrients': entry['nutrients']
            })
        
        return formatted_entries
    
    def remove_food_entry(self, date_str: str, entry_id: int):
        """Remove a food entry"""
        return self.db.remove_food_entry(user_id=self.user_id, entry_id=entry_id)
    
    def get_daily_totals(self, date_str: str) -> Dict[str, float]:
        """Calculate total nutrients for a specific date"""
        entries = self.get_daily_entries(date_str)
        
        totals = {}
        for entry in entries:
            nutrients = entry.get('nutrients', {})
            for nutrient, value in nutrients.items():
                if isinstance(value, (int, float)):
                    totals[nutrient] = totals.get(nutrient, 0) + value
        
        return totals
    
    def cache_food_data(self, fdc_id: int, food_data: Dict):
        """Cache food data - not implemented for database storage"""
        # Could implement a food cache table if needed
        pass
    
    def get_cached_food_data(self, fdc_id: int) -> Optional[Dict]:
        """Get cached food data - not implemented for database storage"""
        # Could implement a food cache table if needed
        return None
    
    def add_measurement(self, measurement_data: Dict):
        """Add a body measurement entry"""
        date_str = measurement_data.pop('date', datetime.now().strftime('%Y-%m-%d'))
        return self.db.add_measurement(
            user_id=self.user_id,
            date=date_str,
            measurement_data=measurement_data
        )
    
    def get_measurements_history(self) -> List[Dict]:
        """Get measurement history"""
        measurements = self.db.get_measurements(user_id=self.user_id)
        
        # Convert to the format expected by the app
        formatted_measurements = []
        for measurement in measurements:
            formatted_measurements.append({
                'date': measurement['date'],
                'weight_kg': measurement['weight_kg'],
                'body_fat_percent': measurement['body_fat_percent'],
                'muscle_mass_kg': measurement['muscle_mass_kg'],
                'waist_cm': measurement['waist_cm'],
                'chest_cm': measurement['chest_cm'],
                'arms_cm': measurement['arms_cm'],
                'thighs_cm': measurement['thighs_cm']
            })
        
        return formatted_measurements
    
    def get_latest_measurement(self) -> Optional[Dict]:
        """Get the most recent measurement"""
        measurements = self.get_measurements_history()
        return measurements[0] if measurements else None
    
    def get_dates_with_entries(self) -> List[str]:
        """Get all dates that have food entries"""
        return self.db.get_dates_with_entries(user_id=self.user_id)
    
    def export_data(self) -> Dict:
        """Export all data for backup"""
        # Get all food entries
        all_entries = self.db.get_food_entries(user_id=self.user_id)
        
        # Get all measurements
        all_measurements = self.get_measurements_history()
        
        return {
            'food_entries': all_entries,
            'measurements': all_measurements,
            'export_date': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict):
        """Import data from backup - not implemented for database storage"""
        # Could implement bulk import functionality
        pass
    
    def clear_all_data(self):
        """Clear all stored data - not implemented for safety"""
        # Could implement with proper confirmation
        pass
    
    def get_nutrition_summary(self, days: int = 7) -> Dict:
        """Get nutrition summary for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        summary = {
            'total_days': days,
            'days_with_entries': 0,
            'avg_calories': 0,
            'avg_protein': 0,
            'avg_carbohydrates': 0,
            'avg_fat': 0,
            'nutrients': {}
        }
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        days_with_data = 0
        
        # Get data for each day in the range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_totals = self.get_daily_totals(date_str)
            
            if daily_totals:
                days_with_data += 1
                total_calories += daily_totals.get('calories', 0)
                total_protein += daily_totals.get('protein', 0)
                total_carbs += daily_totals.get('carbohydrates', 0)
                total_fat += daily_totals.get('fat', 0)
                
                # Accumulate other nutrients
                for nutrient, value in daily_totals.items():
                    if nutrient not in ['calories', 'protein', 'carbohydrates', 'fat']:
                        if nutrient not in summary['nutrients']:
                            summary['nutrients'][nutrient] = 0
                        summary['nutrients'][nutrient] += value
            
            current_date += timedelta(days=1)
        
        # Calculate averages
        if days_with_data > 0:
            summary['days_with_entries'] = days_with_data
            summary['avg_calories'] = total_calories / days_with_data
            summary['avg_protein'] = total_protein / days_with_data
            summary['avg_carbohydrates'] = total_carbs / days_with_data
            summary['avg_fat'] = total_fat / days_with_data
            
            # Average other nutrients
            for nutrient in summary['nutrients']:
                summary['nutrients'][nutrient] /= days_with_data
        
        return summary