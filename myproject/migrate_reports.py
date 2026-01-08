#!/usr/bin/env python
"""
Migration script to convert existing PetFound and Rescue reports to unified PetReport model
Run this script to migrate existing data to the new structure
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import PetFound, Rescue, PetReport

def migrate_reports():
    print("=== Migrating Reports to Unified PetReport Model ===")
    
    migrated_count = 0
    
    try:
        # Migrate PetFound reports to PetReport with type 'FOUND'
        print("\n1. Migrating Found Pet Reports...")
        found_reports = PetFound.find_all()
        
        for report in found_reports:
            # Convert to unified format
            unified_report = {
                'report_type': 'FOUND',
                'user_id': report.get('user_id'),
                'user_name': report.get('user_name'),
                'animal_type': report.get('animal_type'),
                'breed': report.get('breed'),
                'age_estimate': report.get('age_estimate'),
                'gender': report.get('gender'),
                'color': report.get('color'),
                'special_marks': report.get('special_marks', ''),
                'report_date': report.get('report_date'),
                'condition': report.get('condition'),
                'location': report.get('location'),
                'city': report.get('city'),
                'contact_name': report.get('contact_name'),
                'contact_phone': report.get('contact_phone'),
                'contact_email': report.get('contact_email'),
                'description': report.get('description'),
                'urgency': report.get('urgency', 'medium'),
                'additional_notes': report.get('additional_notes', ''),
                'image_path': report.get('image_path', ''),
                'status': report.get('status', 'pending'),
                'created_at': report.get('created_at', datetime.now()),
                'approved_at': report.get('approved_at') if report.get('status') == 'approved' else None
            }
            
            PetReport.create(unified_report)
            migrated_count += 1
        
        print(f"   ✅ Migrated {len(found_reports)} found pet reports")
        
        # Migrate Rescue reports to PetReport with type 'RESCUE'
        print("\n2. Migrating Rescue Reports...")
        rescue_reports = Rescue.find_all()
        
        for report in rescue_reports:
            # Convert to unified format
            unified_report = {
                'report_type': 'RESCUE',
                'user_id': report.get('user_id'),
                'user_name': report.get('user_name'),
                'animal_type': report.get('animal_type'),
                'breed': report.get('breed'),
                'age_estimate': report.get('age_estimate'),
                'gender': report.get('gender'),
                'color': report.get('color'),
                'special_marks': report.get('special_marks', ''),
                'report_date': report.get('report_date'),
                'condition': report.get('condition'),
                'location': report.get('location'),
                'city': report.get('city'),
                'contact_name': report.get('contact_name'),
                'contact_phone': report.get('contact_phone'),
                'contact_email': report.get('contact_email'),
                'description': report.get('description'),
                'urgency': report.get('urgency', 'medium'),
                'additional_notes': report.get('additional_notes', ''),
                'image_path': report.get('image_path', ''),
                'status': report.get('status', 'pending'),
                'created_at': report.get('created_at', datetime.now()),
                'approved_at': report.get('approved_at') if report.get('status') == 'approved' else None
            }
            
            PetReport.create(unified_report)
            migrated_count += 1
        
        print(f"   ✅ Migrated {len(rescue_reports)} rescue reports")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   Total reports migrated: {migrated_count}")
        print(f"   Found reports: {len(found_reports)}")
        print(f"   Rescue reports: {len(rescue_reports)}")
        
        # Note: Original collections are preserved for backup
        print(f"\n📝 Note: Original 'pet_found' and 'rescues' collections are preserved as backup")
        print(f"   New unified reports are stored in 'pet_reports' collection")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

def create_sample_lost_reports():
    """Create some sample LOST pet reports for testing ML matching"""
    print("\n=== Creating Sample Lost Pet Reports ===")
    
    sample_lost_reports = [
        {
            'report_type': 'LOST',
            'user_id': 'sample_user_1',
            'user_name': 'John Doe',
            'animal_type': 'Dog',
            'breed': 'Golden Retriever',
            'age_estimate': '3 years',
            'gender': 'Male',
            'color': 'Golden',
            'special_marks': 'White patch on chest',
            'report_date': '2024-01-15',
            'condition': 'Healthy',
            'location': 'Central Park',
            'city': 'New York',
            'owner_name': 'John Doe',
            'owner_phone': '+1-555-0101',
            'owner_email': 'john.doe@email.com',
            'description': 'Friendly golden retriever, responds to "Max". Last seen near the playground.',
            'urgency': 'high',
            'additional_notes': 'Wearing blue collar with name tag',
            'status': 'approved'
        },
        {
            'report_type': 'LOST',
            'user_id': 'sample_user_2',
            'user_name': 'Sarah Smith',
            'animal_type': 'Cat',
            'breed': 'Persian',
            'age_estimate': '2 years',
            'gender': 'Female',
            'color': 'White',
            'special_marks': 'Blue eyes, fluffy tail',
            'report_date': '2024-01-16',
            'condition': 'Healthy',
            'location': 'Downtown',
            'city': 'New York',
            'owner_name': 'Sarah Smith',
            'owner_phone': '+1-555-0102',
            'owner_email': 'sarah.smith@email.com',
            'description': 'Beautiful white Persian cat, very shy. Escaped through window.',
            'urgency': 'medium',
            'additional_notes': 'Indoor cat, not used to outdoors',
            'status': 'approved'
        },
        {
            'report_type': 'LOST',
            'user_id': 'sample_user_3',
            'user_name': 'Mike Johnson',
            'animal_type': 'Dog',
            'breed': 'Labrador',
            'age_estimate': '5 years',
            'gender': 'Female',
            'color': 'Black',
            'special_marks': 'Scar on left ear',
            'report_date': '2024-01-17',
            'condition': 'Healthy',
            'location': 'Riverside Park',
            'city': 'New York',
            'owner_name': 'Mike Johnson',
            'owner_phone': '+1-555-0103',
            'owner_email': 'mike.johnson@email.com',
            'description': 'Black Labrador, very energetic. Broke free from leash during walk.',
            'urgency': 'high',
            'additional_notes': 'Microchipped, loves tennis balls',
            'status': 'approved'
        }
    ]
    
    created_count = 0
    for report_data in sample_lost_reports:
        report_data['created_at'] = datetime.now()
        PetReport.create(report_data)
        created_count += 1
    
    print(f"   ✅ Created {created_count} sample lost pet reports")
    print(f"   These reports can be used for testing ML matching functionality")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Migrate existing reports to unified model")
    print("2. Create sample lost pet reports for testing")
    print("3. Both")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        migrate_reports()
    elif choice == "2":
        create_sample_lost_reports()
    elif choice == "3":
        migrate_reports()
        create_sample_lost_reports()
    else:
        print("Invalid choice. Exiting.")