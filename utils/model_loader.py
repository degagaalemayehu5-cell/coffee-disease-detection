"""
Custom model loader - Downloads model from Google Drive
"""

import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import warnings
import requests
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION – REPLACE WITH YOUR GOOGLE DRIVE FILE ID
# ============================================================================

GOOGLE_DRIVE_FILE_ID = "1cP3kw4Cs5SCqQnrrAmS9od0KHnumTStK"   # <-- your ID
MODEL_FILENAME = "MobileNetV2_best.h5"
MODEL_PATH = os.path.join("models", MODEL_FILENAME)

# ============================================================================
# DOWNLOAD FUNCTION
# ============================================================================

def download_model_from_drive():
    """Download model from Google Drive if not exists or invalid"""
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Check if model exists and is valid (not the 1KB pointer)
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        if file_size > 5:  # Valid model > 5MB
            print(f"✅ Model already exists: {MODEL_PATH} ({file_size:.1f} MB)")
            return MODEL_PATH
    
    print(f"📥 Downloading model from Google Drive...")
    
    # Direct download URL
    url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"
    
    try:
        # Download the file
        response = requests.get(url, stream=True)
        
        # Handle Google Drive's virus scan warning
        if "quota" in response.text or "confirm" in response.text:
            import re
            confirm = re.search(r'confirm=([^&]+)', response.text)
            if confirm:
                url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}&confirm={confirm.group(1)}"
                response = requests.get(url, stream=True)
        
        # Save the file
        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"✅ Model downloaded successfully! ({file_size:.1f} MB)")
        return MODEL_PATH
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


# ============================================================================
# MODEL LOADER
# ============================================================================

def load_model_compatible(model_path=None):
    """Load model, downloading from Drive first if needed"""
    
    if model_path is None:
        model_path = MODEL_PATH
    
    # Ensure we have the real model file
    model_path = download_model_from_drive()
    
    if model_path is None:
        print("❌ Could not download model")
        return None
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return None
    
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📁 Loading model from: {model_path} ({file_size:.1f} MB)")
    
    # Check if this is a valid model (not the tiny pointer file)
    if file_size < 1.0:
        print("❌ Model file is too small - download failed or corrupted")
        return None
    
    try:
        # Try loading with compile=False
        model = load_model(model_path, compile=False)
        print("✅ Model loaded successfully!")
        return model
    except Exception as e:
        print(f"⚠️ First attempt failed: {e}")
        try:
            # Try with safe_mode=False
            model = load_model(model_path, compile=False, safe_mode=False)
            print("✅ Model loaded with safe_mode=False!")
            return model
        except Exception as e2:
            print(f"❌ All loading attempts failed: {e2}")
            return None