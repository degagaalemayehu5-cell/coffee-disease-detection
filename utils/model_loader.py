import tensorflow as tf
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings('ignore')

# 1. Custom InputLayer to strip out Keras 3 specifics
class CustomInputLayer(InputLayer):
    def __init__(self, *args, **kwargs):
        # Strip out Keras 3 fields that break Keras 2 / older Keras 3
        kwargs.pop('batch_shape', None)
        kwargs.pop('optional', None)
        super().__init__(*args, **kwargs)

# 2. Your existing Custom Dense Layer
class CustomDense(Dense):
    def __init__(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(*args, **kwargs)

# Register BOTH custom objects so Keras uses them during loading
custom_objects = {
    'InputLayer': CustomInputLayer,
    'Dense': CustomDense
}

def load_model_compatible(model_path):
    """Load model with compatibility fixes for both Input and Dense layers"""
    try:
        # Load with safe_mode=False if your Keras version supports it
        model = load_model(model_path, custom_objects=custom_objects, compile=False)
        print(f"✓ Model loaded: {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None