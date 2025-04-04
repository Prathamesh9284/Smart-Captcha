import time
import asyncio
import firebase_admin
from firebase_admin import credentials, db
from app.config import get_settings

class FirebaseRepository:
    """Repository for Firebase operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseRepository, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            settings = get_settings()
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL
                })
                self._initialized = True
            except Exception as e:
                print(f"Error initializing Firebase: {e}")
    
    async def is_bot_fingerprint(self, fingerprint: str) -> str:
        """Check if fingerprint is in the blacklist"""
        try:
            # Reference to the 'bots' node in Firebase
            bots_ref = db.reference('bots')
            
            # Query the database
            snapshot = await asyncio.to_thread(bots_ref.child(fingerprint).get)
            
            # Return result
            return 'Yes' if snapshot else 'No'
                
        except Exception as e:
            print(f"Error checking bot status: {e}")
            return 'No'
    
    async def save_fingerprint_visit(self, fingerprint: str, timestamp: int) -> dict:
        """Save fingerprint and timestamp to Firebase"""
        try:
            # Save fingerprint and timestamp
            fingerprint_ref = db.reference(f'fingerprints/{fingerprint}')
            new_visit_ref = fingerprint_ref.push()
            await asyncio.to_thread(new_visit_ref.set, {
                'timestamp': timestamp,
                'fingerprint': fingerprint
            })
            
            # Check recent visits
            recent_entries_count = await self.check_recent_entries(fingerprint)
            
            # If too many recent visits, add to bot list
            if recent_entries_count > 15:
                bots_ref = db.reference('bots')
                await asyncio.to_thread(bots_ref.update, {fingerprint: fingerprint})
            
            return {
                'message': 'Fingerprint and visit info saved successfully!',
                'timestamp': timestamp,
                'fingerprint': fingerprint
            }
            
        except Exception as e:
            print(f"Error saving fingerprint visit: {e}")
            raise
    
    async def check_recent_entries(self, fingerprint: str) -> int:
        """Count recent entries with the same fingerprint"""
        try:
            # Calculate timestamp for 30 seconds ago
            thirty_seconds_ago = int(time.time() * 1000) - 30000
            
            # Reference to the database path
            fingerprint_ref = db.reference(f'fingerprints/{fingerprint}')
            
            # Create a query to get entries from the last 30 seconds
            query = fingerprint_ref.order_by_child('timestamp').start_at(thirty_seconds_ago)
            
            # Retrieve and count entries
            snapshot = await asyncio.to_thread(query.get)
            if snapshot:
                count = len(snapshot)
                print(f'Recent entries count: {count}')
                return count
            
            return 0
                
        except Exception as e:
            print(f"Error checking recent entries: {e}")
            return 0