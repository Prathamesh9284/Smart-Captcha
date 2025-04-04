from typing import Dict, Any

class BrowserDetectionService:
    """Service for browser automation detection"""
    
    def __init__(self):
        self.known_patterns = {
            'userAgent': [
                # Common user agents for popular browsers
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.67',
                'Mozilla/5.0 (Linux; Android 11; SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
                'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            ],
            'webdriver': [
                False  # Expected webdriver status for non-automated browsers
            ],
            'platform': [
                'Win32', 'Win64', 'MacIntel', 'Linux x86_64', 'iPhone', 'iPad', 'Android', 'Linux armv7l',
                'Linux armv8l', 'Linux aarch64', 'Linux i686', 'Linux x86',
            ],
            'screenResolution': [
                '1920x1080', '1366x768', '1440x900', '1536x864', '1600x900', '1280x720', '2560x1440', '1536x864',
                '3840x2160', '2560x1600', '2880x1800', '320x480', '360x640', '375x667',
                '412x869', '414x896', '768x1024',
            ],
            'maxTouchPoints': [
                0, 1, 2, 5, 10, 15, 20
            ],
        }
    
    def detect_automation(self, browser_info: Dict[str, Any]) -> str:
        """Determine if browser shows signs of automation"""
        
        # Check if WebDriver is detected
        if browser_info.get('webdriver') is True:
            return 'Yes'
        
        # Check userAgent against known patterns
        if browser_info.get('userAgent', '') not in self.known_patterns['userAgent']:
            return 'Yes'
        
        # Check platform
        if browser_info.get('platform') not in self.known_patterns['platform']:
            return 'Yes'
        
        # Check max touch points
        if browser_info.get('maxTouchPoints') not in self.known_patterns['maxTouchPoints']:
            return 'Yes'
        
        # Check for unusual screen resolution
        screen_res = browser_info.get('screenResolution', '0x0')
        screen_width, screen_height = map(int, screen_res.split('x'))
        if screen_width < 500 or screen_height < 500:
            return 'Yes'
        
        # Check for missing required attributes
        required_attrs = ['userAgent', 'pluginsCount', 'languages', 'platform']
        if any(attr not in browser_info for attr in required_attrs):
            return 'Yes'
        
        # Check for bot indicators in user agent
        user_agent = browser_info.get('userAgent', '').lower()
        bot_indicators = ['phantomjs', 'selenium', 'puppeteer', 'crawler', 'curl', 'scrapy', 
                        'wget', 'robot', 'headless']
        if any(indicator in user_agent for indicator in bot_indicators):
            return 'Yes'
        
        # No indicators of automation detected
        return 'No'