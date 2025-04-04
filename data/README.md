# User Interaction Classification System

This project aims to classify user interaction data into human or bot behavior based on three different types of user activities: keystrokes, mouse movements, and scroll behavior. The models are trained using machine learning techniques and extract relevant features from the raw input data to make predictions.

## Table of Contents
1. [Overview](#overview)
2. [Data Description](#data-description)
3. [Feature Extraction](#feature-extraction)
4. [Model Training](#model-training)


## Overview

The project includes three main components:
- **Keystrokes Classification**: Detects whether keystroke patterns are from a human or bot.
- **Mouse Movements Classification**: Determines if mouse movement patterns are human-like or generated by a bot.
- **Scroll Behavior Classification**: Classifies scrolling behavior into human or bot based on various scroll-related features.

Each component involves:
1. Parsing raw data from CSV files.
2. Extracting meaningful features.
3. Training machine learning models for classification.
4. Evaluating the performance and saving the models.
5. Making predictions on new data.


## Data Description

### Keystrokes Data
- Consists of CSV files with timestamped keystroke events.
- Each file contains data such as keypress duration, time between consecutive keypresses, and the key pressed.

### Mouse Movements Data
- Contains timestamped data of mouse pointer movements.
- Each file records the X and Y coordinates, timestamps, and movement types (clicks, drags, etc.).

### Scroll Behavior Data
- Includes timestamped data of scroll events.
- Records the scroll position, speed, and direction over time.

## Feature Extraction

### Keystrokes Features
- **Time difference between consecutive keystrokes**: Measures typing speed variability.
- **Keypress duration**: Duration a key is pressed down.
- **Typing speed variance**: Variability in typing speed.
- **Unique key ratio**: Ratio of distinct keys pressed.

### Mouse Movements Features
- **Time difference between consecutive movements**: Measures movement speed.
- **Euclidean distance between points**: Indicates smoothness of movements.
- **Movement speed and acceleration**: Derived from distance and time differences.
- **Direction changes**: Frequency of changes in movement direction.

### Scroll Behavior Features
- **Total scroll distance**: Cumulative distance scrolled.
- **Scroll speed variance**: Variability in scrolling speed.
- **Direction changes**: Frequency of changes in scrolling direction.
- **Average pause**: Time between consecutive scroll events.

## Model Training

For each classification type, the following steps are taken:
1. **Data Preprocessing**: The raw data is cleaned and relevant features are extracted.
2. **Model Selection**: Multiple classifiers are used, including:
   - **Random Forest Classifier**
   - **Support Vector Machine (SVM)**
   - **Logistic Regression**
   - **K-Nearest Neighbors (KNN)**
3. **Training and Evaluation**: The models are trained on labeled datasets and evaluated using metrics like accuracy, precision, recall, and F1-score.



