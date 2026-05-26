"""
MongoDB Database Module for Coffee Leaf Disease Detection
Uses environment variables for secure configuration
"""

import os
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MongoDB:
    def __init__(self):
        # Get connection string from environment variable
        self.connection_string = os.environ.get('MONGODB_URI')
        
        if not self.connection_string:
            st.error("❌ MONGODB_URI not found in environment variables!")
            st.info("Please create a .env file with your MongoDB connection string")
            self.client = None
            self.db = None
            return
        
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client['coffee_disease_detection']
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def get_user(self, email):
        """Get user by email"""
        if self.db is None:
            return None
        return self.db.users.find_one({'email': email})
    
    def create_user(self, email, password, name=""):
        """Create new user"""
        if self.db is None:
            return False, "Database not connected"
        
        # Check if user exists
        if self.get_user(email):
            return False, "User already exists"
        
        # Hash password with bcrypt (more secure than SHA256)
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        user = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'created_at': datetime.now(),
            'language_preference': 'en',
            'total_predictions': 0,
            'is_active': True
        }
        
        result = self.db.users.insert_one(user)
        return True, "User created successfully"
    
    def verify_user(self, email, password):
        """Verify user credentials"""
        user = self.get_user(email)
        if not user:
            return False, "User not found"
        
        # Verify with bcrypt
        try:
            if bcrypt.checkpw(password.encode(), user['password'].encode()):
                return True, "Login successful"
            else:
                return False, "Incorrect password"
        except Exception as e:
            return False, f"Error verifying password: {e}"
    
    def save_prediction(self, user_email, prediction_data):
        """Save prediction to database"""
        if self.db is None:
            return None
        
        prediction = {
            'user_email': user_email,
            'image_name': prediction_data.get('image_name', 'unknown'),
            'image_url': prediction_data.get('image_url', ''),
            'predicted_disease': prediction_data.get('predicted_disease'),
            'confidence': prediction_data.get('confidence'),
            'all_probabilities': prediction_data.get('all_probabilities', {}),
            'crop_used': prediction_data.get('crop_used', False),
            'created_at': datetime.now(),
            'model_version': 'MobileNetV2_v1'
        }
        
        result = self.db.predictions.insert_one(prediction)
        
        # Update user's total predictions count
        self.db.users.update_one(
            {'email': user_email},
            {'$inc': {'total_predictions': 1}}
        )
        
        return result.inserted_id
    
    def get_user_predictions(self, user_email, limit=50):
        """Get prediction history for user"""
        if self.db is None:
            return []
        
        predictions = self.db.predictions.find(
            {'user_email': user_email}
        ).sort('created_at', -1).limit(limit)
        
        return list(predictions)
    
    def get_statistics(self, user_email=None):
        """Get statistics for dashboard"""
        if self.db is None:
            return {}
        
        stats = {}
        
        # Total predictions
        if user_email:
            stats['total_predictions'] = self.db.predictions.count_documents({'user_email': user_email})
        else:
            stats['total_predictions'] = self.db.predictions.count_documents({})
            stats['total_users'] = self.db.users.count_documents({})
        
        # Disease distribution
        pipeline = [
            {'$group': {'_id': '$predicted_disease', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        if user_email:
            pipeline.insert(0, {'$match': {'user_email': user_email}})
        
        stats['disease_distribution'] = list(self.db.predictions.aggregate(pipeline))
        
        # Average confidence
        pipeline = [
            {'$group': {'_id': None, 'avg_confidence': {'$avg': '$confidence'}}}
        ]
        if user_email:
            pipeline.insert(0, {'$match': {'user_email': user_email}})
        
        result = list(self.db.predictions.aggregate(pipeline))
        stats['avg_confidence'] = result[0]['avg_confidence'] if result else 0
        
        return stats

# Create global instance
try:
    db = MongoDB()
except Exception as e:
    print(f"Failed to initialize database: {e}")
    db = None

def init_database():
    """Initialize database with indexes"""
    if db and db.db is not None:
        try:
            # Create indexes for better performance
            db.db.users.create_index('email', unique=True)
            db.db.predictions.create_index('user_email')
            db.db.predictions.create_index('created_at')
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")