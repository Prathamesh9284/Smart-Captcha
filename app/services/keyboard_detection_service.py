import pandas as pd
import joblib
from app.config import get_settings

class KeyboardDetectionService:
    """Service for keyboard typing detection"""
    
    def __init__(self):
        settings = get_settings()
        self.model = joblib.load(settings.KEYBOARD_MODEL_PATH)
    
    def predict(self, data: pd.DataFrame) -> str:
        """Predict if keyboard typing is from human or bot"""
        try:
            # Convert timestamps
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            # Calculate time differences grouped by field
            data['time_diff'] = data.groupby('fieldName')['timestamp'].diff().dt.total_seconds().fillna(0)
            
            # Extract features: mean, std, min, max of time differences
            features = data.groupby('fieldName')['time_diff'].agg(['mean', 'std', 'min', 'max']).reset_index()
            
            # Flatten features into a single row
            feature_vector = features.drop('fieldName', axis=1).values.flatten()
            
            # Make prediction
            prediction = self.model.predict([feature_vector])
            
            # Return result
            return 'Bot' if prediction[0] == 1 else 'Human'
            
        except Exception as e:
            print(f"Keyboard prediction error: {e}")
            return f"Error: {str(e)}"