"""
Custom model loader to handle Keras models
"""

import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import warnings
warnings.filterwarnings('ignore')


class DenseWithQuantization(tf.keras.layers.Dense):
    """Dense layer subclass that ignores missing quantization config during deserialization."""

    @classmethod
    def from_config(cls, config):
        config.pop('quantization_config', None)
        return super().from_config(config)


def load_model_compatible(model_path):
    """Load model with compatibility fixes."""
    
    print(f"Attempting to load model from: {model_path}")

    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return None

    file_size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"📁 Model file size: {file_size:.1f} MB")

    # No dummy model check - this will only load real models
    custom_objects = {
        'Dense': DenseWithQuantization
    }

    try:
        model = load_model(model_path, compile=False, custom_objects=custom_objects)
        print(f"✅ Model loaded successfully: {model_path}")
        return model
    except Exception as e:
        print(f"⚠️ First attempt failed: {e}")
        try:
            model = load_model(model_path, compile=False, safe_mode=False, custom_objects=custom_objects)
            print(f"✅ Model loaded with safe_mode=False")
            return model
        except Exception as e2:
            print(f"❌ Second attempt failed: {e2}")
            return None