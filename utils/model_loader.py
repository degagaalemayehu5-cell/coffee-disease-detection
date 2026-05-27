import tensorflow as tf
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.models import load_model

class CustomInputLayer(InputLayer):
    def __init__(self, *args, **kwargs):
        # 1. Capture the batch_shape Keras 3 gave it
        batch_shape = kwargs.pop('batch_shape', None)
        
        # 2. Map it to the 'batch_input_shape' key that Keras 2 actually understands
        if batch_shape and 'batch_input_shape' not in kwargs:
            kwargs['batch_input_shape'] = batch_shape
            
        # 3. Strip out the unsupported 'optional' flag completely
        kwargs.pop('optional', None)
        
        super().__init__(*args, **kwargs)

class CustomDense(Dense):
    def __init__(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(*args, **kwargs)

# Register both to patch the version gap
custom_objects = {
    'InputLayer': CustomInputLayer,
    'Dense': CustomDense
}

def load_model_compatible(model_path):
    try:
        # Load without compiling to skip optimizer configuration mismatches
        return load_model(model_path, custom_objects=custom_objects, compile=False)
    except Exception as e:
        print(f"Error: {e}")
        return None