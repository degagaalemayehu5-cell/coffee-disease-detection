"""
Coffee Disease Predictor Utility
Updated for MobileNetV2_best.h5 model
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import warnings
warnings.filterwarnings('ignore')


class CoffeeDiseasePredictor:
    """Coffee leaf disease prediction class for MobileNetV2 model"""
    
    def __init__(self, model_path='models/MobileNetV2_best.h5', 
                 class_names_path='models/class_names.json'):
        
        self.model_path = model_path
        self.class_names_path = class_names_path
        self.model = None
        self.class_names = None
        self.idx_to_class = None
        
        # Load model with compatibility
        self._load_model()
        
        # Load class names
        self._load_class_names()
    
    def _load_model(self):
        """Load model with compatibility fixes"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        try:
            # Try loading with compile=False first
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            print(f"✓ Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            try:
                # Try with safe_mode=False
                self.model = tf.keras.models.load_model(self.model_path, compile=False, safe_mode=False)
                print(f"✓ Model loaded with safe_mode=False")
            except Exception as e2:
                raise RuntimeError(f"Failed to load model: {e2}")
    
    def _load_class_names(self):
        """Load class names from JSON file"""
        if not os.path.exists(self.class_names_path):
            raise FileNotFoundError(f"Class names not found: {self.class_names_path}")
        
        with open(self.class_names_path, 'r') as f:
            class_data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(class_data, list):
            self.class_names = class_data
            self.idx_to_class = {idx: name for idx, name in enumerate(class_data)}
        elif isinstance(class_data, dict):
            self.class_names = list(class_data.keys())
            self.idx_to_class = {v: k for k, v in class_data.items()}
        else:
            raise ValueError(f"Unexpected class_names format: {type(class_data)}")
        
        print(f"✓ Class names loaded: {self.class_names}")
    
    def preprocess(self, image, target_size=(224, 224)):
        """Preprocess image for model prediction"""
        image = image.resize(target_size)
        img_array = np.array(image)
        
        # Handle grayscale (convert to RGB)
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image):
        """Predict disease class for an image"""
        if self.model is None:
            return {
                'success': False,
                'error': 'Model not loaded'
            }
        
        if self.idx_to_class is None:
            return {
                'success': False,
                'error': 'Class names not loaded'
            }
        
        # Preprocess
        processed = self.preprocess(image)
        
        # Predict
        predictions = self.model.predict(processed, verbose=0)
        
        # Get results
        predicted_idx = np.argmax(predictions[0])
        predicted_class = self.idx_to_class[predicted_idx]
        confidence = float(predictions[0][predicted_idx])
        
        # Get all probabilities
        probabilities = {
            self.idx_to_class[i]: float(predictions[0][i])
            for i in range(len(self.idx_to_class))
        }
        
        return {
            'class': predicted_class,
            'confidence': confidence,
            'probabilities': probabilities,
            'success': True
        }
    
    def predict_batch(self, images):
        """Predict for multiple images at once"""
        results = []
        for img in images:
            results.append(self.predict(img))
        return results
    
    def get_model_info(self):
        """Return model information"""
        if self.model is None:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'model_path': self.model_path,
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'num_classes': len(self.class_names) if self.class_names else 0,
            'class_names': self.class_names
        }


# Test function
if __name__ == "__main__":
    print("Testing CoffeeDiseasePredictor...")
    
    try:
        predictor = CoffeeDiseasePredictor()
        info = predictor.get_model_info()
        print(f"Model info: {info}")
        
        test_image_path = "test_image.jpg"
        if os.path.exists(test_image_path):
            image = Image.open(test_image_path).convert('RGB')
            result = predictor.predict(image)
            print(f"Prediction: {result}")
        else:
            print("No test image found. Skipping prediction test.")
            
    except Exception as e:
        print(f"Error: {e}")