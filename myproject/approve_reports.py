#!/usr/bin/env python
"""
Script to approve all pending reports for testing ML matching
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import PetReport

def approve_all_reports():
    print("=== Approving All Pending Reports ===")
    
    try:
        # Get all reports
        all_reports = PetReport.find_all()
        approved_count = 0
        
        for report in all_reports:
            if report.get('status') == 'pending':
                # Approve the report
                PetReport.approve(str(report['_id']))
                approved_count += 1
                print(f"✅ Approved {report.get('report_type', 'Unknown')} report: {report.get('animal_type', 'Unknown')} - {report.get('breed', 'Unknown')}")
        
        print(f"\n🎉 Successfully approved {approved_count} reports!")
        
        # Show updated status
        print("\n=== Updated Status ===")
        lost_approved = len(PetReport.find_approved_by_type('LOST'))
        found_approved = len(PetReport.find_approved_by_type('FOUND'))
        rescue_approved = len(PetReport.find_approved_by_type('RESCUE'))
        
        print(f"LOST reports (approved): {lost_approved}")
        print(f"FOUND reports (approved): {found_approved}")
        print(f"RESCUE reports (approved): {rescue_approved}")
        
        if lost_approved > 0 and found_approved > 0:
            print(f"\n🤖 ML Matching is now ready!")
            print(f"   You can match {lost_approved} LOST reports with {found_approved} FOUND reports")
        elif lost_approved > 0 and rescue_approved > 0:
            print(f"\n⚠️  Note: You have LOST and RESCUE reports.")
            print(f"   For ML matching, you need LOST and FOUND reports.")
            print(f"   RESCUE reports are for animals needing rescue, not lost pets.")
        else:
            print(f"\n⚠️  You need both LOST and FOUND reports for ML matching.")
        
    except Exception as e:
        print(f"❌ Error approving reports: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    approve_all_reports()