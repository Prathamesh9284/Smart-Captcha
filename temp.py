import time
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import joblib
from io import BytesIO
import collections
import json
import firebase_admin
from firebase_admin import credentials, db
import asyncio

# Firebase Admin SDK setup
cred = credentials.Certificate("D:\API\sihp-2135d-firebase-adminsdk-p2uhe-2490ca71b7.json")  # Path to your Firebase service account JSON file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sihp-2135d-default-rtdb.firebaseio.com/'
})

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Load models
mouse_model = joblib.load(r'artifacts/serialized/models/MouseVerifier.pkl')
key_model = joblib.load(r'artifacts/serialized/models/KeyboardVerifier.pkl')

known_patterns = {
    'userAgent': [
        # Common user agents for popular browsers
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',  # Safari on macOS
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',  # Firefox on Ubuntu
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',  # Safari on iPhone
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.67',  # Edge on Windows
        'Mozilla/5.0 (Linux; Android 11; SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',  # Chrome on Android
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',  # Safari on iPad
    ],
    'webdriver': [
        False  # Expected webdriver status for non-automated browsers
    ],
    'platform': [
        'Win32', 'Win64', 'MacIntel', 'Linux x86_64', 'iPhone', 'iPad', 'Android', 'Linux armv7l',
        'Linux armv8l', 'Linux aarch64',
        'Linux i686', 'Linux x86',
    ],
    'screenResolution': [
        '1920x1080', '1366x768', '1440x900', '1536x864', '1600x900', '1280x720', '2560x1440', '1536x864',
        '3840x2160', '2560x1600', '2880x1800',
        '320x480', '360x640', '375x667',
        '412x869', '414x896', '768x1024',
    ],
    'maxTouchPoints': [
        0, 1, 2, 5, 10, 15, 20
    ],
}


def mouse_prediction(data):
    # Ensure proper data types
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    
    # Handle NaT in timestamps
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
    
    # Replace inf values and drop rows with NaN
    # data.replace([np.inf, -np.inf], np.nan, inplace=True)
    # data.dropna(inplace=True)
    
    # Prediction
    if data.empty:
        return "Error: No valid data for prediction"

    try:
        predictions = mouse_model.predict(data)
    except Exception as e:
        return f"Prediction error: {e}"

    human_count = (predictions == 0).sum()
    bot_count = (predictions == 1).sum()
    overall_prediction = "Human" if human_count > bot_count else "Bot"

    return overall_prediction

def key_prediction(data):
    # Convert timestamps
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Calculate time differences
    data['time_diff'] = data.groupby('fieldName')['timestamp'].diff().dt.total_seconds().fillna(0)
    
    # Aggregate features
    features = data.groupby('fieldName')['time_diff'].agg(['mean', 'std', 'min', 'max']).reset_index()

    # Flatten features
    features = features.drop('fieldName', axis=1).values.flatten()

    # Prediction
    prediction = key_model.predict([features])
    
    return 'Bot' if prediction[0] == 1 else 'Human'


def determine_if_automated(browser_info):
    # Check if WebDriver is detected (used by many automation tools)
    if browser_info.get('webdriver') is True:
        print('webdriver')
        return 'Yes'

    # Check userAgent against known patterns
    if browser_info.get('userAgent', '') not in known_patterns['userAgent']:
        print(browser_info.get('userAgent'))
        print('useragent')
        return 'Yes'

    # Check platform
    if browser_info.get('platform') not in known_patterns['platform']:
        print('platform')
        return 'Yes'

    # Check max touch points
    if browser_info.get('maxTouchPoints') not in known_patterns['maxTouchPoints']:
        print('maxtouchpoints')
        return 'Yes'

    # Check for an unusually high or low screen resolution
    screen_width, screen_height = map(int, browser_info.get('screenResolution', '0x0').split('x'))
    if screen_width < 500 or screen_height < 500:  # Example threshold, can be adjusted
        print('screenwidth')
        return 'Yes'

    # Check if the user agent has missing or unusual properties
    if 'missingProperty' in browser_info.get('userAgent', ''):
        print('missingProperty')
        return 'Yes'

    # Check for missing or unusual attributes that are typically present in a real browser
    required_attrs = ['userAgent', 'pluginsCount', 'languages', 'platform']
    if any(attr not in browser_info for attr in required_attrs):
        print('requiredAttr')
        return 'Yes'

    # Check for userAgent inconsistencies or known bot identifiers
    user_agent = browser_info.get('userAgent', '').lower()
    bot_indicators = ['phantomjs', 'selenium', 'puppeteer', 'crawler', 'curl', 'scrapy', 'wget', 'robot', 'headless']
    if any(bot_indicator in user_agent for bot_indicator in bot_indicators):
        print('Bot detected')
        return 'Yes'

    # Check if the browser is running in headless mode (common for bots)
    if 'headless' in user_agent:
        print('Bot detected')
        return 'Yes'

    return 'No'

async def is_bot(fingerprint):
    try:
        # Reference to the 'bots' node in Firebase Realtime Database
        bots_ref = db.reference('bots')

        # Query the database to check if the fingerprint is in the 'bots' node
        snapshot = await asyncio.to_thread(bots_ref.child(fingerprint).get)
        
        # If the snapshot exists and is not empty, the fingerprint is a bot
        if snapshot:
            return 'Yes'
        else:
            return 'No'
            
    except Exception as e:
        print(f"Error checking bot status: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/predict_behavior")
async def predict_behavior(
    mouse_file: UploadFile = File(...),
    key_file: UploadFile = File(...),
    browser_info: str = Form(...),
    fingerprint: str = Form(...)
):
#     try:
        # Read the uploaded files
    mouse_data = await mouse_file.read()
    key_data = await key_file.read()

    # Convert the files into DataFrames
    mouse = pd.read_csv(BytesIO(mouse_data))
    key = pd.read_csv(BytesIO(key_data))

    # Convert browser_info JSON string to dictionary
    browser_info_dict = json.loads(browser_info)

    # Perform predictions
    mouse_result = await asyncio.to_thread(mouse_prediction, mouse)
    key_result = await asyncio.to_thread(key_prediction, key)
    is_automated = await asyncio.to_thread(determine_if_automated, browser_info_dict)
    bot = await is_bot(fingerprint)
    print('Mouse is controlled by : ',mouse_result)
    print('Keyboard is controlled by :',key_result)
    print('Malicious Browser found ? :',is_automated)
    print('Is device fingerprint blacklisted ? : ',bot)
    # Return results as a JSON response
    return JSONResponse(content={
    'mouse_result': mouse_result,
    'key_result': key_result,
    'is_automated': is_automated,
    'is_bot': bot
    })

    # except Exception as e:
    #     return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post('/add_visit_info')
async def add_visit_info(
    fingerprint: str = Form(...),
    timestamp: int = Form(...)
):
    try:
        # Get the current timestamp in milliseconds
        timestamp = int(time.time() * 1000)

        # Save fingerprint and timestamp to Firebase Realtime Database
        fingerprint_ref = db.reference(f'fingerprints/{fingerprint}')
        new_visit_ref = fingerprint_ref.push()
        await asyncio.to_thread(new_visit_ref.set, {
            'timestamp': timestamp,
            'fingerprint': fingerprint
        })

        recent_entries_count = await check_recent_entries(fingerprint)
        
        if recent_entries_count > 15:
            bots_ref = db.reference(f'bots')
            await asyncio.to_thread(bots_ref.set, {
                fingerprint: fingerprint
            })

        return JSONResponse(content={
            'message': 'Fingerprint and visit info saved successfully!',
            'timestamp': timestamp,
            'fingerprint': fingerprint
        })
        
    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)

async def check_recent_entries(fingerprint):
    thirty_seconds_ago = int(time.time() * 1000) - 30000  # 30 seconds ago in milliseconds

    # Reference to the database path for this fingerprint
    fingerprint_ref = db.reference(f'fingerprints/{fingerprint}')

    # Create a query to get entries from the last 30 seconds
    query = fingerprint_ref.order_by_child('timestamp').start_at(thirty_seconds_ago)

    try:
        # Retrieve the entries
        snapshot = await asyncio.to_thread(query.get)
        if snapshot:
            # Count the number of entries
            entries = snapshot
            count = len(entries)
            print(f'Number of entries with the same fingerprint in the last 30 seconds: {count}')
            return count
        else:
            print('No recent entries found.')
            return 0
            
    except Exception as error:
        print('Error retrieving data from database:', error)
        return 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


