"""
Database models for Coffee Leaf Disease Detection
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class User:
    """User model for authentication and profile"""
    
    def __init__(self, email: str, password: str, name: str = "", created_at: datetime = None):
        self.email = email
        self.password = password  # This should be hashed
        self.name = name
        self.created_at = created_at or datetime.now()
        self.language_preference = 'en'
        self.total_predictions = 0
        self.is_active = True
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON storage"""
        return {
            'email': self.email,
            'password': self.password,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'language_preference': self.language_preference,
            'total_predictions': self.total_predictions,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary"""
        user = cls(
            email=data['email'],
            password=data['password'],
            name=data.get('name', ''),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at')
        )
        user.language_preference = data.get('language_preference', 'en')
        user.total_predictions = data.get('total_predictions', 0)
        user.is_active = data.get('is_active', True)
        return user
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Create user from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class Prediction:
    """Prediction model for storing disease detection results"""
    
    def __init__(
        self,
        user_email: str,
        predicted_disease: str,
        confidence: float,
        image_name: str = "",
        image_url: str = "",
        all_probabilities: Dict[str, float] = None,
        crop_used: bool = False,
        created_at: datetime = None
    ):
        self.user_email = user_email
        self.predicted_disease = predicted_disease
        self.confidence = confidence
        self.image_name = image_name
        self.image_url = image_url
        self.all_probabilities = all_probabilities or {}
        self.crop_used = crop_used
        self.created_at = created_at or datetime.now()
        self.model_version = 'MobileNetV2_v1'
    
    def to_dict(self) -> dict:
        """Convert prediction to dictionary"""
        return {
            'user_email': self.user_email,
            'predicted_disease': self.predicted_disease,
            'confidence': self.confidence,
            'image_name': self.image_name,
            'image_url': self.image_url,
            'all_probabilities': self.all_probabilities,
            'crop_used': self.crop_used,
            'created_at': self.created_at.isoformat(),
            'model_version': self.model_version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Prediction':
        """Create prediction from dictionary"""
        return cls(
            user_email=data['user_email'],
            predicted_disease=data['predicted_disease'],
            confidence=data['confidence'],
            image_name=data.get('image_name', ''),
            image_url=data.get('image_url', ''),
            all_probabilities=data.get('all_probabilities', {}),
            crop_used=data.get('crop_used', False),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at')
        )


class Feedback:
    """Feedback model for user feedback on predictions"""
    
    def __init__(
        self,
        prediction_id: str,
        user_email: str,
        was_correct: bool,
        actual_disease: str = None,
        comment: str = None,
        created_at: datetime = None
    ):
        self.prediction_id = prediction_id
        self.user_email = user_email
        self.was_correct = was_correct
        self.actual_disease = actual_disease if not was_correct else None
        self.comment = comment
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert feedback to dictionary"""
        return {
            'prediction_id': self.prediction_id,
            'user_email': self.user_email,
            'was_correct': self.was_correct,
            'actual_disease': self.actual_disease,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Feedback':
        """Create feedback from dictionary"""
        return cls(
            prediction_id=data['prediction_id'],
            user_email=data['user_email'],
            was_correct=data['was_correct'],
            actual_disease=data.get('actual_disease'),
            comment=data.get('comment'),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at')
        )