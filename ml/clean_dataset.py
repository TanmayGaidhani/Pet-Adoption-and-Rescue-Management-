#!/usr/bin/env python3
"""
Clean and preprocess pet matching dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def clean_dataset(input_file, output_file):
    """Clean and preprocess the pet matching dataset"""
    
    print(f"Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Original dataset shape: {df.shape}")
    
    # Remove duplicates
    df = df.drop_duplicates()
    print(f"After removing duplicates: {df.shape}")
    
    # Handle missing values
    df = df.dropna()
    print(f"After removing null values: {df.shape}")
    
    # Encode categorical variables
    categorical_columns = ['lost_pet_type', 'lost_breed', 'lost_color', 'lost_location',
                          'found_pet_type', 'found_breed', 'found_color', 'found_location']
    
    label_encoders = {}
    for col in categorical_columns:
        le = LabelEncoder()
        df[col + '_encoded'] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Convert dates to numerical features
    df['lost_date'] = pd.to_datetime(df['lost_date'])
    df['found_date'] = pd.to_datetime(df['found_date'])
    df['date_diff'] = (df['found_date'] - df['lost_date']).dt.days
    
    # Create feature columns
    feature_columns = [col + '_encoded' for col in categorical_columns] + ['date_diff']
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    print(f"Cleaned dataset saved to {output_file}")
    
    return df, label_encoders

if __name__ == "__main__":
    clean_dataset('../dataset/pet_match_dataset.csv', '../dataset/pet_match_dataset_clean.csv')