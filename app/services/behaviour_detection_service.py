import pandas as pd
import asyncio
from io import BytesIO
from typing import Dict, Any

from app.services.mouse_detection_service import MouseDetectionService
from app.services.keyboard_detection_service import KeyboardDetectionService
from app.services.browser_detection_service import BrowserDetectionService
from app.repositories.firebase_repository import FirebaseRepository

class BehaviorDetectionService:
    """Service for detecting bot behavior through multiple sources"""
    
    def __init__(self):
        self.mouse_service = MouseDetectionService()
        self.keyboard_service = KeyboardDetectionService()
        self.browser_service = BrowserDetectionService()
        self.firebase_repo = FirebaseRepository()
    
    async def analyze_behavior(self, 
                              mouse_data: bytes, 
                              key_data: bytes, 
                              browser_info: Dict[str, Any], 
                              fingerprint: str) -> Dict[str, str]:
        """Analyze user behavior from multiple data sources"""
        try:
            # Process mouse data
            mouse_df = pd.read_csv(BytesIO(mouse_data))
            
            # Process keyboard data
            key_df = pd.read_csv(BytesIO(key_data))
            
            # Run predictions concurrently
            mouse_result, key_result, is_bot = await asyncio.gather(
                asyncio.to_thread(self.mouse_service.predict, mouse_df),
                asyncio.to_thread(self.keyboard_service.predict, key_df),
                self.firebase_repo.is_bot_fingerprint(fingerprint)
            )
            
            # Detect browser automation
            is_automated = self.browser_service.detect_automation(browser_info)
            
            # Log results
            print(f'Mouse is controlled by: {mouse_result}')
            print(f'Keyboard is controlled by: {key_result}')
            print(f'Malicious Browser found?: {is_automated}')
            print(f'Is device fingerprint blacklisted?: {is_bot}')
            
            # Return combined results
            return {
                'mouse_result': mouse_result,
                'key_result': key_result,
                'is_automated': is_automated,
                'is_bot': is_bot
            }
            
        except Exception as e:
            print(f"Error in behavior analysis: {e}")
            raise