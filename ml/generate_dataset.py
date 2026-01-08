#!/usr/bin/env python3
"""
Generate synthetic pet matching dataset for ML training
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_pet_dataset(num_samples=1000):
    """Generate synthetic pet matching dataset"""
    
    # Pet types and breeds
    pet_data = {
        'Dog': ['Labrador', 'Golden Retriever', 'German Shepherd', 'Bulldog', 'Poodle', 'Beagle', 'Rottweiler', 'Yorkshire Terrier'],
        'Cat': ['Persian', 'Siamese', 'Maine Coon', 'British Shorthair', 'Ragdoll', 'Bengal', 'Russian Blue', 'Abyssinian'],
        'Bird': ['Parrot', 'Canary', 'Cockatiel', 'Budgie', 'Finch', 'Lovebird', 'Conure', 'Macaw']
    }
    
    colors = ['Black', 'White', 'Brown', 'Golden', 'Gray', 'Orange', 'Mixed', 'Spotted', 'Striped']
    locations = ['Central Park', 'Brooklyn Bridge', 'Times Square', 'Riverside Park', 'Queens Plaza', 'Bronx Zoo', 'Staten Island', 'Manhattan']
    
    data = []
    
    for i in range(num_samples):
        # Generate lost pet
        pet_type = random.choice(list(pet_data.keys()))
        breed = random.choice(pet_data[pet_type])
        color = random.choice(colors)
        location = random.choice(locations)
        
        # Generate found pet (with some probability of match)
        is_match = random.random() < 0.3  # 30% chance of match
        
        if is_match:
            # Generate matching found pet with some variations
            found_type = pet_type
            found_breed = breed if random.random() < 0.8 else random.choice(pet_data[pet_type])
            found_color = color if random.random() < 0.9 else random.choice(colors)
            found_location = location if random.random() < 0.7 else random.choice(locations)
            match_label = 1
        else:
            # Generate non-matching found pet
            found_type = random.choice(list(pet_data.keys()))
            found_breed = random.choice(pet_data[found_type])
            found_color = random.choice(colors)
            found_location = random.choice(locations)
            match_label = 0
        
        # Generate dates
        lost_date = datetime.now() - timedelta(days=random.randint(1, 30))
        found_date = lost_date + timedelta(days=random.randint(0, 10))
        
        data.append({
            'lost_pet_type': pet_type,
            'lost_breed': breed,
            'lost_color': color,
            'lost_location': location,
            'lost_date': lost_date.strftime('%Y-%m-%d'),
            'found_pet_type': found_type,
            'found_breed': found_breed,
            'found_color': found_color,
            'found_location': found_location,
            'found_date': found_date.strftime('%Y-%m-%d'),
            'match': match_label
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating pet matching dataset...")
    df = generate_pet_dataset(1000)
    
    # Create dataset directory if it doesn't exist
    import os
    os.makedirs('../dataset', exist_ok=True)
    
    df.to_csv('../dataset/pet_match_dataset.csv', index=False)
    print(f"Generated {len(df)} samples and saved to ../dataset/pet_match_dataset.csv")