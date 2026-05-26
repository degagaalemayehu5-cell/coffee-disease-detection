"""
Custom model loader to handle Keras 3.13 models in Keras 3.12
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings('ignore')

class CustomDense(Dense):
    """Custom Dense layer that ignores quantization_config"""
    def __init__(self, *args, **kwargs):
        # Remove quantization_config if present
        kwargs.pop('quantization_config', None)
        super().__init__(*args, **kwargs)

custom_objects = {'Dense': CustomDense}

def load_model_compatible(model_path):
    """Load model with compatibility fixes"""
    try:
        model = load_model(model_path, custom_objects=custom_objects, compile=False)
        print(f"✓ Model loaded: {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None