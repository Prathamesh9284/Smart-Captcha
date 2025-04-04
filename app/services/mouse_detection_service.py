import pandas as pd
import numpy as np
import joblib
from app.config import get_settings

class MouseDetectionService:
    """Service for mouse movement detection"""
    
    def __init__(self):
        settings = get_settings()
        self.model = joblib.load(settings.MOUSE_MODEL_PATH)
    
    def predict(self, data: pd.DataFrame) -> str:
        """Predict if mouse movement is from human or bot"""
        try:
            # Convert timestamps
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
            
            # Handle invalid timestamps
            if data['timestamp'].isna().any():
                return "Error: Invalid timestamps"
            
            # Feature engineering
            data['time_diff'] = data['timestamp'].diff().dt.total_seconds().fillna(0) * 1000
            data['distance'] = np.sqrt((data['x'].diff()**2) + (data['y'].diff()**2)).fillna(0)
            data['speed'] = data['distance'] / data['time_diff'].replace(0, np.nan).fillna(0)
            data['direction'] = np.arctan2(data['y'].diff(), data['x'].diff()).fillna(0)
            data['curvature'] = data['direction'].diff().fillna(0)
            
            # Select relevant columns
            data = data[['time_diff', 'distance', 'speed', 'direction', 'curvature']]
            
            # Check if data is valid
            if data.empty:
                return "Error: No valid data for prediction"
            
            # Make prediction
            predictions = self.model.predict(data)
            
            # Count predictions
            human_count = (predictions == 0).sum()
            bot_count = (predictions == 1).sum()
            
            # Return final prediction
            return "Human" if human_count > bot_count else "Bot"
            
        except Exception as e:
            print(f"Mouse prediction error: {e}")
            return f"Error: {str(e)}"