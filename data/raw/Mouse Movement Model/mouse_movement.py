#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings(action='ignore')


# In[7]:


# Function to parse the dataset
def parse_data(file_path):
    data = pd.read_csv(file_path)
    # Convert timestamp to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data


# In[8]:


# Load datasets
data_human = parse_data("human.csv")
data_bot = parse_data("bot.csv")


# In[9]:


# Function to extract features
def extract_features(data):
    # Calculate the time difference between consecutive movements in milliseconds
    data['time_diff'] = data['timestamp'].diff().dt.total_seconds().fillna(0) * 1000
    
    # Calculate the Euclidean distance between consecutive points
    data['distance'] = np.sqrt((data['x'].diff()**2) + (data['y'].diff()**2)).fillna(0)
    
    # Calculate the speed (distance/time)
    data['speed'] = data['distance'] / data['time_diff'].replace(0, np.nan).fillna(0)
    
    # Calculate the direction of movement
    data['direction'] = np.arctan2(data['y'].diff(), data['x'].diff()).fillna(0)
    
    # Optional: Calculate curvature between three consecutive points
    data['curvature'] = data['direction'].diff().fillna(0)
    
    return data[['time_diff', 'distance', 'speed', 'direction', 'curvature']]


# In[10]:


# Prepare features and labels
features_human = extract_features(data_human)
features_bot = extract_features(data_bot)

features_human['label'] = 0  # Human label
features_bot['label'] = 1    # Bot label


# In[11]:


# Combine the datasets
dataset = pd.concat([features_human, features_bot]).reset_index(drop=True)

X = dataset.drop('label', axis=1).dropna()
y = dataset['label'][X.index]


# In[12]:


# Define multiple classifiers
classifiers = {
    "Random Forest": RandomForestClassifier(),
    "Support Vector Machine": make_pipeline(StandardScaler(), SVC()),
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression()),
    "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1)) 
}


# In[13]:


# Train all classifiers
trained_models = {}
for name, model in classifiers.items():
    model.fit(X, y)
    trained_models[name] = model
    print(f"{name} has been trained successfully.")


# In[18]:


# Function to predict new data using all models
def predict_new_data(file_path, trained_models):
    # Parse the new data file
    new_data = parse_data(file_path)
    
    # Extract features from the new data
    features_new_data = extract_features(new_data).dropna()
    
    predictions = {}
    for name, model in trained_models.items():
        # Predict using the trained model
        preds = model.predict(features_new_data)
        
        # Count the predictions
        human_count = (preds == 0).sum()
        bot_count = (preds == 1).sum()
        
        # Majority voting to determine overall classification
        overall_prediction = "Human" if human_count > bot_count else "Bot"
        predictions[name] = overall_prediction
        print(f"The overall prediction for '{file_path}' using {name} is: {overall_prediction}")
    
    # return predictions


# In[19]:


file_path = "human_test.csv"  # Replace with your actual file path
prediction = predict_new_data(file_path, trained_models)
# print(f"The overall prediction for the file '{file_path}' is: {prediction}")


# In[21]:


file_path = "bot_test.csv"  # Replace with your actual file path
prediction = predict_new_data(file_path, trained_models)
# print(f"The overall prediction for the file '{file_path}' is: {prediction}")


# In[ ]:




