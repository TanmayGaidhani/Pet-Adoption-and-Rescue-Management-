"""
RescueMate Database Seeder
Seeds MongoDB with attractive demo data for:
- Available Adoption Pets
- Rescue Reports
- Found Pets
- Community Comments

Usage:
    python seed_demo_data.py
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import get_db, AdoptionPet, PetReport, Comment, User
from myproject.demo_data import (
    DEMO_ADOPTION_PETS,
    DEMO_RESCUE_REPORTS,
    DEMO_FOUND_PETS,
    DEMO_COMMENTS
)


def seed():
    print("🌱 Connecting to MongoDB...")
    try:
        db = get_db()
        db.command('ping')
        print(" Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("Note: The application will still display all demo data via in-app fallbacks.")
        return False

    print("\n📦 Seeding Adoption Pets...")
    try:
        existing_pets_count = db.adoption_pets.count_documents({})
        print(f"Current adoption pets in DB: {existing_pets_count}")
        if existing_pets_count == 0:
            for pet in DEMO_ADOPTION_PETS:
                pet_doc = dict(pet)
                pet_doc.pop('id', None)
                pet_doc['status'] = 'available'
                pet_doc['created_at'] = datetime.now()
                db.adoption_pets.insert_one(pet_doc)
            print(f" Inserted {len(DEMO_ADOPTION_PETS)} adoption pets!")
        else:
            print("ℹ️ Adoption pets already exist. Skipping.")
    except Exception as e:
        print(f"❌ Error seeding adoption pets: {e}")

    print("\n📦 Seeding Rescue & Found Reports...")
    try:
        existing_reports_count = db.pet_reports.count_documents({})
        print(f"Current pet reports in DB: {existing_reports_count}")
        if existing_reports_count == 0:
            for rep in DEMO_RESCUE_REPORTS:
                rep_doc = dict(rep)
                rep_doc.pop('id', None)
                rep_doc['report_type'] = 'RESCUE'
                rep_doc['status'] = 'approved'
                rep_doc['created_at'] = datetime.now()
                db.pet_reports.insert_one(rep_doc)
            for fnd in DEMO_FOUND_PETS:
                fnd_doc = dict(fnd)
                fnd_doc.pop('id', None)
                fnd_doc['report_type'] = 'FOUND'
                fnd_doc['status'] = 'approved'
                fnd_doc['created_at'] = datetime.now()
                db.pet_reports.insert_one(fnd_doc)
            print(f" Inserted {len(DEMO_RESCUE_REPORTS)} rescue reports and {len(DEMO_FOUND_PETS)} found reports!")
        else:
            print("ℹ️ Pet reports already exist. Skipping.")
    except Exception as e:
        print(f"❌ Error seeding pet reports: {e}")

    print("\n📦 Seeding Community Comments...")
    try:
        existing_comments_count = db.comments.count_documents({})
        print(f"Current comments in DB: {existing_comments_count}")
        if existing_comments_count == 0:
            for comm in DEMO_COMMENTS:
                comm_doc = dict(comm)
                comm_doc.pop('id', None)
                comm_doc.pop('time_ago', None)
                comm_doc['created_at'] = datetime.now()
                db.comments.insert_one(comm_doc)
            print(f" Inserted {len(DEMO_COMMENTS)} community comments!")
        else:
            print("ℹ️ Comments already exist. Skipping.")
    except Exception as e:
        print(f"❌ Error seeding comments: {e}")

    print("\n All demo data seeding completed successfully!")
    return True


if __name__ == '__main__':
    seed()
