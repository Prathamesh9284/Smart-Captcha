import time
from typing import Dict, Any

def get_current_timestamp() -> int:
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)

def validate_browser_info(browser_info: Dict[str, Any]) -> bool:
    """Validate browser information"""
    required_fields = ['userAgent', 'platform', 'screenResolution']
    return all(field in browser_info for field in required_fields)

def format_log_message(message: str, data: Dict[str, Any]) -> str:
    """Format log message with data"""
    return f"{message}: {data}"