"""
Coffee Disease Predictor Utility
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os

class CoffeeDiseasePredictor:
    """Coffee leaf disease prediction class"""
    
    def __init__(self, model_path='models/coffee_leaf_final_99pct.h5', 
                 class_indices_path='models/class_indices.json'):
        
        self.model_path = model_path
        self.class_indices_path = class_indices_path
        
        # Load model
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            print(f"✓ Model loaded from {model_path}")
        else:
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load class indices
        if os.path.exists(class_indices_path):
            with open(class_indices_path, 'r') as f:
                self.class_indices = json.load(f)
            self.idx_to_class = {v: k for k, v in self.class_indices.items()}
            print(f"✓ Class indices loaded: {list(self.class_indices.keys())}")
        else:
            raise FileNotFoundError(f"Class indices not found: {class_indices_path}")
    
    def preprocess(self, image, target_size=(224, 224)):
        """Preprocess image for prediction"""
        image = image.resize(target_size)
        img_array = np.array(image)
        
        # Handle grayscale
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict(self, image):
        """Predict disease class for an image"""
        processed = self.preprocess(image)
        predictions = self.model.predict(processed, verbose=0)
        
        predicted_idx = np.argmax(predictions[0])
        predicted_class = self.idx_to_class[predicted_idx]
        confidence = predictions[0][predicted_idx]
        
        probabilities = {
            self.idx_to_class[i]: float(predictions[0][i])
            for i in range(len(self.idx_to_class))
        }
        
        return {
            'class': predicted_class,
            'confidence': float(confidence),
            'probabilities': probabilities,
            'success': True
        }