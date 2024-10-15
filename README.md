# Smart Captcha API

This FastAPI-based application detects if interactions with a website are coming from a human or a bot, based on mouse and keyboard behavior. It also uses browser information and device fingerprints to assess if the client is automated or previously blacklisted.

## Features

- **Mouse and Keyboard Behavior Analysis**: The API uses pre-trained models to predict if the interaction is from a human or a bot based on mouse and keyboard movement patterns.
- **Browser Automation Detection**: By analyzing browser data, the system checks for anomalies in `userAgent`, platform, and other properties to determine if the browser is automated.
- **Device Fingerprinting**: The system logs device fingerprints to Firebase Realtime Database and flags devices as bots if they make frequent requests.
- **Firebase Realtime Database**: Stores visit information, device fingerprints, and bot statuses using Firebase's real-time database.

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Firebase Admin SDK
- Joblib
- Pandas
- NumPy

### Python Packages

Install the following packages using `pip`:

```bash
pip install fastapi uvicorn firebase-admin joblib pandas numpy
```

## Setup

1. **Start the Server**:
   - Run the FastAPI server using Uvicorn:
   
   ```bash
   uvicorn main:app --reload
   ```

   This will start the API server locally at `http://127.0.0.1:8000`.

## API Endpoints

### `/predict_behavior` (POST)
Predicts if the user behavior comes from a human or a bot based on mouse, keyboard interactions, and browser information.

#### Parameters:
- `mouse_file`: CSV file containing mouse movement data (`x`, `y`, `timestamp`).
- `key_file`: CSV file containing keyboard event data (`fieldName`, `timestamp`).
- `browser_info`: JSON string of browser details (e.g., userAgent, platform, etc.).
- `fingerprint`: String representing the device fingerprint.

#### Response:
```json
{
  "mouse_result": "Human" or "Bot",
  "key_result": "Human" or "Bot",
  "is_automated": "Yes" or "No",
  "is_bot": "Yes" or "No"
}
```

### `/add_visit_info` (POST)
Logs visit information based on a device fingerprint and timestamp.

#### Parameters:
- `fingerprint`: String representing the device fingerprint.
- `timestamp`: Integer representing the time in milliseconds.

#### Response:
```json
{
  "message": "Fingerprint and visit info saved successfully!",
  "timestamp": <timestamp>,
  "fingerprint": <fingerprint>
}
```

## Models

The API uses two machine learning models:
1. `MouseVerifier.pkl`: Detects if mouse movements are human or bot-controlled.
2. `KeyboardVerifier.pkl`: Detects if keyboard inputs are from a human or a bot.

Ensure these models are stored in the project directory.

## Running the Application

To run the application locally:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

You can then access the API at `http://127.0.0.1:8000`.

## Example Usage

To test the `/predict_behavior` endpoint, use a tool like `curl` or Postman to send a POST request with the required files and form data.

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/predict_behavior" \
-F "mouse_file=@path/to/mouse_data.csv" \
-F "key_file=@path/to/key_data.csv" \
-F "browser_info={\"userAgent\": \"Mozilla/5.0 ...\", \"platform\": \"Win32\", ...}" \
-F "fingerprint=abc123"
```

---

This README should guide users on how to set up, run, and test the application.
