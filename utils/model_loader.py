"""
Custom model loader - Downloads model from Google Drive with TF 2.15 Compatibility Patches
"""

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, InputLayer
import os
import warnings
import requests
import streamlit as st
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

GOOGLE_DRIVE_FILE_ID = "1cP3kw4Cs5SCqQnrrAmS9od0KHnumTStK"
MODEL_FILENAME = "MobileNetV2_best.h5"
MODEL_PATH = os.path.join("models", MODEL_FILENAME)

# ============================================================================
# COMPATIBILITY LAYER FOR KERAS 3 / TF 2.15 CROSS-VERSION ISSUES
# ============================================================================

class CompatibleInputLayer(InputLayer):
    """InputLayer that ignores Keras 3 specific parameters"""
    def __init__(self, *args, **kwargs):
        # Remove Keras 3 exclusive structural parameters
        kwargs.pop('batch_shape', None)
        kwargs.pop('optional', None)
        super().__init__(*args, **kwargs)
    
    @classmethod
    def from_config(cls, config):
        # Clean config before deserialization
        config.pop('batch_shape', None)
        config.pop('optional', None)
        return super().from_config(config)


class CompatibleDense(Dense):
    """Dense layer that ignores quantization_config parameter"""
    def __init__(self, *args, **kwargs):
        # Remove quantization_config if present
        kwargs.pop('quantization_config', None)
        super().__init__(*args, **kwargs)
    
    @classmethod
    def from_config(cls, config):
        config.pop('quantization_config', None)
        return super().from_config(config)

# ============================================================================
# DOWNLOAD FUNCTION
# ============================================================================

def download_model_from_drive():
    """Download model from Google Drive if it does not exist or is invalid"""
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Check if model exists and is valid (not the 1KB pointer)
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        if file_size > 5:  # Valid model > 5MB
            print(f"✅ Model already exists: {MODEL_PATH} ({file_size:.1f} MB)")
            return MODEL_PATH
    
    print(f"📥 Downloading model from Google Drive...")
    
    # CORRECTED: Use the standard Google Drive download URL
    url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"
    
    try:
        # Start a session to handle cookies
        session = requests.Session()
        response = session.get(url, stream=True)
        
        # Handle Google Drive's virus scan warning
        if "quota" in response.text or "confirm" in response.text:
            import re
            # Extract confirm token
            confirm_match = re.search(r'confirm=([^&]+)', response.text)
            if confirm_match:
                confirm = confirm_match.group(1)
                url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}&confirm={confirm}"
                response = session.get(url, stream=True)
        
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
    """Load model, downloading from Drive first if needed, applying version patches"""
    
    if model_path is None:
        model_path = MODEL_PATH
    
    # Run the download sequence under a visual Streamlit spinner wrapper
    with st.spinner("📦 Fetching model weights from cloud repository... Please wait."):
        model_path = download_model_from_drive()
    
    if model_path is None:
        print("❌ Could not download model")
        return None
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return None
    
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📁 Loading model from: {model_path} ({file_size:.1f} MB)")
    
    # Check if this is a valid model (not a 1KB pointer file or broken network package)
    if file_size < 1.0:
        print("❌ Model file is too small - download failed or corrupted")
        return None
    
    # Register custom objects for deserialization
    custom_objects = {
        'InputLayer': CompatibleInputLayer,
        'Dense': CompatibleDense,
        'Functional': tf.keras.Model,
        'Sequential': tf.keras.Sequential
    }
    
    try:
        # Attempt 1: Safe deserialization loading without graph compilation blocks
        model = load_model(model_path, compile=False, custom_objects=custom_objects)
        print("✅ Model loaded successfully!")
        return model
    except Exception as e:
        print(f"⚠️ First attempt failed: {e}")
        try:
            # Attempt 2: Override strict tracking flags via safe_mode fallback
            model = load_model(model_path, compile=False, safe_mode=False, custom_objects=custom_objects)
            print("✅ Model loaded with safe_mode=False!")
            return model
        except Exception as e2:
            print(f"❌ All loading attempts failed: {e2}")
            return None