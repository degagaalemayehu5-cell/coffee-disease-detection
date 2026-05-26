"""
Database module for Coffee Leaf Disease Detection
Exports database manager and models
"""

from database.db_manager import DatabaseManager
from database.models import User, Prediction, Feedback

# Create a singleton instance
db_manager = DatabaseManager()

__all__ = ['db_manager', 'User', 'Prediction', 'Feedback']