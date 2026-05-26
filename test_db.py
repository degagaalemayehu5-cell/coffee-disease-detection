# test_db.py
from dotenv import load_dotenv
from utils.database import db

load_dotenv()

print("Testing MongoDB connection...")

if db and db.client:
    print("✅ Connected successfully!")
    print(f"Database: {db.db.name}")
    
    # Test creating a user
    success, message = db.create_user("test@example.com", "test123", "Test User")
    print(f"Create user: {message}")
    
    # Test login
    success, message = db.verify_user("test@example.com", "test123")
    print(f"Login test: {message}")
else:
    print("❌ Connection failed!")