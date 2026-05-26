"""
Database Manager for Coffee Leaf Disease Detection
Handles both JSON file storage and MongoDB (optional)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import bcrypt

from database.models import User, Prediction, Feedback

class DatabaseManager:
    """Manages database operations (JSON file-based)"""
    
    def __init__(self, db_path: str = "database"):
        self.db_path = db_path
        self.users_file = os.path.join(db_path, "users.json")
        self.predictions_file = os.path.join(db_path, "predictions.json")
        self.feedback_file = os.path.join(db_path, "feedback.json")
        
        # Initialize database files
        self._init_db()
    
    def _init_db(self):
        """Initialize database files if they don't exist"""
        os.makedirs(self.db_path, exist_ok=True)
        
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, [])
        
        if not os.path.exists(self.predictions_file):
            self._save_json(self.predictions_file, [])
        
        if not os.path.exists(self.feedback_file):
            self._save_json(self.feedback_file, [])
    
    def _load_json(self, file_path: str) -> list:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_json(self, file_path: str, data: list):
        """Save JSON data to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    # ============================================================
    # USER OPERATIONS
    # ============================================================
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email"""
        users = self._load_json(self.users_file)
        for user_data in users:
            if user_data.get('email') == email:
                return User.from_dict(user_data)
        return None
    
    def create_user(self, email: str, password: str, name: str = "") -> tuple:
        """Create a new user"""
        # Check if user exists
        if self.get_user(email):
            return False, "User already exists"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Create user
        user = User(email, hashed_password, name)
        
        # Save to file
        users = self._load_json(self.users_file)
        users.append(user.to_dict())
        self._save_json(self.users_file, users)
        
        return True, "User created successfully"
    
    def verify_user(self, email: str, password: str) -> tuple:
        """Verify user credentials"""
        user = self.get_user(email)
        if not user:
            return False, "User not found"
        
        try:
            if bcrypt.checkpw(password.encode(), user.password.encode()):
                return True, "Login successful"
            else:
                return False, "Incorrect password"
        except Exception:
            return False, "Error verifying password"
    
    def update_user(self, email: str, **kwargs) -> tuple:
        """Update user information"""
        users = self._load_json(self.users_file)
        
        for i, user_data in enumerate(users):
            if user_data.get('email') == email:
                for key, value in kwargs.items():
                    if key in user_data:
                        user_data[key] = value
                self._save_json(self.users_file, users)
                return True, "User updated successfully"
        
        return False, "User not found"
    
    def delete_user(self, email: str, password: str) -> tuple:
        """Delete user and all associated data"""
        # Verify password
        success, message = self.verify_user(email, password)
        if not success:
            return False, message
        
        # Delete user
        users = self._load_json(self.users_file)
        users = [u for u in users if u.get('email') != email]
        self._save_json(self.users_file, users)
        
        # Delete user's predictions
        predictions = self._load_json(self.predictions_file)
        predictions = [p for p in predictions if p.get('user_email') != email]
        self._save_json(self.predictions_file, predictions)
        
        # Delete user's feedback
        feedback = self._load_json(self.feedback_file)
        feedback = [f for f in feedback if f.get('user_email') != email]
        self._save_json(self.feedback_file, feedback)
        
        return True, "Account deleted successfully"
    
    # ============================================================
    # PREDICTION OPERATIONS
    # ============================================================
    
    def save_prediction(self, user_email: str, prediction_data: dict) -> Optional[str]:
        """Save a prediction"""
        prediction = Prediction(
            user_email=user_email,
            predicted_disease=prediction_data.get('predicted_disease'),
            confidence=prediction_data.get('confidence'),
            image_name=prediction_data.get('image_name', ''),
            image_url=prediction_data.get('image_url', ''),
            all_probabilities=prediction_data.get('all_probabilities', {}),
            crop_used=prediction_data.get('crop_used', False)
        )
        
        # Save to file
        predictions = self._load_json(self.predictions_file)
        prediction_dict = prediction.to_dict()
        predictions.append(prediction_dict)
        self._save_json(self.predictions_file, predictions)
        
        # Update user's prediction count
        users = self._load_json(self.users_file)
        for user_data in users:
            if user_data.get('email') == user_email:
                user_data['total_predictions'] = user_data.get('total_predictions', 0) + 1
                break
        self._save_json(self.users_file, users)
        
        return str(len(predictions) - 1)  # Return index as ID
    
    def get_user_predictions(self, user_email: str, limit: int = 50) -> List[Dict]:
        """Get user's prediction history"""
        predictions = self._load_json(self.predictions_file)
        user_predictions = [p for p in predictions if p.get('user_email') == user_email]
        # Sort by created_at descending
        user_predictions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return user_predictions[:limit]
    
    def get_all_predictions(self, limit: int = 100) -> List[Dict]:
        """Get all predictions (admin use)"""
        predictions = self._load_json(self.predictions_file)
        predictions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return predictions[:limit]
    
    # ============================================================
    # STATISTICS
    # ============================================================
    
    def get_statistics(self, user_email: str = None) -> Dict:
        """Get statistics for user or overall"""
        stats = {}
        
        if user_email:
            # User-specific stats
            predictions = self.get_user_predictions(user_email, limit=1000)
            stats['total_predictions'] = len(predictions)
            
            if predictions:
                # Average confidence
                confidences = [p.get('confidence', 0) for p in predictions]
                stats['avg_confidence'] = sum(confidences) / len(confidences) * 100
                
                # Disease distribution
                disease_counts = {}
                for p in predictions:
                    disease = p.get('predicted_disease', 'Unknown')
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1
                stats['disease_distribution'] = disease_counts
            else:
                stats['avg_confidence'] = 0
                stats['disease_distribution'] = {}
        else:
            # Overall stats
            predictions = self._load_json(self.predictions_file)
            users = self._load_json(self.users_file)
            
            stats['total_predictions'] = len(predictions)
            stats['total_users'] = len(users)
            
            if predictions:
                confidences = [p.get('confidence', 0) for p in predictions]
                stats['avg_confidence'] = sum(confidences) / len(confidences) * 100
            else:
                stats['avg_confidence'] = 0
        
        return stats
    
    # ============================================================
    # FEEDBACK OPERATIONS
    # ============================================================

    # ============================================================
# FEEDBACK OPERATIONS
# ============================================================

def save_feedback(self, feedback_data: dict) -> bool:
    """Save user feedback"""
    try:
        # Ensure feedback file exists
        if not hasattr(self, 'feedback_file'):
            self.feedback_file = os.path.join(self.db_path, "feedback.json")
        
        feedback_list = self._load_json(self.feedback_file)
        
        # Add ID if not present
        if 'id' not in feedback_data:
            feedback_data['id'] = len(feedback_list) + 1
        
        feedback_list.append(feedback_data)
        self._save_json(self.feedback_file, feedback_list)
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_feedback(self, user_email: str = None) -> list:
    """Get feedback, optionally filtered by user"""
    try:
        if not hasattr(self, 'feedback_file'):
            self.feedback_file = os.path.join(self.db_path, "feedback.json")
        
        feedback_list = self._load_json(self.feedback_file)
        
        if user_email:
            return [f for f in feedback_list if f.get('user_email') == user_email]
        return feedback_list
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return []

def get_all_feedback(self) -> list:
    """Get all feedback (admin use)"""
    return self.get_feedback()
    
    def save_feedback(self, feedback_data: dict) -> bool:
        """Save user feedback"""
        feedback = Feedback(
            prediction_id=feedback_data.get('prediction_id'),
            user_email=feedback_data.get('user_email'),
            was_correct=feedback_data.get('was_correct'),
            actual_disease=feedback_data.get('actual_disease'),
            comment=feedback_data.get('comment')
        )
        
        feedback_list = self._load_json(self.feedback_file)
        feedback_list.append(feedback.to_dict())
        self._save_json(self.feedback_file, feedback_list)
        
        return True
    
    def get_user_feedback(self, user_email: str) -> List[Dict]:
        """Get user's feedback history"""
        feedback_list = self._load_json(self.feedback_file)
        return [f for f in feedback_list if f.get('user_email') == user_email]