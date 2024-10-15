import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Function to extract features from raw scroll data
def extract_features(df):
    # Scroll distance: difference in position between consecutive scroll events
    df['scroll_distance'] = df['position'].diff().fillna(0).abs()

    # Scroll speed variance: variance of speed values
    scroll_speed_variance = df['speed'].var()

    # Direction changes: when the position change direction (up or down)
    df['direction_change'] = np.sign(df['position'].diff())
    direction_changes = df['direction_change'].diff().fillna(0).abs().sum()

    # Pauses between scrolls: time difference between consecutive scroll events
    df['pause'] = df['timestamp'].diff().fillna(0)
    average_pause = df['pause'].mean()

    # Summarize the features for the entire scroll session
    features = {
        'total_scroll_distance': df['scroll_distance'].sum(),
        'scroll_speed_variance': scroll_speed_variance,
        'direction_changes': direction_changes,
        'average_pause': average_pause
    }

    return features

# Function to process all datasets and extract features
def process_datasets(human_files, bot_files):
    all_data = []

    # Process human datasets
    for file in human_files:
        df = pd.read_csv(file)
        features = extract_features(df)
        features['is_human'] = 1  # Label humans as 1
        all_data.append(features)

    # Process bot datasets
    for file in bot_files:
        df = pd.read_csv(file)
        features = extract_features(df)
        features['is_human'] = 0  # Label bots as 0
        all_data.append(features)

    # Return a DataFrame with all combined data
    return pd.DataFrame(all_data)

# List of CSV files for humans and bots
human_files = [
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\human\\human 1.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\human\\human 2.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\human\\human 3.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\human\\human 4.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\human\\human 5.csv'
]
bot_files = [
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\bot\\bot_1_constant_speed.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\bot\\bot_2_accelerating.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\bot\\bot_3_decelerating.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\bot\\bot_4_random_jumps.csv',
    'E:\\Projects\\SIH\\Demo\\Scroll Movement\\dataset\\bot\\bot_5_pauses.csv'
]

# Extract features and labels from datasets
data = process_datasets(human_files, bot_files)

# Features (X) and Labels (y)
X = data[['total_scroll_distance', 'scroll_speed_variance', 'direction_changes', 'average_pause']]
y = data['is_human']

# Define multiple classifiers
classifiers = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Support Vector Machine": make_pipeline(StandardScaler(), SVC()),
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression()),
    "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3))
}

# Train all classifiers
trained_models = {}
for name, model in classifiers.items():
    model.fit(X, y)
    trained_models[name] = model
    print(f"{name} has been trained successfully.")


# Function to load the models and make predictions on new data
def predict_user_from_csv(file_path, trained_models):
    # Load and extract features from the new CSV file
    df = pd.read_csv(file_path)
    features = extract_features(df)
    
    # Convert the features to a DataFrame for prediction
    input_data = pd.DataFrame([features])

    # Predict whether the user is human or bot using each classifier
    predictions = {}
    for name, model in trained_models.items():
        prediction = model.predict(input_data)
        predictions[name] = 'Human' if prediction == 1 else 'Bot'
        print(f"The overall prediction for '{file_path}' using {name} is: {predictions[name]}")
    
    return predictions

# Example usage with a new CSV file
result = predict_user_from_csv('scroll_data.csv', trained_models)
print(result)
