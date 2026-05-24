#!/usr/bin/env python
"""
Script to create a demo user in MongoDB Atlas
Run: python create_demo_user.py
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from myproject.models import User

def create_demo_user():
    email = "demouser@rescuemate.com"
    password = "Demo@1234"

    if User.exists(email):
        print(f"✅ Demo user already exists: {email}")
        return

    User.create(
        fullname="Demo User",
        email=email,
        phone="9876543210",
        password=make_password(password),
        is_admin=False
    )
    print(f"✅ Demo user created!")
    print(f"   Email: {email}")
    print(f"   Password: {password}")

if __name__ == "__main__":
    create_demo_user()
