#!/usr/bin/env python3
"""
Image similarity calculation for pet matching
"""

import cv2
import numpy as np

def image_similarity(img1_path, img2_path):
    """
    Calculate similarity between two images.
    Returns a score between 0 (completely different) and 1 (identical).
    """
    
    try:
        # Handle empty or None paths
        if not img1_path or not img2_path:
            return 0.0
        
        # Load images
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        
        # Check if images loaded successfully
        if img1 is None or img2 is None:
            return 0.0
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Resize images to same size for comparison
        height, width = 100, 100
        gray1 = cv2.resize(gray1, (width, height))
        gray2 = cv2.resize(gray2, (width, height))
        
        # Calculate histogram correlation
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        
        # Normalize histograms
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        
        # Calculate correlation
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # Ensure result is between 0 and 1
        similarity = max(0.0, min(1.0, correlation))
        
        return similarity
        
    except Exception as e:
        print(f"Error calculating image similarity: {str(e)}")
        return 0.0

def calculate_structural_similarity(img1_path, img2_path):
    """
    Calculate structural similarity using SSIM (requires scikit-image)
    """
    try:
        from skimage.metrics import structural_similarity as ssim
        
        # Load and preprocess images
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        
        if img1 is None or img2 is None:
            return 0.0
        
        # Resize to same dimensions
        height, width = 100, 100
        img1 = cv2.resize(img1, (width, height))
        img2 = cv2.resize(img2, (width, height))
        
        # Calculate SSIM
        similarity = ssim(img1, img2)
        
        return max(0.0, min(1.0, similarity))
        
    except ImportError:
        # Fall back to histogram correlation if scikit-image not available
        return image_similarity(img1_path, img2_path)
    except Exception as e:
        print(f"Error calculating structural similarity: {str(e)}")
        return 0.0