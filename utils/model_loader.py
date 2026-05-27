"""
Custom model loader to handle Keras 3.13 models in Keras 3.12
And handle legacy models with batch_shape/optional parameters
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings('ignore')

class CustomDense(Dense):
    """Custom Dense layer that ignores quantization_config"""
    def __init__(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(*args, **kwargs)


class CustomInputLayer(InputLayer):
    """Custom InputLayer that removes unsupported parameters"""
    def __init__(self, *args, **kwargs):
        # Remove parameters that cause issues in older TensorFlow versions
        kwargs.pop('batch_shape', None)
        kwargs.pop('optional', None)
        super().__init__(*args, **kwargs)


# Register custom objects for loading legacy models
custom_objects = {
    'Dense': CustomDense,
    'InputLayer': CustomInputLayer,
    'Functional': tf.keras.models.Model,
    'Sequential': tf.keras.models.Sequential
}


def load_model_compatible(model_path):
    """Load model with compatibility fixes for different TensorFlow versions"""
    
    print(f"Attempting to load model from: {model_path}")
    
    # Try different loading strategies
    strategies = [
        # Strategy 1: With custom objects, no compilation
        lambda: load_model(model_path, custom_objects=custom_objects, compile=False),
        
        # Strategy 2: Without custom objects
        lambda: load_model(model_path, compile=False),
        
        # Strategy 3: Default loading
        lambda: tf.keras.models.load_model(model_path),
        
        # Strategy 4: With custom_objects and allow_pickle
        lambda: load_model(model_path, custom_objects=custom_objects, compile=False, safe_mode=False),
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            model = strategy()
            print(f"✓ Model loaded successfully using strategy {i+1}")
            return model
        except Exception as e:
            print(f"Strategy {i+1} failed: {e}")
            continue
    
    print(f"❌ All loading strategies failed for {model_path}")
    return None


def load_model_with_fallback(model_path):
    """Load model with fallback to dummy model if fails"""
    model = load_model_compatible(model_path)
    
    if model is None:
        print("⚠️ Creating fallback model for testing")
        # Create a simple fallback model
        dummy_input = tf.keras.layers.Input(shape=(224, 224, 3))
        x = tf.keras.layers.Flatten()(dummy_input)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        output = tf.keras.layers.Dense(5, activation='softmax')(x)
        model = tf.keras.Model(inputs=dummy_input, outputs=output)
        
        print("⚠️ USING FALLBACK MODEL - predictions may not be accurate")
        return model, True
    
    return model, False