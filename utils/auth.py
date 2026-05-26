"""
Authentication module for Coffee Leaf Disease Detection System
Handles user authentication, profile management, and database operations
Includes PWA install features
"""

import streamlit as st
import streamlit.components.v1 as components
import bcrypt
import json
import os
from datetime import datetime
import re

# Import database module
from utils.database import db

# ============================================================================
# PWA FUNCTIONS
# ============================================================================

from utils.pwa import get_pwa_install_html, get_pwa_status_html

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def login_user(email, password):
    """
    Authenticate user with email and password
    
    Args:
        email (str): User's email
        password (str): User's password
    
    Returns:
        tuple: (success, message)
    """
    if db is None:
        return False, "Database connection error. Please check your .env configuration."
    
    success, message = db.verify_user(email, password)
    return success, message

def signup_user(email, password, name=""):
    """
    Register a new user
    
    Args:
        email (str): User's email address
        password (str): User's password
        name (str): User's full name (optional)
    
    Returns:
        tuple: (success, message)
    """
    if db is None:
        return False, "Database connection error. Please check your .env configuration."
    
    # Validate email format
    if not validate_email(email):
        return False, "Invalid email format. Please enter a valid email address."
    
    # Validate password strength
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    success, message = db.create_user(email, password, name)
    return success, message

def validate_email(email):
    """
    Validate email format using regex
    
    Args:
        email (str): Email to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def get_user_history(email, limit=50):
    """
    Get prediction history for a user
    
    Args:
        email (str): User's email
        limit (int): Maximum number of records to return
    
    Returns:
        list: List of prediction records
    """
    if db is None:
        return []
    return db.get_user_predictions(email, limit)

def save_prediction_to_db(user_email, prediction_data):
    """
    Save prediction to database
    
    Args:
        user_email (str): User's email
        prediction_data (dict): Prediction results
    
    Returns:
        ObjectId: Inserted record ID or None
    """
    if db is None:
        return None
    return db.save_prediction(user_email, prediction_data)

def get_db_stats(user_email=None):
    """
    Get database statistics for user or overall
    
    Args:
        user_email (str, optional): User's email
    
    Returns:
        dict: Statistics including total predictions, average confidence, etc.
    """
    if db is None:
        return {}
    return db.get_statistics(user_email)

# ============================================================================
# PROFILE MANAGEMENT FUNCTIONS
# ============================================================================

def update_user_profile(email, name=None, language=None):
    """
    Update user profile information
    
    Args:
        email (str): User's email
        name (str, optional): New name
        language (str, optional): Language preference
    
    Returns:
        tuple: (success, message)
    """
    if db is None:
        return False, "Database connection error"
    
    update_data = {}
    if name:
        update_data['name'] = name
    if language:
        update_data['language_preference'] = language
    
    if not update_data:
        return False, "No changes made"
    
    try:
        result = db.update_user(email, **update_data)
        if result[0]:
            return True, "Profile updated successfully"
        return False, result[1]
    except Exception as e:
        return False, f"Error updating profile: {str(e)}"

def change_user_password(email, current_password, new_password):
    """
    Change user password
    
    Args:
        email (str): User's email
        current_password (str): Current password
        new_password (str): New password
    
    Returns:
        tuple: (success, message)
    """
    if db is None:
        return False, "Database connection error"
    
    # Verify current password
    success, message = db.verify_user(email, current_password)
    if not success:
        return False, "Current password is incorrect"
    
    # Validate new password strength
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long"
    
    if current_password == new_password:
        return False, "New password must be different from current password"
    
    # Hash new password
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    
    # Update password
    try:
        result = db.update_user(email, password=hashed_password)
        if result[0]:
            return True, "Password changed successfully. Please login again."
        return False, result[1]
    except Exception as e:
        return False, f"Error changing password: {str(e)}"

def delete_user_account(email, password):
    """
    Delete user account and all associated data
    
    Args:
        email (str): User's email
        password (str): Password for verification
    
    Returns:
        tuple: (success, message)
    """
    if db is None:
        return False, "Database connection error"
    
    # Verify password
    success, message = db.verify_user(email, password)
    if not success:
        return False, "Incorrect password"
    
    try:
        result = db.delete_user(email, password)
        return result
    except Exception as e:
        return False, f"Error deleting account: {str(e)}"

def get_user_info(email):
    """
    Get user information
    
    Args:
        email (str): User's email
    
    Returns:
        dict: User information or None
    """
    if db is None:
        return None
    return db.get_user(email)

# ============================================================================
# SESSION MANAGEMENT FUNCTIONS
# ============================================================================

def check_authentication():
    """
    Check if user is logged in, show login/signup if not
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_signup()
        return False
    return True

def show_login_signup():
    """Display login/signup interface with PWA install button"""
    
    # PWA Install Banner and Status
    components.html(get_pwa_install_html(), height=260, scrolling=False)
    st.markdown(get_pwa_status_html(), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🌿 Coffee Leaf Disease Detection</h1>
        <p style="font-size: 1.2rem;">AI-Powered Diagnosis for Ethiopian Coffee Farmers</p>
        <p>Please login or signup to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("Please fill all fields")
                else:
                    with st.spinner("Logging in..."):
                        success, message = login_user(email, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    
    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Full Name (Optional)", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("Email and password are required")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        success, message = signup_user(email, password, name)
                        if success:
                            st.success(message)
                            st.info("Please login with your credentials")
                        else:
                            st.error(message)

def logout_user():
    """Clear session state and logout"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================================
# FEEDBACK FUNCTIONS
# ============================================================================

def save_feedback_to_db(feedback_data: dict) -> bool:
    """
    Save user feedback to database
    
    Args:
        feedback_data (dict): Feedback information
    
    Returns:
        bool: True if saved successfully
    """
    if db is None:
        return False
    
    try:
        if 'created_at' not in feedback_data:
            feedback_data['created_at'] = datetime.now().isoformat()
        
        result = db.save_feedback(feedback_data)
        return result
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_feedback_stats(user_email: str = None) -> dict:
    """
    Get feedback statistics
    
    Args:
        user_email (str, optional): Filter by user
    
    Returns:
        dict: Statistics
    """
    if db is None:
        return {}
    
    try:
        feedback_list = db.get_feedback(user_email) if user_email else db.get_all_feedback()
        
        total = len(feedback_list)
        if total == 0:
            return {'total': 0, 'accuracy_rate': 0, 'total_correct': 0, 'total_wrong': 0}
        
        correct_count = sum(1 for f in feedback_list if f.get('was_correct', False))
        
        return {
            'total': total,
            'accuracy_rate': (correct_count / total * 100),
            'total_correct': correct_count,
            'total_wrong': total - correct_count
        }
    except Exception as e:
        print(f"Error getting feedback stats: {e}")
        return {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_achievements(email):
    """
    Get user achievements based on activity
    
    Args:
        email (str): User's email
    
    Returns:
        list: List of achievements
    """
    stats = get_db_stats(email)
    total_predictions = stats.get('total_predictions', 0)
    avg_confidence = stats.get('avg_confidence', 0)
    
    achievements = []
    
    if total_predictions >= 1:
        achievements.append({"name": "First Prediction", "icon": "🌱", "description": "Made your first prediction"})
    if total_predictions >= 10:
        achievements.append({"name": "10 Predictions", "icon": "⭐", "description": "Made 10 predictions"})
    if total_predictions >= 50:
        achievements.append({"name": "50 Predictions", "icon": "🏅", "description": "Made 50 predictions"})
    if total_predictions >= 100:
        achievements.append({"name": "100 Predictions", "icon": "🎖️", "description": "Made 100 predictions"})
    if total_predictions >= 500:
        achievements.append({"name": "Expert", "icon": "👑", "description": "Made 500 predictions"})
    if avg_confidence > 90:
        achievements.append({"name": "High Accuracy", "icon": "🎯", "description": "Average confidence above 90%"})
    
    return achievements