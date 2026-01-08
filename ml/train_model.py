#!/usr/bin/env python3
"""
Train machine learning model for pet matching
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def train_pet_matching_model():
    """Train a Random Forest model for pet matching"""
    
    # Load cleaned dataset
    print("Loading cleaned dataset...")
    df = pd.read_csv('../dataset/pet_match_dataset_clean.csv')
    
    # Define features
    feature_columns = [
        'lost_pet_type_encoded', 'lost_breed_encoded', 'lost_color_encoded', 'lost_location_encoded',
        'found_pet_type_encoded', 'found_breed_encoded', 'found_color_encoded', 'found_location_encoded',
        'date_diff'
    ]
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['match']
    
    print(f"Dataset shape: {X.shape}")
    print(f"Positive matches: {y.sum()} ({y.mean():.2%})")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train Random Forest model
    print("Training Random Forest model...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    rf_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save the model
    os.makedirs('../saved_models', exist_ok=True)
    model_path = '../saved_models/pet_match_rf.pkl'
    joblib.dump(rf_model, model_path)
    print(f"\nModel saved to {model_path}")
    
    return rf_model, feature_importance

if __name__ == "__main__":
    model, importance = train_pet_matching_model()