import os
import sqlalchemy as db
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from typing import Optional, Dict, Any

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    profile_picture = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # User profile data
    age = Column(Integer)
    gender = Column(String(10))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    activity_level = Column(String(20))
    goal = Column(String(20))

class FoodEntry(Base):
    __tablename__ = 'food_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    meal_type = Column(String(20), nullable=False)
    food_name = Column(String(255), nullable=False)
    fdc_id = Column(Integer)
    portion_size = Column(Float, nullable=False)
    portion_unit = Column(String(50), nullable=False)
    nutrients = Column(Text)  # JSON string of nutrients
    created_at = Column(DateTime, default=datetime.utcnow)

class Measurement(Base):
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    weight_kg = Column(Float)
    body_fat_percent = Column(Float)
    muscle_mass_kg = Column(Float)
    waist_cm = Column(Float)
    chest_cm = Column(Float)
    arms_cm = Column(Float)
    thighs_cm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Use SQLite for local development/demo
            database_url = 'sqlite:///nutrition_tracker.db'
            print("⚠️  DATABASE_URL not set, using SQLite for demo purposes")
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def create_or_update_user(self, google_id: str, email: str, name: str, profile_picture: str = None) -> User:
        """Create a new user or update existing user's login time"""
        user = self.session.query(User).filter_by(google_id=google_id).first()
        
        if user:
            # Update existing user
            user.last_login = datetime.utcnow()
            user.email = email  # Update in case email changed
            user.name = name    # Update in case name changed
            if profile_picture:
                user.profile_picture = profile_picture
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                profile_picture=profile_picture,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            self.session.add(user)
        
        self.session.commit()
        return user
    
    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return self.session.query(User).filter_by(google_id=google_id).first()
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        user = self.session.query(User).filter_by(id=user_id).first()
        if not user:
            return False
        
        for key, value in profile_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.session.commit()
        return True
    
    def add_food_entry(self, user_id: int, date: str, meal_type: str, food_name: str, 
                      fdc_id: int, portion_size: float, portion_unit: str, nutrients: Dict) -> bool:
        """Add a food entry for a user"""
        entry = FoodEntry(
            user_id=user_id,
            date=date,
            meal_type=meal_type,
            food_name=food_name,
            fdc_id=fdc_id,
            portion_size=portion_size,
            portion_unit=portion_unit,
            nutrients=json.dumps(nutrients)
        )
        
        self.session.add(entry)
        self.session.commit()
        return True
    
    def get_food_entries(self, user_id: int, date: str = None) -> list:
        """Get food entries for a user on a specific date or all dates"""
        query = self.session.query(FoodEntry).filter_by(user_id=user_id)
        
        if date:
            query = query.filter_by(date=date)
        
        entries = query.all()
        
        # Convert to dictionary format
        result = []
        for entry in entries:
            result.append({
                'id': entry.id,
                'date': entry.date,
                'meal_type': entry.meal_type,
                'food_name': entry.food_name,
                'fdc_id': entry.fdc_id,
                'portion_size': entry.portion_size,
                'portion_unit': entry.portion_unit,
                'nutrients': json.loads(entry.nutrients) if entry.nutrients else {},
                'created_at': entry.created_at
            })
        
        return result
    
    def remove_food_entry(self, user_id: int, entry_id: int) -> bool:
        """Remove a food entry"""
        entry = self.session.query(FoodEntry).filter_by(id=entry_id, user_id=user_id).first()
        if entry:
            self.session.delete(entry)
            self.session.commit()
            return True
        return False
    
    def add_measurement(self, user_id: int, date: str, measurement_data: Dict) -> bool:
        """Add a body measurement for a user"""
        measurement = Measurement(
            user_id=user_id,
            date=date,
            **measurement_data
        )
        
        self.session.add(measurement)
        self.session.commit()
        return True
    
    def get_measurements(self, user_id: int) -> list:
        """Get all measurements for a user"""
        measurements = self.session.query(Measurement).filter_by(user_id=user_id).order_by(Measurement.date.desc()).all()
        
        result = []
        for measurement in measurements:
            result.append({
                'id': measurement.id,
                'date': measurement.date,
                'weight_kg': measurement.weight_kg,
                'body_fat_percent': measurement.body_fat_percent,
                'muscle_mass_kg': measurement.muscle_mass_kg,
                'waist_cm': measurement.waist_cm,
                'chest_cm': measurement.chest_cm,
                'arms_cm': measurement.arms_cm,
                'thighs_cm': measurement.thighs_cm,
                'created_at': measurement.created_at
            })
        
        return result
    
    def get_dates_with_entries(self, user_id: int) -> list:
        """Get all dates that have food entries for a user"""
        dates = self.session.query(FoodEntry.date).filter_by(user_id=user_id).distinct().all()
        return [date[0] for date in dates]
    
    def close(self):
        """Close database session"""
        self.session.close()