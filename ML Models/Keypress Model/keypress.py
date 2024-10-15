import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Load datasets
human_data = pd.read_csv('human.csv')
bot_data = pd.read_csv('bot.csv')

# Function to extract features
def extract_features(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['time_diff'] = data.groupby('fieldName')['timestamp'].diff().dt.total_seconds().fillna(0)

    # Aggregate features for each field
    features = data.groupby('fieldName')['time_diff'].agg(['mean', 'std', 'min', 'max']).reset_index()
    return features.drop('fieldName', axis=1).values.flatten()

# Prepare the data
human_features = extract_features(human_data)
bot_features = extract_features(bot_data)

X = []
y = []

X.append(human_features)
y.append(0)  # Label for human

X.append(bot_features)
y.append(1)  # Label for bot

X = pd.DataFrame(X)
y = pd.Series(y)

# List of classifiers to compare
classifiers = {
    "Random Forest": RandomForestClassifier(),
    "Support Vector Machine": make_pipeline(StandardScaler(), SVC()),
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression()),
    "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))  
}


# Train all classifiers on the entire dataset
trained_models = {}
for name, model in classifiers.items():
    model.fit(X, y)
    trained_models[name] = model
    print(f"{name} has been trained successfully.")

# Predict for a new dataset using all models and display the results
def classify_new_data(file_path, trained_models):
    new_data = pd.read_csv(file_path)
    new_features = extract_features(new_data)
    predictions = {}
    for name, model in trained_models.items():
        prediction = model.predict([new_features])
        predictions[name] = 'Bot' if prediction[0] == 1 else 'Human'
        print(f"The given file is classified as: {predictions[name]} using {name}")
    return predictions

# Example usage
file_to_classify = 'bot_test.csv'
classify_new_data(file_to_classify, trained_models)

file_to_classify = 'human_test.csv'
classify_new_data(file_to_classify, trained_models)
