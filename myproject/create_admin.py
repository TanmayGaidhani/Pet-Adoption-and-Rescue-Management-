#!/usr/bin/env python
"""
Script to create admin users in the database
Run this script to add admin users manually
"""

import os
import sys
import django
from django.contrib.auth.hashers import make_password

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import User

def create_admin():
    print("=== Create Admin User ===")
    
    fullname = input("Enter admin full name: ")
    email = input("Enter admin email: ")
    phone = input("Enter admin phone: ")
    password = input("Enter admin password: ")
    
    # Check if user already exists
    if User.exists(email):
        print(f"❌ User with email {email} already exists!")
        return
    
    # Create admin user
    try:
        hashed_password = make_password(password)
        admin_id = User.create_admin(fullname, email, phone, hashed_password)
        print(f"✅ Admin user created successfully!")
        print(f"Admin ID: {admin_id}")
        print(f"Email: {email}")
        print(f"You can now login as admin using these credentials.")
    except Exception as e:
        print(f"❌ Error creating admin: {str(e)}")

if __name__ == "__main__":
    create_admin()