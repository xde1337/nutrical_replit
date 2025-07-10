import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, List, Optional
import json

class DataStorage:
    def __init__(self):
        self.init_session_storage()
    
    def init_session_storage(self):
        """Initialize session storage for all data"""
        if 'daily_entries' not in st.session_state:
            st.session_state.daily_entries = {}
        
        if 'food_database' not in st.session_state:
            st.session_state.food_database = {}
        
        if 'measurements_history' not in st.session_state:
            st.session_state.measurements_history = []
    
    def add_food_entry(self, date_str: str, food_data: Dict):
        """Add a food entry for a specific date"""
        if date_str not in st.session_state.daily_entries:
            st.session_state.daily_entries[date_str] = []
        
        # Add timestamp and unique ID
        food_data['timestamp'] = datetime.now().isoformat()
        food_data['entry_id'] = len(st.session_state.daily_entries[date_str])
        
        st.session_state.daily_entries[date_str].append(food_data)
    
    def get_daily_entries(self, date_str: str) -> List[Dict]:
        """Get all food entries for a specific date"""
        return st.session_state.daily_entries.get(date_str, [])
    
    def remove_food_entry(self, date_str: str, entry_id: int):
        """Remove a food entry"""
        if date_str in st.session_state.daily_entries:
            entries = st.session_state.daily_entries[date_str]
            st.session_state.daily_entries[date_str] = [
                entry for entry in entries if entry.get('entry_id') != entry_id
            ]
    
    def get_daily_totals(self, date_str: str) -> Dict[str, float]:
        """Calculate total nutrients for a specific date"""
        entries = self.get_daily_entries(date_str)
        totals = {}
        
        for entry in entries:
            nutrients = entry.get('nutrients', {})
            for nutrient, amount in nutrients.items():
                totals[nutrient] = totals.get(nutrient, 0) + amount
        
        return totals
    
    def cache_food_data(self, fdc_id: int, food_data: Dict):
        """Cache food data to reduce API calls"""
        st.session_state.food_database[str(fdc_id)] = food_data
    
    def get_cached_food_data(self, fdc_id: int) -> Optional[Dict]:
        """Get cached food data"""
        return st.session_state.food_database.get(str(fdc_id))
    
    def add_measurement(self, measurement_data: Dict):
        """Add a body measurement entry"""
        measurement_data['date'] = measurement_data.get('date', date.today().isoformat())
        measurement_data['timestamp'] = datetime.now().isoformat()
        
        st.session_state.measurements_history.append(measurement_data)
        
        # Keep only the latest 100 measurements
        if len(st.session_state.measurements_history) > 100:
            st.session_state.measurements_history = st.session_state.measurements_history[-100:]
    
    def get_measurements_history(self) -> List[Dict]:
        """Get measurement history"""
        return st.session_state.measurements_history
    
    def get_latest_measurement(self) -> Optional[Dict]:
        """Get the most recent measurement"""
        if st.session_state.measurements_history:
            return st.session_state.measurements_history[-1]
        return None
    
    def get_dates_with_entries(self) -> List[str]:
        """Get all dates that have food entries"""
        return list(st.session_state.daily_entries.keys())
    
    def export_data(self) -> Dict:
        """Export all data for backup"""
        return {
            'daily_entries': st.session_state.daily_entries,
            'measurements_history': st.session_state.measurements_history,
            'user_profile': st.session_state.get('user_profile', {}),
            'export_date': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict):
        """Import data from backup"""
        if 'daily_entries' in data:
            st.session_state.daily_entries.update(data['daily_entries'])
        
        if 'measurements_history' in data:
            st.session_state.measurements_history.extend(data['measurements_history'])
        
        if 'user_profile' in data:
            st.session_state.user_profile.update(data['user_profile'])
    
    def clear_all_data(self):
        """Clear all stored data"""
        st.session_state.daily_entries = {}
        st.session_state.food_database = {}
        st.session_state.measurements_history = []
    
    def get_nutrition_summary(self, days: int = 7) -> Dict:
        """Get nutrition summary for the last N days"""
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        summary = {
            'total_days': 0,
            'avg_nutrients': {},
            'dates_tracked': []
        }
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            daily_totals = self.get_daily_totals(date_str)
            
            if daily_totals:
                summary['total_days'] += 1
                summary['dates_tracked'].append(date_str)
                
                for nutrient, amount in daily_totals.items():
                    if nutrient not in summary['avg_nutrients']:
                        summary['avg_nutrients'][nutrient] = []
                    summary['avg_nutrients'][nutrient].append(amount)
            
            current_date += timedelta(days=1)
        
        # Calculate averages
        for nutrient, values in summary['avg_nutrients'].items():
            summary['avg_nutrients'][nutrient] = sum(values) / len(values)
        
        return summary
