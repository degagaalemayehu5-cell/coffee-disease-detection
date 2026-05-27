"""
Custom model loader to handle Keras models
"""

import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import warnings
warnings.filterwarnings('ignore')

def load_model_compatible(model_path):
    """Load model with compatibility fixes"""
    
    print(f"Attempting to load model from: {model_path}")
    
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return None
    
    # Get file size
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📁 Model file size: {file_size:.1f} MB")
    
    # Check if it's the dummy model (small size)
    if file_size < 1.0:
        print("⚠️ This appears to be a dummy model, not the real model")
        return None
    
    try:
        # Try loading with compile=False first
        model = load_model(model_path, compile=False)
        print(f"✅ Model loaded successfully: {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        
        try:
            # Try with custom objects
            model = load_model(model_path, compile=False, safe_mode=False)
            print(f"✅ Model loaded with safe_mode=False")
            return model
        except Exception as e2:
            print(f"Second attempt failed: {e2}")
            return None


def load_model_with_fallback(model_path):
    """Load model, return (model, is_fallback)"""
    
    model = load_model_compatible(model_path)
    
    if model is None:
        print("⚠️ Creating fallback model - predictions will be random!")
        # Create a simple model that always predicts Healthy
        inputs = tf.keras.layers.Input(shape=(224, 224, 3))
        x = tf.keras.layers.Flatten()(inputs)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        outputs = tf.keras.layers.Dense(5, activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model, True
    
    return model, False