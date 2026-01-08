#!/usr/bin/env python3
"""
Feature extraction for pet matching ML model
"""

import os
from ml.image_similarity import image_similarity

def extract_features(lost_report, found_report):
    """
    Extract features from lost and found pet reports for ML model.
    
    Args:
        lost_report (dict): Lost pet report data
        found_report (dict): Found pet report data
    
    Returns:
        list: Feature vector for ML model
    """
    
    features = []
    
    # 1. Pet type match (binary: 1 if same, 0 if different)
    pet_type_match = 1 if lost_report.get("animal_type", "").lower() == found_report.get("animal_type", "").lower() else 0
    features.append(pet_type_match)
    
    # 2. Breed match (binary: 1 if same, 0 if different)
    breed_match = 1 if lost_report.get("breed", "").lower() == found_report.get("breed", "").lower() else 0
    features.append(breed_match)
    
    # 3. Color match (binary: 1 if same, 0 if different)
    color_match = 1 if lost_report.get("color", "").lower() == found_report.get("color", "").lower() else 0
    features.append(color_match)
    
    # 4. Location proximity (simplified: 1 if same city, 0.5 if nearby, 0 if different)
    lost_location = lost_report.get("location", "").lower()
    found_location = found_report.get("location", "").lower()
    
    if lost_location == found_location:
        location_score = 1.0
    elif any(word in found_location for word in lost_location.split()) or any(word in lost_location for word in found_location.split()):
        location_score = 0.5
    else:
        location_score = 0.0
    
    features.append(location_score)
    
    # 5. Date difference (days between lost and found dates)
    try:
        from datetime import datetime
        lost_date = datetime.strptime(lost_report.get("report_date", ""), "%Y-%m-%d")
        found_date = datetime.strptime(found_report.get("report_date", ""), "%Y-%m-%d")
        date_diff = abs((found_date - lost_date).days)
    except:
        date_diff = 30  # Default to 30 days if date parsing fails
    
    features.append(date_diff)
    
    # 6. Image similarity score (0–1)
    image_sim = image_similarity(
        lost_report["image_path"],
        found_report["image_path"]
    )
    features.append(image_sim)
    
    return features

def get_feature_names():
    """
    Get the names of features returned by extract_features.
    
    Returns:
        list: List of feature names
    """
    return [
        'pet_type_match',
        'breed_match', 
        'color_match',
        'location_score',
        'date_diff',
        'image_similarity'
    ]