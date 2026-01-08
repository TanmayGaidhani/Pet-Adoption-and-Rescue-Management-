from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from .models import User, Rescue, PetFound, Comment, ChatMessage, PetReport, AdoptionPet, MatchResult, Notification, db
from bson import ObjectId
import random
import json
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def index(request):
    return render(request, "index.html")


@never_cache
def signup(request):
    # If already logged in, redirect to dashboard
    if "user_id" in request.session:
        return redirect("dashboard")
    
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmPassword")

        if not all([fullname, email, phone, password, confirmPassword]):
            messages.error(request, "All fields are required!")
            return redirect("signup")

        if password != confirmPassword:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.exists(email):
            messages.error(request, "Email already registered!")
            return redirect("signup")

        # ----------- OTP VERIFICATION PART -----------
        entered_otp = "".join([request.POST.get(f"otp_{i}", "") for i in range(6)])
        session_otp = request.session.get("otp")
        otp_timestamp = request.session.get("otp_timestamp")

        # Check if OTP exists and is not expired (10 minutes = 600 seconds)
        if not session_otp or not otp_timestamp:
            messages.error(request, "OTP not found. Please request a new OTP.")
            return redirect("signup")
        
        current_time = datetime.now().timestamp()
        if current_time - otp_timestamp > 600:  # 10 minutes
            messages.error(request, "OTP has expired. Please request a new OTP.")
            request.session.pop('otp', None)
            request.session.pop('otp_timestamp', None)
            return redirect("signup")

        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP!")
            return redirect("signup")
        # ----------------------------------------------

        hashed_password = make_password(password)
        User.create(fullname=fullname, email=email, phone=phone, password=hashed_password)

        # Clear OTP from session
        request.session.pop('otp', None)
        request.session.pop('otp_timestamp', None)
        
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    response = render(request, "signup.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# otp sneder
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"success": False, "message": "Email is required!"})

        otp = random.randint(100000, 999999)
        request.session["otp"] = str(otp)
        request.session["otp_timestamp"] = datetime.now().timestamp()  # Store OTP creation time

        try:
            result = send_mail(
                subject="Your OTP Verification Code - RescueMate",
                message=f"Hello!\n\nYour OTP verification code is: {otp}\n\nThis code will expire in 10 minutes.\n\nThank you for joining RescueMate - Pet Adoption & Rescue Portal!\n\nBest regards,\nRescueMate Team",
                from_email="RescueMate - Pet Adoption & Rescue Portal <s23_gaidhani_tanmay@mgmcen.ac.in>",
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": f"OTP sent to {email}"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Failed to send email: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request"})

# LOGIN FUNCTION
@never_cache
def login_view(request):
    # If already logged in, redirect to appropriate dashboard
    if "user_id" in request.session:
        if request.session.get("is_admin"):
            return redirect("admin_dashboard")
        else:
            return redirect("dashboard")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.find_by_email(email)

        if user:
            if check_password(password, user['password']):
                # Clear any existing session data
                request.session.flush()
                # Create new session
                request.session["user_id"] = str(user['_id'])
                request.session["user_name"] = user['fullname']
                request.session["is_admin"] = user.get('is_admin', False)
                request.session.set_expiry(1200)  # Session expires in 20 hour
                
                # Redirect based on user type
                if user.get('is_admin', False):
                    messages.success(request, f"Welcome Admin {user['fullname']}!")
                    return redirect("admin_dashboard")
                else:
                    messages.success(request, f"Welcome {user['fullname']}!")
                    return redirect("dashboard")
            else:
                messages.error(request, "Invalid password!")
        else:
            messages.error(request, "User does not exist!")

    response = render(request, "login.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# DASHBOARD
@never_cache
def dashboard(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")

    response = render(request, "dashboard.html", {"user_name": request.session.get("user_name")})
    # Prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# LOGOUT
@never_cache
def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    response = redirect("index")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# RESCUE REPORT
@never_cache
def rescue_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    # Get user details for auto-population
    user_id = request.session.get('user_id')
    user = User.get_by_id(user_id)
    user_phone = user.get('phone', '') if user else ''
    user_email = user.get('email', '') if user else ''
    user_name = request.session.get('user_name', '')
    
    if request.method == "POST":
        report_type = request.POST.get('reportType')  # 'found' or 'rescue'
        
        # Get logged-in user details
        user_id = request.session.get('user_id')
        user_name = request.session.get('user_name')
        
        # Get user's contact details from database
        user = User.get_by_id(user_id)
        user_email = user.get('email', '') if user else ''
        user_phone = user.get('phone', '') if user else ''
        
        # Get form data with auto-populated user details
        report_data = {
            'user_id': user_id,
            'user_name': user_name,
            'animal_type': request.POST.get('animalType'),
            'breed': request.POST.get('breed'),
            'age_estimate': request.POST.get('ageEstimate'),
            'gender': request.POST.get('gender'),
            'color': request.POST.get('color'),
            'special_marks': request.POST.get('specialMarks', ''),
            'report_date': request.POST.get('reportDate'),
            'condition': request.POST.get('condition'),
            'location': request.POST.get('location'),
            'city': request.POST.get('city'),
            'contact_name': user_name,  # Auto-populate from logged-in user
            'contact_phone': user_phone,  # Auto-populate from logged-in user
            'contact_email': user_email,  # Auto-populate from logged-in user
            'description': request.POST.get('description'),
            'urgency': request.POST.get('urgency'),
            'additional_notes': request.POST.get('additionalNotes', ''),
        }
        
        # Add report type
        if report_type == 'found':
            report_data['report_type'] = 'FOUND'
        elif report_type == 'rescue':
            report_data['report_type'] = 'RESCUE'
        
        # Handle file upload
        if 'animalImage' in request.FILES:
            animal_image = request.FILES['animalImage']
            
            # Choose folder based on report type
            folder_name = 'pet_found' if report_type == 'found' else 'rescues'
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_name))
            
            # Create unique filename
            import uuid
            ext = animal_image.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            
            # Save file
            saved_filename = fs.save(filename, animal_image)
            report_data['image_path'] = f"{folder_name}/{saved_filename}"
        
        # Save to unified PetReport collection
        try:
            if report_type == 'found':
                PetReport.create(report_data)
                messages.success(request, "Pet Found report submitted successfully! It will be reviewed by our admin team and published once approved.")
            elif report_type == 'rescue':
                PetReport.create(report_data)
                messages.success(request, "Animal Rescue report submitted successfully! It will be reviewed by our admin team and published once approved.")
            else:
                messages.error(request, "Invalid report type selected!")
                return redirect("rescue")
            
            return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Error submitting report: {str(e)}")
    
    response = render(request, "rescue.html", {
        'user_name': user_name,
        'user_phone': user_phone,
        'user_email': user_email
    })
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# PET REPORT (Lost/Missing Pet) - DEPRECATED: Now using RESCUE reports as LOST reports
@never_cache
def pet_report_view(request):
    """
    DEPRECATED: This function is no longer used.
    RESCUE reports are now treated as LOST reports in the ML matching system.
    Redirect users to the rescue report form instead.
    """
    messages.info(request, "Lost pet reports are now handled through the Rescue Report form.")
    return redirect("rescue")


# FOUND PET PAGE
@never_cache
def found_pet_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    response = render(request, "found_pet.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to get found pets data
@never_cache
def get_found_pets_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        # Get only approved FOUND pet reports from unified collection
        found_pets = PetReport.find_approved_by_type('FOUND')
        
        # Convert to JSON-serializable format
        pets_data = []
        for pet in found_pets:
            pet_data = {
                'id': str(pet['_id']),
                'animal_type': pet.get('animal_type', ''),
                'breed': pet.get('breed', ''),
                'color': pet.get('color', ''),
                'gender': pet.get('gender', ''),
                'location': pet.get('location', ''),
                'city': pet.get('city', ''),
                'report_date': pet.get('report_date', ''),
                'description': pet.get('description', ''),
                'contact_name': pet.get('contact_name', ''),
                'contact_phone': pet.get('contact_phone', ''),
                'contact_email': pet.get('contact_email', ''),
                'special_marks': pet.get('special_marks', ''),
                'condition': pet.get('condition', ''),
                'urgency': pet.get('urgency', ''),
                'image_path': pet.get('image_path', ''),
                'created_at': pet.get('created_at', '').strftime('%Y-%m-%d') if pet.get('created_at') else ''
            }
            pets_data.append(pet_data)
        
        return JsonResponse({"pets": pets_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# REPORT INFO PAGE
@never_cache
def report_info_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    response = render(request, "report_info.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to get rescue reports data
@never_cache
def get_rescue_reports_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        # Get only approved RESCUE reports from unified collection
        rescue_reports = PetReport.find_approved_by_type('RESCUE')
        
        # Convert to JSON-serializable format
        reports_data = []
        for report in rescue_reports:
            report_data = {
                'id': str(report['_id']),
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'gender': report.get('gender', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'report_date': report.get('report_date', ''),
                'description': report.get('description', ''),
                'contact_name': report.get('contact_name', ''),
                'contact_phone': report.get('contact_phone', ''),
                'contact_email': report.get('contact_email', ''),
                'special_marks': report.get('special_marks', ''),
                'condition': report.get('condition', ''),
                'urgency': report.get('urgency', ''),
                'image_path': report.get('image_path', ''),
                'additional_notes': report.get('additional_notes', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d') if report.get('created_at') else ''
            }
            reports_data.append(report_data)
        
        return JsonResponse({"reports": reports_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ADMIN DASHBOARD
@never_cache
def admin_dashboard_view(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_dashboard.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# ADMIN USERS PAGE
@never_cache
def admin_users_view(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_users.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# ADMIN REPORTS PAGE
@never_cache
def admin_reports_view(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_reports.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API for admin dashboard stats
@never_cache
def admin_stats_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Count users
        total_users = len(User.find_all_users())
        
        # Count found pets from unified collection
        found_pets = len(PetReport.find_by_type('FOUND'))
        
        # Count rescue reports from unified collection
        rescue_reports = len(PetReport.find_by_type('RESCUE'))
        
        # Count active reports (found pets + rescue reports)
        active_reports = found_pets + rescue_reports
        
        return JsonResponse({
            "total_users": total_users,
            "found_pets": found_pets,
            "rescue_reports": rescue_reports,
            "active_reports": active_reports
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to get pending reports for admin
@never_cache
def admin_pending_reports_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all pending reports from unified collection
        pending_reports = PetReport.find_pending()
        
        found_data = []
        rescue_data = []
        
        for report in pending_reports:
            report_data = {
                'id': str(report['_id']),
                'type': report.get('report_type', '').lower(),  # 'FOUND' -> 'found', 'RESCUE' -> 'rescue'
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'contact_name': report.get('contact_name', ''),
                'contact_phone': report.get('contact_phone', ''),
                'contact_email': report.get('contact_email', ''),
                'description': report.get('description', ''),
                'special_marks': report.get('special_marks', ''),
                'condition': report.get('condition', ''),
                'urgency': report.get('urgency', ''),
                'report_date': report.get('report_date', ''),
                'image_path': report.get('image_path', ''),
                'additional_notes': report.get('additional_notes', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d') if report.get('created_at') else ''
            }
            
            # Separate by report type
            if report.get('report_type') == 'FOUND':
                found_data.append(report_data)
            elif report.get('report_type') == 'RESCUE':
                rescue_data.append(report_data)
        
        return JsonResponse({
            "found_pets": found_data,
            "rescue_reports": rescue_data
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to approve/reject reports
@never_cache
def admin_approve_report_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        report_id = data.get('report_id')
        report_type = data.get('report_type')  # 'found' or 'rescue'
        action = data.get('action')  # 'approve' or 'reject'
        
        if not all([report_id, report_type, action]):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        # Get the report from unified collection
        report = PetReport.find_by_id(report_id)
        
        if not report:
            return JsonResponse({"error": "Report not found"}, status=404)
        
        # Verify report type matches
        expected_type = 'FOUND' if report_type == 'found' else 'RESCUE'
        if report.get('report_type') != expected_type:
            return JsonResponse({"error": "Report type mismatch"}, status=400)
        
        user_id = report.get('user_id')
        user_name = report.get('user_name', 'User')
        contact_email = report.get('contact_email', '')
        animal_type = report.get('animal_type', 'Pet')
        breed = report.get('breed', 'Unknown')
        location = report.get('location', 'Unknown location')
        
        # Get user email if not in report
        if not contact_email and user_id:
            user = User.get_by_id(user_id)
            if user:
                contact_email = user.get('email', '')
                user_name = user.get('fullname', user_name)
        
        # Perform the action using unified PetReport methods
        if action == 'approve':
            result = PetReport.approve(report_id)
        elif action == 'reject':
            result = PetReport.reject(report_id)
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
        
        # Send notifications and emails
        if action == 'approve':
            if result.modified_count > 0:
                # Create notification
                title = f"Report Approved ✅"
                message = f"Your {report_type} report for {animal_type} ({breed}) in {location} has been approved and is now visible to the community."
                
                if user_id:
                    create_notification(user_id, title, message, 'report_approved', {
                        'report_id': report_id,
                        'report_type': report_type,
                        'animal_type': animal_type
                    })
                
                # Send email notification
                if contact_email:
                    email_message = f"""Great news! Your {report_type} report has been approved.

Report Details:
- Animal: {animal_type} ({breed})
- Location: {location}
- Status: Approved and Published

Your report is now visible to the community and will help connect pets with their families or find them new homes.

Thank you for helping animals in need!"""
                    
                    send_notification_email(contact_email, user_name, title, email_message)
                
                return JsonResponse({"success": True, "message": f"Report approved successfully and user notified"})
            else:
                return JsonResponse({"error": "Report not found or already processed"}, status=404)
                
        elif action == 'reject':
            if result.modified_count > 0:
                # Create notification
                title = f"Report Not Approved ❌"
                message = f"Your {report_type} report for {animal_type} ({breed}) could not be approved. Please ensure all information is accurate and complete."
                
                if user_id:
                    create_notification(user_id, title, message, 'report_rejected', {
                        'report_id': report_id,
                        'report_type': report_type,
                        'animal_type': animal_type
                    })
                
                # Send email notification
                if contact_email:
                    email_message = f"""We're sorry, but your {report_type} report could not be approved at this time.

Report Details:
- Animal: {animal_type} ({breed})
- Location: {location}
- Status: Not Approved

Common reasons for rejection:
- Incomplete information
- Poor quality images
- Duplicate reports
- Inappropriate content

You can submit a new report with complete and accurate information. If you have questions, please contact our support team.

Thank you for your understanding."""
                    
                    send_notification_email(contact_email, user_name, title, email_message)
                
                return JsonResponse({"success": True, "message": f"Report rejected and user notified"})
            else:
                return JsonResponse({"error": "Report not found or already processed"}, status=404)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API for admin users stats
@never_cache
def admin_users_stats_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all users
        all_users = User.find_all_users()
        
        # Count total users
        total_users = len(all_users)
        
        # Count active users (assuming users with recent activity)
        active_users = len([user for user in all_users if user.get('is_active', True)])
        
        # Count admin users
        admin_users = len([user for user in all_users if user.get('is_admin', False)])
        
        # Count new users (last 30 days) - placeholder for now
        new_users = 0  # You can implement date-based filtering here
        
        return JsonResponse({
            "total_users": total_users,
            "active_users": active_users,
            "new_users": new_users,
            "admin_users": admin_users
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to get all users for admin
@never_cache
def admin_users_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all users
        all_users = User.find_all_users()
        users_data = []
        
        for user in all_users:
            user_data = {
                'id': str(user.get('_id', '')),
                'username': user.get('fullname', 'Unknown'),
                'email': user.get('email', ''),
                'first_name': user.get('fullname', '').split(' ')[0] if user.get('fullname') else '',
                'last_name': ' '.join(user.get('fullname', '').split(' ')[1:]) if user.get('fullname') and len(user.get('fullname', '').split(' ')) > 1 else '',
                'phone': user.get('phone', ''),
                'is_active': user.get('is_active', True),
                'is_staff': user.get('is_admin', False),
                'is_superuser': user.get('is_admin', False),
                'date_joined': user.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if user.get('created_at') else '',
                'last_login': user.get('last_login', '').strftime('%Y-%m-%d %H:%M:%S') if user.get('last_login') else None
            }
            users_data.append(user_data)
        
        return JsonResponse({"users": users_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# API to delete a user (admin only)
@never_cache
@csrf_exempt
def admin_delete_user_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != 'DELETE':
        return JsonResponse({"error": "Only DELETE method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id_to_delete = data.get('user_id')
        
        if not user_id_to_delete:
            return JsonResponse({"error": "User ID is required"}, status=400)
        
        # Prevent admin from deleting themselves
        current_admin_id = request.session.get("user_id")
        if str(user_id_to_delete) == str(current_admin_id):
            return JsonResponse({"error": "Cannot delete your own account"}, status=400)
        
        # Check if user exists
        user_to_delete = User.get_by_id(user_id_to_delete)
        if not user_to_delete:
            return JsonResponse({"error": "User not found"}, status=404)
        
        # Prevent deletion of other admin users
        if user_to_delete.get('is_admin', False):
            return JsonResponse({"error": "Cannot delete admin users"}, status=400)
        
        # Delete user and all related data
        from bson import ObjectId
        user_obj_id = ObjectId(user_id_to_delete)
        
        # Delete user's reports and related data
        PetReport.delete_by_user(user_id_to_delete)
        Comment.delete_by_user(user_id_to_delete)
        ChatMessage.delete_by_user(user_id_to_delete)
        Notification.delete_by_user_id(user_id_to_delete)
        
        # Delete the user
        result = User.delete_by_id(user_id_to_delete)
        
        if result.deleted_count > 0:
            return JsonResponse({"success": True, "message": "User deleted successfully"})
        else:
            return JsonResponse({"error": "Failed to delete user"}, status=500)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ===== AI CHATBOT API WITH GOOGLE GEMINI =====
from google import genai
from google.genai import types
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat_api(request):
    """
    API endpoint for AI chatbot - Simple fallback version
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip().lower()
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        # Simple rule-based responses for pet-related questions
        pet_responses = {
            # Greetings
            'hello': "Hello! 🐾 I'm PetCare AI, your friendly assistant for all pet and animal questions. How can I help you today?",
            'hi': "Hi there! 🐕 I'm here to help with any pet-related questions you have. What would you like to know?",
            'hey': "Hey! 🐱 Welcome to PetCare AI. I'm ready to help with all your animal and pet questions!",
            
            # Dogs
            'dog': "Dogs are wonderful companions! 🐕 They need daily exercise, proper nutrition, and lots of love. What specific question do you have about dogs?",
            'puppy': "Puppies are adorable! 🐶 They need frequent meals, lots of sleep, socialization, and basic training. Start with house training and simple commands!",
            'dog training': "Dog training requires patience and consistency! 🎾 Start with basic commands like sit, stay, and come. Use positive reinforcement with treats and praise.",
            'dog food': "Good dog food should have meat as the first ingredient! 🍖 Feed puppies 3-4 times daily, adult dogs twice daily. Avoid chocolate, grapes, and onions!",
            'dog exercise': "Dogs need daily exercise! 🏃‍♂️ Most dogs need 30 minutes to 2 hours depending on breed. Walking, playing fetch, and running are great activities.",
            'dog name': "Great dog names include Max, Bella, Charlie, Lucy, Cooper, and Daisy! 🐕 Choose something easy to say and that fits your dog's personality.",
            
            # Cats
            'cat': "Cats are amazing pets! 🐱 They're independent but still need care, proper food, and regular vet checkups. What would you like to know about cats?",
            'kitten': "Kittens are so cute! 😸 They need kitten-specific food, litter box training, and lots of play time. Socialize them early for friendly adult cats!",
            'cat food': "Cats are obligate carnivores! 🐟 They need high-protein food with taurine. Feed kittens 3-4 times daily, adult cats twice daily.",
            'litter box': "Keep litter boxes clean! 🧹 Scoop daily, change weekly. Have one box per cat plus one extra. Place in quiet, accessible locations.",
            'cat behavior': "Cats communicate through body language! 🐾 Purring means contentment, tail up means happy, and slow blinks mean 'I love you'!",
            
            # Birds
            'bird': "Birds make wonderful pets! 🐦 They need spacious cages, social interaction, and species-appropriate diets. What bird questions do you have?",
            'parrot': "Parrots are intelligent and social! 🦜 They need mental stimulation, social interaction, and can live 20-80+ years depending on species.",
            'bird cage': "Bird cages should be spacious! 🏠 Width is more important than height. Include perches of different sizes and safe toys for enrichment.",
            
            # Fish
            'fish': "Fish are peaceful pets! 🐠 They need proper water conditions, appropriate tank size, and regular feeding. What fish topic interests you?",
            'aquarium': "Aquariums need proper filtration and cycling! 🐟 Test water regularly, maintain proper temperature, and don't overcrowd your tank.",
            'goldfish': "Goldfish need more space than people think! 🐠 A single goldfish needs at least 20 gallons. They can live 10-30 years with proper care!",
            
            # Small Animals
            'rabbit': "Rabbits are gentle pets! 🐰 They need hay, fresh vegetables, pellets, and space to hop around. They can be litter trained too!",
            'hamster': "Hamsters are cute small pets! 🐹 They need proper bedding, exercise wheels, and hiding spots. They're mostly nocturnal animals.",
            'guinea pig': "Guinea pigs are social animals! 🐹 They need vitamin C in their diet, spacious cages, and do best in pairs or groups.",
            
            # General Care
            'food': "Pet nutrition is very important! 🍽️ Always choose high-quality food appropriate for your pet's age and size. Avoid chocolate, grapes, and onions for dogs and cats.",
            'health': "Pet health is crucial! 🏥 Regular vet checkups, vaccinations, and watching for changes in behavior are key. For serious concerns, always consult a veterinarian.",
            'vet': "Regular vet visits are essential! 👩‍⚕️ Annual checkups for healthy adults, more frequent for puppies/kittens and senior pets. Don't delay if you notice health changes!",
            'vaccination': "Vaccinations protect your pets! 💉 Core vaccines for dogs include rabies, DHPP. For cats: rabies, FVRCP. Follow your vet's schedule.",
            'grooming': "Regular grooming keeps pets healthy! ✂️ Brush regularly, trim nails, clean ears, and bathe as needed. Professional grooming helps too!",
            
            # Training & Behavior
            'training': "Pet training requires patience and consistency! 🎾 Use positive reinforcement, start with basic commands, and keep sessions short and fun.",
            'behavior': "Understanding pet behavior helps! 🧠 Watch body language, provide mental stimulation, and address problems early with positive methods.",
            'socialization': "Early socialization is key! 👥 Expose young pets to different people, animals, and environments safely to build confidence.",
            
            # Adoption & Rescue
            'adoption': "Pet adoption is wonderful! 🏠 Consider your lifestyle, living space, and time commitment. Visit local shelters and spend time with potential pets.",
            'rescue': "Pet rescue is so important! 🚨 If you find a stray or injured animal, contact local animal control or rescue organizations immediately.",
            'shelter': "Animal shelters do amazing work! 🏠 They provide care, medical treatment, and help match pets with loving families. Consider adopting!",
            
            # Emergency & Safety
            'emergency': "Pet emergencies need immediate attention! 🚨 Contact your vet or emergency clinic right away. Keep their number handy at all times!",
            'poison': "If your pet ate something toxic, call your vet immediately! ☎️ Common toxins include chocolate, grapes, onions, and certain plants.",
            'first aid': "Basic pet first aid is helpful! 🩹 Learn how to check vital signs, handle minor cuts, and when to seek emergency care.",
            
            # General Help
            'help': "I can help with pet care, health, nutrition, training, adoption, and rescue topics! 🐾 Just ask me anything about animals and pets.",
            'tips': "Here are some quick pet tips! 💡 Fresh water daily, regular exercise, mental stimulation, routine vet care, and lots of love!",
            'care': "Good pet care includes proper nutrition, exercise, medical care, grooming, and emotional needs! 💕 What specific care topic interests you?"
        }
        
        # Check for keywords in user message
        response = None
        
        # First check for exact matches
        for keyword, reply in pet_responses.items():
            if keyword == user_message:
                response = reply
                break
        
        # If no exact match, check for partial matches
        if not response:
            for keyword, reply in pet_responses.items():
                if keyword in user_message:
                    response = reply
                    break
        
        # Check for common variations and synonyms
        if not response:
            if any(word in user_message for word in ['puppy', 'puppies']):
                response = pet_responses.get('puppy', pet_responses['dog'])
            elif any(word in user_message for word in ['kitten', 'kittens']):
                response = pet_responses.get('kitten', pet_responses['cat'])
            elif any(word in user_message for word in ['name', 'names', 'naming']):
                if 'dog' in user_message:
                    response = pet_responses['dog name']
                else:
                    response = "Choosing a good pet name is fun! 🐾 Pick something easy to say, that fits their personality, and that you'll love calling for years to come!"
            elif any(word in user_message for word in ['train', 'training', 'teach']):
                response = pet_responses['training']
            elif any(word in user_message for word in ['feed', 'feeding', 'eat', 'eating']):
                response = pet_responses['food']
            elif any(word in user_message for word in ['sick', 'ill', 'disease', 'medicine']):
                response = pet_responses['health']
            elif any(word in user_message for word in ['adopt', 'adopting', 'adoption']):
                response = pet_responses['adoption']
            elif any(word in user_message for word in ['exercise', 'walk', 'walking', 'play', 'playing']):
                if 'dog' in user_message:
                    response = pet_responses['dog exercise']
                else:
                    response = "Regular exercise is important for pets! 🏃‍♂️ Dogs need daily walks and playtime. Cats enjoy interactive toys and climbing. Match activity to your pet's energy level!"
            elif any(word in user_message for word in ['cage', 'house', 'home', 'habitat']):
                if 'bird' in user_message:
                    response = pet_responses['bird cage']
                else:
                    response = "Proper housing is essential! 🏠 Pets need safe, comfortable spaces appropriate for their size and species. Ensure good ventilation and easy cleaning!"
        
        # Default responses
        if not response:
            if any(word in user_message for word in ['pet', 'animal', 'dog', 'cat', 'bird', 'fish', 'rabbit', 'hamster']):
                response = "I'd love to help with your pet question! 🐾 Try asking about specific topics like 'dog training', 'cat food', 'bird care', 'fish tank', or 'pet health'. What would you like to know?"
            else:
                response = "I'm sorry, but I can only answer questions related to pets and animals. 🐾 Please ask me about pet care, animal health, training, nutrition, or any animal-related topics!"
        
        # Save the chat message to database
        if "user_id" in request.session:
            try:
                user_id = request.session.get('user_id')
                user_name = request.session.get('user_name', 'Anonymous')
                ChatMessage.create(user_id, user_name, user_message, response)
            except Exception as e:
                print(f"Error saving chat message: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'response': response
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': 'I apologize, but I\'m having technical difficulties. Please try asking a simple pet-related question.'
        }, status=500)


# ===== ADOPTION SYSTEM VIEWS =====

# ADOPTION PAGE - User side to browse pets
@never_cache
def adoption_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    # Get user details for auto-population
    user_id = request.session.get('user_id')
    user = User.get_by_id(user_id)
    user_phone = user.get('phone', '') if user else ''
    user_email = user.get('email', '') if user else ''
    user_name = request.session.get('user_name', '')
    
    response = render(request, "adoption.html", {
        'user_name': user_name,
        'user_phone': user_phone,
        'user_email': user_email
    })
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to get available pets for adoption
@never_cache
def get_adoption_pets_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        from .models import AdoptionPet
        # Get only available pets for adoption
        available_pets = AdoptionPet.find_available()
        
        # Convert to JSON-serializable format
        pets_data = []
        for pet in available_pets:
            pet_data = {
                'id': str(pet['_id']),
                'name': pet.get('name', ''),
                'animal_type': pet.get('animal_type', ''),
                'breed': pet.get('breed', ''),
                'age': pet.get('age', ''),
                'gender': pet.get('gender', ''),
                'color': pet.get('color', ''),
                'size': pet.get('size', ''),
                'personality': pet.get('personality', ''),
                'health_status': pet.get('health_status', ''),
                'vaccination_status': pet.get('vaccination_status', ''),
                'spayed_neutered': pet.get('spayed_neutered', ''),
                'good_with_kids': pet.get('good_with_kids', ''),
                'good_with_pets': pet.get('good_with_pets', ''),
                'energy_level': pet.get('energy_level', ''),
                'description': pet.get('description', ''),
                'special_needs': pet.get('special_needs', ''),
                'adoption_fee': pet.get('adoption_fee', ''),
                'contact_info': pet.get('contact_info', ''),
                'image_path': pet.get('image_path', ''),
                'created_at': pet.get('created_at', '').strftime('%Y-%m-%d') if pet.get('created_at') else ''
            }
            pets_data.append(pet_data)
        
        return JsonResponse({"pets": pets_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to submit adoption request
@never_cache
def submit_adoption_request_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        from .models import AdoptionRequest, AdoptionPet
        
        data = json.loads(request.body)
        pet_id = data.get('pet_id')
        
        # Check if pet exists and is available
        pet = AdoptionPet.find_by_id(pet_id)
        if not pet:
            return JsonResponse({"error": "Pet not found"}, status=404)
        
        if pet.get('status') != 'available':
            return JsonResponse({"error": "Pet is no longer available for adoption"}, status=400)
        
        # Check if user already has a pending request for this pet
        user_id = request.session.get('user_id')
        existing_requests = AdoptionRequest.find_by_user_id(user_id)
        for existing_request in existing_requests:
            if (existing_request.get('pet_id') == pet_id and 
                existing_request.get('status') == 'pending'):
                return JsonResponse({"error": "You already have a pending request for this pet"}, status=400)
        
        # Create adoption request
        request_data = {
            'user_id': user_id,
            'user_name': request.session.get('user_name'),
            'pet_id': pet_id,
            'pet_name': pet.get('name', ''),
            'applicant_name': data.get('applicant_name'),
            'applicant_email': data.get('applicant_email'),
            'applicant_phone': data.get('applicant_phone'),
            'address': data.get('address'),
            'housing_type': data.get('housing_type'),
            'has_yard': data.get('has_yard'),
            'other_pets': data.get('other_pets'),
            'experience_with_pets': data.get('experience_with_pets'),
            'reason_for_adoption': data.get('reason_for_adoption'),
            'availability': data.get('availability'),
            'references': data.get('references', ''),
            'additional_info': data.get('additional_info', '')
        }
        
        AdoptionRequest.create(request_data)
        
        return JsonResponse({
            "success": True, 
            "message": "Adoption request submitted successfully! We'll contact you soon."
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ADMIN ADOPTION MANAGEMENT
@never_cache
def admin_adoption_view(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_adoption.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to add new pet for adoption (admin only)
@never_cache
def admin_add_adoption_pet_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        from .models import AdoptionPet
        
        # Get form data
        pet_data = {
            'name': request.POST.get('name'),
            'animal_type': request.POST.get('animal_type'),
            'breed': request.POST.get('breed'),
            'age': request.POST.get('age'),
            'gender': request.POST.get('gender'),
            'color': request.POST.get('color'),
            'size': request.POST.get('size'),
            'personality': request.POST.get('personality'),
            'health_status': request.POST.get('health_status'),
            'vaccination_status': request.POST.get('vaccination_status'),
            'spayed_neutered': request.POST.get('spayed_neutered'),
            'good_with_kids': request.POST.get('good_with_kids'),
            'good_with_pets': request.POST.get('good_with_pets'),
            'energy_level': request.POST.get('energy_level'),
            'description': request.POST.get('description'),
            'special_needs': request.POST.get('special_needs', ''),
            'adoption_fee': request.POST.get('adoption_fee'),
            'contact_info': request.POST.get('contact_info'),
            'added_by': request.session.get('user_name')
        }
        
        # Handle file upload
        if 'pet_image' in request.FILES:
            pet_image = request.FILES['pet_image']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'adoption_pets'))
            
            # Create unique filename
            import uuid
            ext = pet_image.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            
            # Save file
            saved_filename = fs.save(filename, pet_image)
            pet_data['image_path'] = f"adoption_pets/{saved_filename}"
        
        AdoptionPet.create(pet_data)
        
        return JsonResponse({
            "success": True, 
            "message": "Pet added for adoption successfully!"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to get all adoption pets (admin)
@never_cache
def admin_adoption_pets_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        from .models import AdoptionPet
        all_pets = AdoptionPet.find_all()
        
        pets_data = []
        for pet in all_pets:
            pet_data = {
                'id': str(pet['_id']),
                'name': pet.get('name', ''),
                'animal_type': pet.get('animal_type', ''),
                'breed': pet.get('breed', ''),
                'age': pet.get('age', ''),
                'gender': pet.get('gender', ''),
                'status': pet.get('status', ''),
                'adoption_fee': pet.get('adoption_fee', ''),
                'image_path': pet.get('image_path', ''),
                'created_at': pet.get('created_at', '').strftime('%Y-%m-%d') if pet.get('created_at') else ''
            }
            pets_data.append(pet_data)
        
        return JsonResponse({"pets": pets_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to get adoption requests (admin)
@never_cache
def admin_adoption_requests_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        from .models import AdoptionRequest
        all_requests = AdoptionRequest.find_pending()
        
        requests_data = []
        for req in all_requests:
            request_data = {
                'id': str(req['_id']),
                'pet_id': req.get('pet_id', ''),
                'pet_name': req.get('pet_name', ''),
                'applicant_name': req.get('applicant_name', ''),
                'applicant_email': req.get('applicant_email', ''),
                'applicant_phone': req.get('applicant_phone', ''),
                'address': req.get('address', ''),
                'housing_type': req.get('housing_type', ''),
                'reason_for_adoption': req.get('reason_for_adoption', ''),
                'experience_with_pets': req.get('experience_with_pets', ''),
                'status': req.get('status', ''),
                'created_at': req.get('created_at', '').strftime('%Y-%m-%d') if req.get('created_at') else ''
            }
            requests_data.append(request_data)
        
        return JsonResponse({"requests": requests_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to approve/reject adoption request (admin)
@never_cache
def admin_adoption_action_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        from .models import AdoptionRequest, AdoptionPet
        
        data = json.loads(request.body)
        request_id = data.get('request_id')
        action = data.get('action')  # 'approve' or 'reject'
        
        if not all([request_id, action]):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        # Get the adoption request
        adoption_request = AdoptionRequest.find_by_id(request_id)
        if not adoption_request:
            return JsonResponse({"error": "Adoption request not found"}, status=404)
        
        user_id = adoption_request.get('user_id')
        user_name = adoption_request.get('user_name', 'User')
        pet_name = adoption_request.get('pet_name', 'Pet')
        applicant_email = adoption_request.get('applicant_email', '')
        
        # Get user email if not in request
        if not applicant_email and user_id:
            user = User.get_by_id(user_id)
            if user:
                applicant_email = user.get('email', '')
                user_name = user.get('fullname', user_name)
        
        if action == 'approve':
            # Approve the request
            result = AdoptionRequest.approve(request_id)
            
            # Mark the pet as adopted
            pet_id = adoption_request.get('pet_id')
            if pet_id:
                AdoptionPet.update_status(pet_id, 'adopted')
            
            # Create notification
            if user_id:
                title = f"Adoption Request Approved ✅"
                message = f"Great news! Your adoption request for {pet_name} has been approved. We'll contact you soon with next steps."
                
                create_notification(user_id, title, message, 'adoption_approved', {
                    'request_id': request_id,
                    'pet_name': pet_name
                })
            
            # Send email notification
            if applicant_email:
                email_message = f"""Congratulations! Your adoption request has been approved.

Pet Details:
- Pet Name: {pet_name}
- Status: Approved for Adoption

Next Steps:
Our team will contact you within 24-48 hours to arrange the adoption process, including:
- Meet and greet with {pet_name}
- Final paperwork completion
- Adoption fee payment
- Pet pickup arrangements

Thank you for choosing to adopt and giving {pet_name} a loving home!"""
                
                send_notification_email(applicant_email, user_name, title, email_message)
            
            return JsonResponse({"success": True, "message": "Adoption request approved successfully and user notified!"})
            
        elif action == 'reject':
            # Reject the request
            result = AdoptionRequest.reject(request_id)
            
            # Create notification
            if user_id:
                title = f"Adoption Request Update ❌"
                message = f"We're sorry, but your adoption request for {pet_name} could not be approved at this time. Please consider other available pets."
                
                create_notification(user_id, title, message, 'adoption_rejected', {
                    'request_id': request_id,
                    'pet_name': pet_name
                })
            
            # Send email notification
            if applicant_email:
                email_message = f"""Thank you for your interest in adopting {pet_name}.

Unfortunately, we cannot approve your adoption request at this time. This could be due to:
- Another application was selected
- Specific requirements not met
- Pet is no longer available

We encourage you to:
- Browse other available pets on our platform
- Submit applications for other pets you're interested in
- Contact us if you have questions about the decision

Thank you for your understanding and continued support of animal rescue."""
                
                send_notification_email(applicant_email, user_name, title, email_message)
            
            return JsonResponse({"success": True, "message": "Adoption request rejected and user notified."})
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ===== VIEW UPDATES PAGE =====

# View Updates - User can see all their requests status
@never_cache
def view_updates_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    response = render(request, "view_updates.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# ===== COMMUNITY COMMENTS PAGE =====

# Community Comments - Dedicated page for community discussions
@never_cache
def community_comments_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    response = render(request, "community_comments.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to get user's requests status
@never_cache
def get_user_requests_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user_id = request.session.get('user_id')
        
        # Get adoption requests
        from .models import AdoptionRequest
        adoption_requests = AdoptionRequest.find_by_user_id(user_id)
        adoption_data = []
        for req in adoption_requests:
            request_data = {
                'id': str(req['_id']),
                'type': 'adoption',
                'title': f"Adoption Request - {req.get('pet_name', 'Pet')}",
                'description': f"Request to adopt {req.get('pet_name', 'a pet')}",
                'status': req.get('status', 'pending'),
                'created_at': req.get('created_at', '').strftime('%Y-%m-%d %H:%M') if req.get('created_at') else '',
                'details': {
                    'pet_name': req.get('pet_name', ''),
                    'applicant_name': req.get('applicant_name', ''),
                    'applicant_email': req.get('applicant_email', ''),
                    'applicant_phone': req.get('applicant_phone', ''),
                    'housing_type': req.get('housing_type', ''),
                    'reason_for_adoption': req.get('reason_for_adoption', '')
                }
            }
            adoption_data.append(request_data)
        
        # Get all user reports from unified collection
        user_reports = []
        all_reports = PetReport.find_all()
        for report in all_reports:
            if report.get('user_id') == user_id:
                report_type = report.get('report_type', '').lower()
                report_data = {
                    'id': str(report['_id']),
                    'type': 'rescue' if report_type == 'rescue' else 'found_pet',
                    'title': f"{report_type.title()} Report - {report.get('animal_type', 'Animal')}",
                    'description': f"{report_type.title()} {report.get('animal_type', 'animal')} in {report.get('location', 'unknown location')}",
                    'status': report.get('status', 'pending'),
                    'created_at': report.get('created_at', '').strftime('%Y-%m-%d %H:%M') if report.get('created_at') else '',
                    'details': {
                        'animal_type': report.get('animal_type', ''),
                        'breed': report.get('breed', ''),
                        'location': report.get('location', ''),
                        'city': report.get('city', ''),
                        'condition': report.get('condition', ''),
                        'urgency': report.get('urgency', ''),
                        'color': report.get('color', ''),
                        'description': report.get('description', ''),
                        'additional_notes': report.get('additional_notes', '')
                    }
                }
                user_reports.append(report_data)
        
        # Combine all requests and sort by date
        all_requests = adoption_data + user_reports
        all_requests.sort(key=lambda x: x['created_at'], reverse=True)
        
        return JsonResponse({
            "requests": all_requests,
            "total_count": len(all_requests),
            "pending_count": len([r for r in all_requests if r['status'] == 'pending']),
            "approved_count": len([r for r in all_requests if r['status'] == 'approved']),
            "rejected_count": len([r for r in all_requests if r['status'] == 'rejected'])
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ===== COMMENT SYSTEM VIEWS =====

# API to get all comments
@never_cache
def get_comments_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        comments = Comment.find_all(limit=50)
        
        comments_data = []
        for comment in comments:
            comment_data = {
                'id': str(comment['_id']),
                'user_name': comment.get('user_name', 'Anonymous'),
                'message': comment.get('message', ''),
                'created_at': comment.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if comment.get('created_at') else '',
                'time_ago': get_time_ago(comment.get('created_at')) if comment.get('created_at') else ''
            }
            comments_data.append(comment_data)
        
        return JsonResponse({"comments": comments_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to post a new comment
@never_cache
@csrf_exempt
def post_comment_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)
        
        if len(message) > 500:
            return JsonResponse({"error": "Message too long (max 500 characters)"}, status=400)
        
        user_id = request.session.get('user_id')
        user_name = request.session.get('user_name')
        
        Comment.create(user_id, user_name, message)
        
        return JsonResponse({
            "success": True, 
            "message": "Comment posted successfully!"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Helper function to calculate time ago (moved to avoid duplication)


# ===== ADMIN ML MATCHING SYSTEM =====

# Admin ML Matching Dashboard
@never_cache
def admin_ml_matching_view(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_ml_matching.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# API to get lost and found reports for ML matching
@never_cache
def admin_get_reports_for_matching_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        from .models import PetReport
        
        # Get approved RESCUE reports (treating them as LOST reports)
        lost_reports = PetReport.find_approved_by_type('RESCUE')
        lost_data = []
        for report in lost_reports:
            report_data = {
                'id': str(report['_id']),
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'report_date': report.get('report_date', ''),
                'contact_name': report.get('contact_name', ''),  # Use contact info from rescue report
                'contact_email': report.get('contact_email', ''),
                'contact_phone': report.get('contact_phone', ''),
                'description': report.get('description', ''),
                'image_path': report.get('image_path', ''),
                'condition': report.get('condition', ''),
                'urgency': report.get('urgency', ''),
                'special_marks': report.get('special_marks', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d') if report.get('created_at') else ''
            }
            lost_data.append(report_data)
        
        # Get approved FOUND reports
        found_reports = PetReport.find_approved_by_type('FOUND')
        found_data = []
        for report in found_reports:
            report_data = {
                'id': str(report['_id']),
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'report_date': report.get('report_date', ''),
                'finder_name': report.get('contact_name', ''),
                'finder_email': report.get('contact_email', ''),
                'finder_phone': report.get('contact_phone', ''),
                'description': report.get('description', ''),
                'image_path': report.get('image_path', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d') if report.get('created_at') else ''
            }
            found_data.append(report_data)
        
        response = JsonResponse({
            "lost_reports": lost_data,
            "found_reports": found_data
        })
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to run ML matching between specific lost and found reports
@never_cache
def admin_run_ml_match_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        from .models import PetReport, MatchResult
        
        data = json.loads(request.body)
        lost_report_id = data.get('lost_report_id')
        found_report_id = data.get('found_report_id')
        
        if not all([lost_report_id, found_report_id]):
            return JsonResponse({"error": "Both lost_report_id and found_report_id are required"}, status=400)
        
        # Get the reports (RESCUE report treated as LOST, FOUND report as FOUND)
        lost_report = PetReport.find_by_id(lost_report_id)  # This is actually a RESCUE report
        found_report = PetReport.find_by_id(found_report_id)
        
        if not lost_report or not found_report:
            return JsonResponse({"error": "One or both reports not found"}, status=404)
        
        # EMBEDDED MATCHING LOGIC - NO EXTERNAL IMPORTS
        score = 0.0
        max_score = 5.0
        
        # Pet type match (most important)
        lost_type = str(lost_report.get('animal_type', '')).lower().strip()
        found_type = str(found_report.get('animal_type', '')).lower().strip()
        if lost_type == found_type:
            score += 2.0
        
        # Breed match
        lost_breed = str(lost_report.get('breed', '')).lower().strip()
        found_breed = str(found_report.get('breed', '')).lower().strip()
        if lost_breed == found_breed:
            score += 1.5
        
        # Color match
        lost_color = str(lost_report.get('color', '')).lower().strip()
        found_color = str(found_report.get('color', '')).lower().strip()
        if lost_color == found_color:
            score += 1.0
        
        # Location proximity (simplified)
        lost_city = str(lost_report.get('city', '')).lower().strip()
        found_city = str(found_report.get('city', '')).lower().strip()
        if lost_city == found_city:
            score += 0.5
        
        probability = round(score / max_score, 3)
        
        if probability >= 0.8:
            match_strength = 'STRONG'
            recommendation = 'Strong match - Verify and notify pet owners'
        elif probability >= 0.5:
            match_strength = 'MEDIUM'
            recommendation = 'Medium match - Manual verification recommended'
        else:
            match_strength = 'WEAK'
            recommendation = 'Low match - Consider other options'
        
        # Create feature analysis
        feature_analysis = {
            'pet_type_match': {
                'value': 1 if lost_type == found_type else 0,
                'description': f"Pet type: {lost_report.get('animal_type', 'Unknown')} vs {found_report.get('animal_type', 'Unknown')}"
            },
            'breed_match': {
                'value': 1 if lost_breed == found_breed else 0,
                'description': f"Breed: {lost_report.get('breed', 'Unknown')} vs {found_report.get('breed', 'Unknown')}"
            },
            'color_match': {
                'value': 1 if lost_color == found_color else 0,
                'description': f"Color: {lost_report.get('color', 'Unknown')} vs {found_report.get('color', 'Unknown')}"
            },
            'location_match': {
                'value': 1 if lost_city == found_city else 0,
                'description': f"City: {lost_report.get('city', 'Unknown')} vs {found_report.get('city', 'Unknown')}"
            }
        }
        
        # Save match result to database (RESCUE report treated as LOST)
        match_data = {
            'lost_report_id': lost_report_id,  # This is actually a RESCUE report ID
            'found_report_id': found_report_id,
            'lost_pet_info': f"{lost_report.get('animal_type', 'Unknown')} - {lost_report.get('breed', 'Unknown')} (Rescue)",
            'found_pet_info': f"{found_report.get('animal_type', 'Unknown')} - {found_report.get('breed', 'Unknown')} (Found)",
            'probability': probability,
            'match_strength': match_strength,
            'recommendation': recommendation,
            'feature_analysis': feature_analysis,
            'features': [score, max_score, probability],
            'admin_id': request.session.get('user_id'),
            'admin_name': request.session.get('user_name')
        }
        
        match_id = MatchResult.create(match_data)
        
        return JsonResponse({
            "success": True,
            "match_id": str(match_id),
            "probability": probability,
            "match_strength": match_strength,
            "recommendation": recommendation,
            "feature_analysis": feature_analysis,
            "lost_report": {
                'id': lost_report_id,
                'animal_type': lost_report.get('animal_type', ''),
                'breed': lost_report.get('breed', ''),
                'color': lost_report.get('color', ''),
                'location': f"{lost_report.get('location', '')}, {lost_report.get('city', '')}",
                'owner_name': lost_report.get('owner_name', ''),
                'owner_email': lost_report.get('owner_email', ''),
                'image_path': lost_report.get('image_path', '')
            },
            "found_report": {
                'id': found_report_id,
                'animal_type': found_report.get('animal_type', ''),
                'breed': found_report.get('breed', ''),
                'color': found_report.get('color', ''),
                'location': f"{found_report.get('location', '')}, {found_report.get('city', '')}",
                'finder_name': found_report.get('contact_name', ''),
                'finder_email': found_report.get('contact_email', ''),
                'image_path': found_report.get('image_path', '')
            }
        })
        
    except Exception as e:
        return JsonResponse({"error": f"Matching error: {str(e)}"}, status=500)

# API to get all match results for admin
@never_cache
def admin_get_match_results_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        from .models import MatchResult
        
        # Get all match results
        match_results = MatchResult.find_all()
        
        results_data = []
        for result in match_results:
            result_data = {
                'id': str(result['_id']),
                'lost_pet_info': result.get('lost_pet_info', ''),
                'found_pet_info': result.get('found_pet_info', ''),
                'probability': result.get('probability', 0.0),
                'match_strength': result.get('match_strength', ''),
                'recommendation': result.get('recommendation', ''),
                'status': result.get('status', 'pending'),
                'admin_name': result.get('admin_name', ''),
                'created_at': result.get('created_at', '').strftime('%Y-%m-%d %H:%M') if result.get('created_at') else '',
                'feature_analysis': result.get('feature_analysis', {})
            }
            results_data.append(result_data)
        
        return JsonResponse({"match_results": results_data})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to approve/reject match and notify pet owners
@never_cache
def admin_match_action_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        from .models import MatchResult, PetReport, Notification
        from django.core.mail import send_mail
        
        data = json.loads(request.body)
        match_id = data.get('match_id')
        action = data.get('action')  # 'approve' or 'reject'
        admin_notes = data.get('admin_notes', '')
        
        if not all([match_id, action]):
            return JsonResponse({"error": "match_id and action are required"}, status=400)
        
        # Get the match result
        match_result = MatchResult.find_by_id(match_id)
        if not match_result:
            return JsonResponse({"error": "Match result not found"}, status=404)
        
        # Update match status
        MatchResult.update_status(match_id, action, admin_notes)
        
        if action == 'approve':
            # Get the original reports for contact information
            lost_report = PetReport.find_by_id(match_result.get('lost_report_id'))
            found_report = PetReport.find_by_id(match_result.get('found_report_id'))
            
            if lost_report and found_report:
                # Send email notifications
                try:
                    # Email to pet owner (lost report)
                    owner_email = lost_report.get('owner_email')
                    if owner_email:
                        send_mail(
                            subject="🎉 Possible Match Found for Your Lost Pet - RescueMate",
                            message=f"""Hello {lost_report.get('owner_name', 'Pet Owner')},

Great news! We may have found a match for your lost {lost_report.get('animal_type', 'pet')}.

Match Details:
- Pet Type: {found_report.get('animal_type', 'Unknown')}
- Breed: {found_report.get('breed', 'Unknown')}
- Color: {found_report.get('color', 'Unknown')}
- Found Location: {found_report.get('location', 'Unknown')}, {found_report.get('city', 'Unknown')}
- Match Probability: {match_result.get('probability', 0.0):.1%}

Please contact our admin team immediately for verification and next steps.

Admin Contact: {request.session.get('user_name', 'RescueMate Admin')}

Best regards,
RescueMate Team""",
                            from_email="RescueMate - Pet Adoption & Rescue Portal <s23_gaidhani_tanmay@mgmcen.ac.in>",
                            recipient_list=[owner_email],
                            fail_silently=True,
                        )
                    
                    # Email to finder (found report)
                    finder_email = found_report.get('contact_email')
                    if finder_email:
                        send_mail(
                            subject="🎉 Pet Owner Found for Your Found Pet Report - RescueMate",
                            message=f"""Hello {found_report.get('contact_name', 'Good Samaritan')},

Thank you for reporting the found {found_report.get('animal_type', 'pet')}! We may have found the owner.

Match Details:
- Lost Pet: {lost_report.get('animal_type', 'Unknown')} - {lost_report.get('breed', 'Unknown')}
- Owner: {lost_report.get('owner_name', 'Unknown')}
- Match Probability: {match_result.get('probability', 0.0):.1%}

Please contact our admin team for verification and coordination.

Admin Contact: {request.session.get('user_name', 'RescueMate Admin')}

Thank you for your kindness in helping reunite pets with their families!

Best regards,
RescueMate Team""",
                            from_email="RescueMate - Pet Adoption & Rescue Portal <s23_gaidhani_tanmay@mgmcen.ac.in>",
                            recipient_list=[finder_email],
                            fail_silently=True,
                        )
                    
                    # Create in-app notifications
                    if lost_report.get('user_id'):
                        Notification.create({
                            'user_id': lost_report.get('user_id'),
                            'title': 'Possible Pet Match Found!',
                            'message': f'We found a potential match for your lost {lost_report.get("animal_type", "pet")}. Please contact admin for verification.',
                            'type': 'match_found',
                            'match_id': match_id
                        })
                    
                    if found_report.get('user_id'):
                        Notification.create({
                            'user_id': found_report.get('user_id'),
                            'title': 'Pet Owner May Be Found!',
                            'message': f'We may have found the owner of the {found_report.get("animal_type", "pet")} you reported. Please contact admin.',
                            'type': 'owner_found',
                            'match_id': match_id
                        })
                    
                except Exception as e:
                    print(f"Error sending notifications: {str(e)}")
            
            return JsonResponse({
                "success": True, 
                "message": "Match approved and notifications sent to pet owner and finder!"
            })
        
        elif action == 'reject':
            return JsonResponse({
                "success": True, 
                "message": "Match rejected successfully."
            })
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API for batch ML analysis (find all potential matches)
@never_cache
def admin_batch_ml_analysis_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        from .models import PetReport
        
        # Get approved reports
        lost_reports = PetReport.find_approved_by_type('LOST')
        found_reports = PetReport.find_approved_by_type('FOUND')
        
        # EMBEDDED BATCH ANALYSIS - NO EXTERNAL IMPORTS
        matches = []
        
        for lost_report in lost_reports:
            for found_report in found_reports:
                # Simple matching logic
                score = 0.0
                max_score = 5.0
                
                # Pet type match
                lost_type = str(lost_report.get('animal_type', '')).lower().strip()
                found_type = str(found_report.get('animal_type', '')).lower().strip()
                if lost_type == found_type:
                    score += 2.0
                
                # Breed match
                lost_breed = str(lost_report.get('breed', '')).lower().strip()
                found_breed = str(found_report.get('breed', '')).lower().strip()
                if lost_breed == found_breed:
                    score += 1.5
                
                # Color match
                lost_color = str(lost_report.get('color', '')).lower().strip()
                found_color = str(found_report.get('color', '')).lower().strip()
                if lost_color == found_color:
                    score += 1.0
                
                # Location match
                lost_city = str(lost_report.get('city', '')).lower().strip()
                found_city = str(found_report.get('city', '')).lower().strip()
                if lost_city == found_city:
                    score += 0.5
                
                probability = round(score / max_score, 3)
                
                if probability >= 0.5:  # Only include matches >= 50%
                    if probability >= 0.8:
                        match_strength = 'STRONG'
                        recommendation = 'Strong match - Verify and notify pet owners'
                    elif probability >= 0.5:
                        match_strength = 'MEDIUM'
                        recommendation = 'Medium match - Manual verification recommended'
                    else:
                        match_strength = 'WEAK'
                        recommendation = 'Low match - Consider other options'
                    
                    matches.append({
                        'lost_report_id': str(lost_report.get('_id', '')),
                        'found_report_id': str(found_report.get('_id', '')),
                        'lost_pet_info': f"{lost_report.get('animal_type', 'Unknown')} - {lost_report.get('breed', 'Unknown')}",
                        'found_pet_info': f"{found_report.get('animal_type', 'Unknown')} - {found_report.get('breed', 'Unknown')}",
                        'probability': probability,
                        'match_strength': match_strength,
                        'recommendation': recommendation,
                        'feature_analysis': {}
                    })
        
        # Sort by probability (highest first)
        matches.sort(key=lambda x: x['probability'], reverse=True)
        
        return JsonResponse({
            "success": True,
            "total_lost_reports": len(lost_reports),
            "total_found_reports": len(found_reports),
            "potential_matches": matches[:20],  # Limit to top 20 matches
            "high_probability_matches": len([m for m in matches if m['probability'] >= 0.8]),
            "medium_probability_matches": len([m for m in matches if 0.5 <= m['probability'] < 0.8])
        })
        
    except Exception as e:
        return JsonResponse({"error": f"Batch analysis error: {str(e)}"}, status=500)


# Helper function to calculate time ago
def get_time_ago(created_at):
    from datetime import datetime, timezone
    
    if not created_at:
        return ''
    
    # Ensure created_at is timezone-aware
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - created_at
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"


# ===== CHAT HISTORY API =====

# API to get user's chat history
@never_cache
def get_chat_history_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user_id = request.session.get('user_id')
        chat_messages = ChatMessage.find_by_user_id(user_id, limit=50)
        
        messages_data = []
        for msg in chat_messages:
            message_data = {
                'id': str(msg['_id']),
                'user_message': msg.get('user_message', ''),
                'bot_response': msg.get('bot_response', ''),
                'created_at': msg.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if msg.get('created_at') else '',
                'time_ago': get_time_ago(msg.get('created_at')) if msg.get('created_at') else ''
            }
            messages_data.append(message_data)
        
        return JsonResponse({
            "messages": messages_data,
            "total_count": len(messages_data)
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API to clear user's chat history
@never_cache
def clear_chat_history_api(request):
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        user_id = request.session.get('user_id')
        result = ChatMessage.delete_by_user_id(user_id)
        
        return JsonResponse({
            "success": True,
            "message": f"Cleared {result.deleted_count} chat messages",
            "deleted_count": result.deleted_count
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# Simple ML Test API
@never_cache
def simple_ml_test_api(request):
    """Simple test endpoint for embedded ML matching"""
    try:
        # Test data
        sample_lost = {
            'animal_type': 'Dog',
            'breed': 'Golden Retriever',
            'color': 'Golden',
            'city': 'New York'
        }
        
        sample_found = {
            'animal_type': 'Dog',
            'breed': 'Golden Retriever',
            'color': 'Golden',
            'city': 'New York'
        }
        
        # Embedded matching logic
        score = 0.0
        max_score = 5.0
        
        if sample_lost.get('animal_type', '').lower() == sample_found.get('animal_type', '').lower():
            score += 2.0
        if sample_lost.get('breed', '').lower() == sample_found.get('breed', '').lower():
            score += 1.5
        if sample_lost.get('color', '').lower() == sample_found.get('color', '').lower():
            score += 1.0
        if sample_lost.get('city', '').lower() == sample_found.get('city', '').lower():
            score += 0.5
        
        probability = score / max_score
        
        return JsonResponse({
            "success": True,
            "embedded_ml_working": True,
            "test_probability": probability,
            "score": score,
            "max_score": max_score,
            "message": "Embedded ML matching is working!"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
# Test endpoint with completely different name
@never_cache
def test_pet_matching_api(request):
    """Test endpoint to verify the matching works"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        from .models import PetReport
        
        data = json.loads(request.body)
        lost_report_id = data.get('lost_report_id')
        found_report_id = data.get('found_report_id')
        
        if not all([lost_report_id, found_report_id]):
            return JsonResponse({"error": "Both report IDs are required"}, status=400)
        
        # Get the reports
        lost_report = PetReport.find_by_id(lost_report_id)
        found_report = PetReport.find_by_id(found_report_id)
        
        if not lost_report or not found_report:
            return JsonResponse({"error": "Reports not found"}, status=404)
        
        # Simple matching - NO EXTERNAL IMPORTS AT ALL
        score = 0
        if lost_report.get('animal_type', '').lower() == found_report.get('animal_type', '').lower():
            score += 2
        if lost_report.get('breed', '').lower() == found_report.get('breed', '').lower():
            score += 2
        if lost_report.get('color', '').lower() == found_report.get('color', '').lower():
            score += 1
        
        probability = score / 5.0
        
        return JsonResponse({
            "success": True,
            "probability": probability,
            "match_strength": "STRONG" if probability >= 0.8 else "MEDIUM" if probability >= 0.5 else "WEAK",
            "message": "Test matching successful - no imports used!",
            "lost_pet": f"{lost_report.get('animal_type', 'Unknown')} - {lost_report.get('breed', 'Unknown')}",
            "found_pet": f"{found_report.get('animal_type', 'Unknown')} - {found_report.get('breed', 'Unknown')}",
            "score": score
        })
        
    except Exception as e:
        return JsonResponse({"error": f"Test error: {str(e)}"}, status=500)

# ===== USER PROFILE VIEWS AND APIs =====

@never_cache
def user_profile_view(request):
    """User profile page view"""
    if "user_id" not in request.session:
        return redirect("login")
    
    try:
        user = User.get_by_id(request.session["user_id"])
        if not user:
            return redirect("login")
        
        context = {
            "user_name": user.get("fullname", "User"),
            "user_email": user.get("email", ""),
            "user_first_name": user.get("fullname", "").split()[0] if user.get("fullname") else "",
            "user_last_name": " ".join(user.get("fullname", "").split()[1:]) if len(user.get("fullname", "").split()) > 1 else "",
            "user_phone": user.get("phone", ""),
        }
        
        return render(request, "user_profile.html", context)
        
    except Exception as e:
        print(f"Error in user_profile_view: {e}")
        return redirect("dashboard")

@never_cache
def user_profile_stats_api(request):
    """API to get user profile statistics"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user_id = request.session["user_id"]
        
        # Count user's activities
        adoption_requests = 0  # Would count from adoption requests collection
        
        # Count reports from unified collection efficiently
        rescue_reports = len(list(db['pet_reports'].find({'user_id': user_id, 'report_type': 'RESCUE'})))
        found_pet_reports = len(list(db['pet_reports'].find({'user_id': user_id, 'report_type': 'FOUND'})))
        
        community_comments = Comment.count_by_user(user_id)
        
        stats = {
            "adoption_requests": adoption_requests,
            "rescue_reports": rescue_reports,
            "found_pet_reports": found_pet_reports,
            "community_comments": community_comments
        }
        
        return JsonResponse({"success": True, "stats": stats})
        
    except Exception as e:
        print(f"Error in user_profile_stats_api: {e}")
        return JsonResponse({"error": "Failed to load stats"}, status=500)

@never_cache
def user_profile_activity_api(request):
    """API to get user's recent activity"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user_id = request.session["user_id"]
        activities = []
        
        # Get recent reports from unified collection
        recent_reports = PetReport.get_recent_by_user(user_id, limit=20)
        for report in recent_reports:
            report_type = report.get('report_type', '').lower()
            activities.append({
                "type": report_type,
                "title": f"Reported {report_type.title()} {report.get('animal_type', 'Animal')}",
                "description": f"Location: {report.get('location', 'Unknown')} - {report.get('breed', 'Unknown breed')}",
                "time_ago": format_time_ago(report.get('created_at')),
                "date": report.get('created_at')
            })
        
        # Get recent comments
        comments = Comment.get_recent_by_user(user_id, limit=10)
        for comment in comments:
            activities.append({
                "type": "comment",
                "title": "Posted Community Comment",
                "description": comment.get('message', '')[:100] + ('...' if len(comment.get('message', '')) > 100 else ''),
                "time_ago": format_time_ago(comment.get('created_at')),
                "date": comment.get('created_at')
            })
        
        # Sort activities by date (most recent first)
        activities.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Limit to 20 most recent activities
        activities = activities[:20]
        
        return JsonResponse({"success": True, "activities": activities})
        
    except Exception as e:
        print(f"Error in user_profile_activity_api: {e}")
        return JsonResponse({"error": "Failed to load activity"}, status=500)

@never_cache
def user_profile_member_since_api(request):
    """API to get user's member since date"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user = User.get_by_id(request.session["user_id"])
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        
        # Format the created_at date
        created_at = user.get('created_at')
        if created_at:
            member_since = format_date(created_at)
        else:
            member_since = "Unknown"
        
        return JsonResponse({"success": True, "member_since": member_since})
        
    except Exception as e:
        print(f"Error in user_profile_member_since_api: {e}")
        return JsonResponse({"error": "Failed to load member since"}, status=500)

@never_cache
@csrf_exempt
def user_profile_update_api(request):
    """API to update user profile information"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = request.session["user_id"]
        
        # Get current user
        user = User.get_by_id(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        
        # Update user information
        update_data = {}
        
        if 'first_name' in data and 'last_name' in data:
            fullname = f"{data['first_name'].strip()} {data['last_name'].strip()}".strip()
            if fullname:
                update_data['fullname'] = fullname
        
        if 'email' in data and data['email'].strip():
            # Check if email is already taken by another user
            existing_user = User.get_by_email(data['email'].strip())
            if existing_user and existing_user.get('_id') != user_id:
                return JsonResponse({"error": "Email already taken by another user"}, status=400)
            update_data['email'] = data['email'].strip()
        
        if 'phone' in data and data['phone'].strip():
            update_data['phone'] = data['phone'].strip()
        
        # Update user in database
        if update_data:
            User.update_by_id(user_id, update_data)
        
        # Return updated user data
        updated_user = User.get_by_id(user_id)
        return JsonResponse({
            "success": True, 
            "message": "Profile updated successfully",
            "user": {
                "name": updated_user.get('fullname', ''),
                "email": updated_user.get('email', '')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(f"Error in user_profile_update_api: {e}")
        return JsonResponse({"error": "Failed to update profile"}, status=500)

@never_cache
@csrf_exempt
def user_profile_settings_api(request):
    """API to update user settings"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = request.session["user_id"]
        
        setting = data.get('setting')
        value = data.get('value')
        
        if not setting:
            return JsonResponse({"error": "Setting name required"}, status=400)
        
        # Update user settings (you might want to create a separate UserSettings model)
        # For now, we'll store settings in the user document
        user = User.get_by_id(user_id)
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        
        # Initialize settings if not exists
        if 'settings' not in user:
            user['settings'] = {}
        
        user['settings'][setting] = value
        
        # Update user in database
        User.update_by_id(user_id, {'settings': user['settings']})
        
        return JsonResponse({"success": True, "message": "Setting updated successfully"})
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(f"Error in user_profile_settings_api: {e}")
        return JsonResponse({"error": "Failed to update setting"}, status=500)

@never_cache
@csrf_exempt
def user_profile_delete_api(request):
    """API to delete user account"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        user_id = request.session["user_id"]
        
        # Delete user's data
        # Note: In a production system, you might want to anonymize rather than delete
        
        # Delete user's reports from unified collection
        PetReport.delete_by_user(user_id)
        
        # Delete user's comments
        Comment.delete_by_user(user_id)
        
        # Delete user's chat messages
        ChatMessage.delete_by_user(user_id)
        
        # Finally delete the user account
        User.delete_by_id(user_id)
        
        # Clear session
        request.session.flush()
        
        return JsonResponse({"success": True, "message": "Account deleted successfully"})
        
    except Exception as e:
        print(f"Error in user_profile_delete_api: {e}")
        return JsonResponse({"error": "Failed to delete account"}, status=500)

# ===== UTILITY FUNCTIONS FOR PROFILE =====

def format_time_ago(date_str):
    """Format date string to 'time ago' format"""
    if not date_str:
        return "Unknown"
    
    try:
        from datetime import datetime, timezone
        import re
        
        # Handle different date formats
        if isinstance(date_str, str):
            # Try to parse ISO format first
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                # Try other common formats
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        return "Unknown"
        else:
            date_obj = date_str
        
        # Make timezone aware if not already
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        diff = now - date_obj
        
        days = diff.days
        seconds = diff.seconds
        
        if days > 30:
            return f"{days // 30} month{'s' if days // 30 > 1 else ''} ago"
        elif days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds > 3600:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds > 60:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
            
    except Exception as e:
        print(f"Error formatting time ago: {e}")
        return "Unknown"

def format_date(date_str):
    """Format date string to readable format"""
    if not date_str:
        return "Unknown"
    
    try:
        from datetime import datetime
        
        if isinstance(date_str, str):
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        return "Unknown"
        else:
            date_obj = date_str
        
        return date_obj.strftime('%B %Y')  # e.g., "January 2024"
        
    except Exception as e:
        print(f"Error formatting date: {e}")
        return "Unknown"

# ===== PET CHAT API ENDPOINTS =====

@never_cache
@csrf_exempt
def pet_chat_send_message_api(request):
    """API to send a chat message about a specific pet report"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Login required"}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        message = data.get('message', '').strip()
        
        if not report_id or not message:
            return JsonResponse({"error": "Report ID and message are required"}, status=400)
        
        if len(message) > 500:
            return JsonResponse({"error": "Message too long (max 500 characters)"}, status=400)
        
        # Get user info
        user_id = request.session.get("user_id")
        user_name = request.session.get("user_name", "Anonymous")
        
        # Create chat message
        chat_message = {
            'report_id': report_id,
            'user_id': user_id,
            'user_name': user_name,
            'message': message,
            'created_at': datetime.now(),
            'message_type': 'pet_discussion'
        }
        
        # Save to database
        result = ChatMessage.create(chat_message)
        
        if result:
            return JsonResponse({
                "success": True,
                "message": "Message sent successfully"
            })
        else:
            return JsonResponse({"error": "Failed to save message"}, status=500)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
def pet_chat_get_messages_api(request, report_id):
    """API to get chat messages for a specific pet report"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Login required"}, status=403)
    
    try:
        # Get current user ID
        current_user_id = request.session.get("user_id")
        
        # Get all chat messages for this report
        messages = ChatMessage.find_by_report(report_id)
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': str(msg.get('_id', '')),
                'user_name': msg.get('user_name', 'Anonymous'),
                'message': msg.get('message', ''),
                'created_at': msg.get('created_at', '').isoformat() if msg.get('created_at') else '',
                'is_current_user': str(msg.get('user_id', '')) == str(current_user_id)
            })
        
        # Sort by creation time (oldest first)
        formatted_messages.sort(key=lambda x: x['created_at'])
        
        return JsonResponse({
            "success": True,
            "messages": formatted_messages
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ===== ADMIN CHAT MANAGEMENT SYSTEM =====

@never_cache
def admin_chat_view(request):
    """Admin Chat Management Dashboard"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_chat.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@never_cache
def admin_chat_stats_api(request):
    """API to get chat statistics for admin dashboard"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all pet discussion messages
        all_messages = list(db[ChatMessage.COLLECTION_NAME].find({'message_type': 'pet_discussion'}))
        
        # Calculate stats
        total_chats = len(set(msg.get('report_id') for msg in all_messages if msg.get('report_id')))
        
        # Messages from today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_messages = len([msg for msg in all_messages if msg.get('created_at', datetime.min) >= today])
        
        # Active users (users who sent messages in last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = len(set(msg.get('user_id') for msg in all_messages if msg.get('created_at', datetime.min) >= week_ago and msg.get('user_id')))
        
        # Flagged messages (placeholder - implement flagging system later)
        flagged_messages = 0
        
        return JsonResponse({
            "total_chats": total_chats,
            "recent_messages": recent_messages,
            "active_users": active_users,
            "flagged_messages": flagged_messages
        })
        
    except Exception as e:
        print(f"Admin chat stats error: {str(e)}")  # Debug logging
        return JsonResponse({
            "total_chats": 0,
            "recent_messages": 0,
            "active_users": 0,
            "flagged_messages": 0,
            "error": str(e)
        })


@never_cache
def admin_chat_list_api(request):
    """API to get list of pet discussions for admin"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all pet discussion messages grouped by report_id
        pipeline = [
            {"$match": {"message_type": "pet_discussion"}},
            {"$group": {
                "_id": "$report_id",
                "message_count": {"$sum": 1},
                "last_message": {"$last": "$message"},
                "last_message_time": {"$last": "$created_at"}
            }},
            {"$sort": {"last_message_time": -1}}
        ]
        
        chat_groups = list(db[ChatMessage.COLLECTION_NAME].aggregate(pipeline))
        
        # Get user names and pet info from reports
        chats = []
        for group in chat_groups:
            report_id = group['_id']
            
            if not report_id:
                continue
                
            # Try to find the pet report and get user info
            user_name = 'Unknown User'
            pet_info = 'Unknown Pet'
            user_id = None
            
            try:
                # Try rescues collection first
                pet_report = db['rescues'].find_one({'_id': ObjectId(report_id)})
                if pet_report:
                    user_id = pet_report.get('user_id')
                    user_name = pet_report.get('user_name', pet_report.get('contact_name', 'Unknown User'))
                    pet_info = f"{pet_report.get('breed', 'Unknown')} ({pet_report.get('animal_type', 'Pet')})"
                else:
                    # Try pet_found collection
                    pet_report = db['pet_found'].find_one({'_id': ObjectId(report_id)})
                    if pet_report:
                        user_id = pet_report.get('user_id')
                        user_name = pet_report.get('user_name', pet_report.get('contact_name', 'Unknown User'))
                        pet_info = f"{pet_report.get('breed', 'Unknown')} ({pet_report.get('animal_type', 'Pet')})"
                    else:
                        # Try pet_reports collection (unified)
                        pet_report = db['pet_reports'].find_one({'_id': ObjectId(report_id)})
                        if pet_report:
                            user_id = pet_report.get('user_id')
                            user_name = pet_report.get('user_name', pet_report.get('contact_name', pet_report.get('owner_name', 'Unknown User')))
                            pet_info = f"{pet_report.get('breed', pet_report.get('pet_name', 'Unknown'))} ({pet_report.get('animal_type', 'Pet')})"
                        else:
                            user_name = f'User {report_id[:8]}...'
                            pet_info = f'Pet Report {report_id[:8]}...'
                
                # If we have user_id but no user_name, try to get it from users collection
                if user_id and (not user_name or user_name == 'Unknown User'):
                    try:
                        user_doc = db['users'].find_one({'_id': ObjectId(user_id)})
                        if user_doc:
                            user_name = user_doc.get('fullname', 'Unknown User')
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error getting user info for report {report_id}: {str(e)}")
                user_name = f'User {report_id[:8]}...'
                pet_info = f'Pet Report {report_id[:8]}...'
            
            chats.append({
                'report_id': report_id,
                'pet_name': f"{user_name} - {pet_info}",  # Show "User Name - Pet Info"
                'user_name': user_name,  # Separate user name field
                'pet_info': pet_info,    # Separate pet info field
                'message_count': group['message_count'],
                'last_message': group['last_message'][:50] + '...' if len(group['last_message']) > 50 else group['last_message'],
                'last_message_time': group['last_message_time'].isoformat() if group['last_message_time'] else ''
            })
        
        return JsonResponse({"chats": chats})
        
    except Exception as e:
        print(f"Admin chat list error: {str(e)}")  # Debug logging
        return JsonResponse({"chats": [], "error": str(e)})


@never_cache
def admin_chat_messages_api(request, report_id):
    """API to get chat messages for a specific pet report (admin view)"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all chat messages for this report
        messages = ChatMessage.find_by_report(report_id)
        
        # Format messages for admin view
        formatted_messages = []
        for msg in messages:
            # Check if message is from admin
            user_id = str(msg.get('user_id', ''))
            is_admin = msg.get('is_admin', False)
            
            # If not explicitly marked as admin, check if user is admin
            if not is_admin:
                user = User.get_by_id(user_id)
                is_admin = user.get('is_admin', False) if user else False
            
            formatted_messages.append({
                'id': str(msg.get('_id', '')),
                'user_name': msg.get('user_name', 'Anonymous'),
                'message': msg.get('message', ''),
                'created_at': msg.get('created_at', '').isoformat() if msg.get('created_at') else '',
                'is_admin': is_admin,
                'user_id': user_id
            })
        
        # Sort by creation time (oldest first)
        formatted_messages.sort(key=lambda x: x['created_at'])
        
        return JsonResponse({
            "success": True,
            "messages": formatted_messages
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
@csrf_exempt
def admin_send_chat_message_api(request):
    """API for admin to send messages in pet discussions"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        message = data.get('message', '').strip()
        
        if not report_id or not message:
            return JsonResponse({"error": "Report ID and message are required"}, status=400)
        
        if len(message) > 500:
            return JsonResponse({"error": "Message too long (max 500 characters)"}, status=400)
        
        # Get admin info
        admin_id = request.session.get("user_id")
        admin_name = request.session.get("user_name", "Admin")
        
        # Create admin chat message
        chat_message = {
            'report_id': report_id,
            'user_id': admin_id,
            'user_name': admin_name,
            'message': message,
            'created_at': datetime.now(),
            'message_type': 'pet_discussion',
            'is_admin': True
        }
        
        # Save to database
        result = ChatMessage.create(chat_message)
        
        if result:
            return JsonResponse({
                "success": True,
                "message": "Admin message sent successfully"
            })
        else:
            return JsonResponse({"error": "Failed to save message"}, status=500)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
@csrf_exempt
def admin_close_chat_api(request):
    """API for admin to close a pet discussion"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        
        if not report_id:
            return JsonResponse({"error": "Report ID is required"}, status=400)
        
        # Add a system message indicating chat is closed
        admin_id = request.session.get("user_id")
        admin_name = request.session.get("user_name", "Admin")
        
        system_message = {
            'report_id': report_id,
            'user_id': admin_id,
            'user_name': 'System',
            'message': f'🔒 This discussion has been closed by admin {admin_name}. No new messages can be posted.',
            'created_at': datetime.now(),
            'message_type': 'pet_discussion',
            'is_admin': True,
            'is_system': True
        }
        
        # Save system message
        result = ChatMessage.create(system_message)
        
        # TODO: Implement actual chat closing logic (add closed flag to report)
        # For now, just add the system message
        
        if result:
            return JsonResponse({
                "success": True,
                "message": "Chat discussion closed successfully"
            })
        else:
            return JsonResponse({"error": "Failed to close chat"}, status=500)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ===== ADMIN REPORTS MANAGEMENT APIs =====

@never_cache
def admin_reports_stats_api(request):
    """API to get reports statistics for admin dashboard"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get all reports from unified collection
        all_reports = PetReport.find_all()
        
        # Calculate stats by type
        rescue_reports = [r for r in all_reports if r.get('report_type') == 'RESCUE']
        found_reports = [r for r in all_reports if r.get('report_type') == 'FOUND']
        lost_reports = [r for r in all_reports if r.get('report_type') == 'LOST']
        
        # Calculate stats by status
        total_reports = len(all_reports)
        pending_reports = len([r for r in all_reports if r.get('status') == 'pending'])
        approved_reports = len([r for r in all_reports if r.get('status') == 'approved'])
        rejected_reports = len([r for r in all_reports if r.get('status') == 'rejected'])
        
        # Recent reports (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_reports = len([r for r in all_reports if r.get('created_at', datetime.min) >= week_ago])
        
        return JsonResponse({
            "total_reports": total_reports,
            "pending_reports": pending_reports,
            "approved_reports": approved_reports,
            "rejected_reports": rejected_reports,
            "recent_reports": recent_reports,
            "rescue_reports": len(rescue_reports),
            "found_reports": len(found_reports),
            "lost_reports": len(lost_reports)
        })
        
    except Exception as e:
        print(f"Admin reports stats error: {str(e)}")
        return JsonResponse({
            "total_reports": 0,
            "pending_reports": 0,
            "approved_reports": 0,
            "rejected_reports": 0,
            "recent_reports": 0,
            "rescue_reports": 0,
            "found_reports": 0,
            "lost_reports": 0,
            "error": str(e)
        })


@never_cache
def admin_all_reports_api(request):
    """API to get all reports for admin management"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get filter parameters
        report_type = request.GET.get('type', 'all')  # all, rescue, found, lost
        status = request.GET.get('status', 'all')     # all, pending, approved, rejected
        
        # Get all reports from unified collection
        all_reports = PetReport.find_all()
        
        # Filter by type
        if report_type != 'all':
            all_reports = [r for r in all_reports if r.get('report_type', '').upper() == report_type.upper()]
        
        # Filter by status
        if status != 'all':
            all_reports = [r for r in all_reports if r.get('status', '') == status]
        
        # Format reports for frontend
        formatted_reports = []
        for report in all_reports:
            report_data = {
                'id': str(report.get('_id', '')),
                'report_type': report.get('report_type', ''),
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'gender': report.get('gender', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'report_date': report.get('report_date', ''),
                'status': report.get('status', 'pending'),
                'user_id': report.get('user_id', ''),
                'user_name': report.get('user_name', ''),
                'contact_name': report.get('contact_name', ''),
                'contact_phone': report.get('contact_phone', ''),
                'contact_email': report.get('contact_email', ''),
                'description': report.get('description', ''),
                'condition': report.get('condition', ''),
                'urgency': report.get('urgency', ''),
                'special_marks': report.get('special_marks', ''),
                'image_path': report.get('image_path', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d %H:%M') if report.get('created_at') else '',
                'additional_notes': report.get('additional_notes', '')
            }
            formatted_reports.append(report_data)
        
        # Sort by creation date (newest first)
        formatted_reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return JsonResponse({
            "success": True,
            "reports": formatted_reports,
            "total_count": len(formatted_reports)
        })
        
    except Exception as e:
        print(f"Admin all reports error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
def admin_delete_report_api(request):
    """API to delete a report (admin only)"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        report_id = data.get('report_id')
        
        if not report_id:
            return JsonResponse({"error": "Report ID is required"}, status=400)
        
        # Get the report first to get user info for notification
        report = PetReport.find_by_id(report_id)
        if not report:
            return JsonResponse({"error": "Report not found"}, status=404)
        
        # Get report details for notification
        user_id = report.get('user_id')
        user_name = report.get('user_name', 'User')
        animal_type = report.get('animal_type', 'Pet')
        breed = report.get('breed', 'Unknown')
        report_type = report.get('report_type', 'Report')
        
        # Delete the report
        result = PetReport.delete_by_id(report_id)
        
        if result.deleted_count > 0:
            # Send notification to user about deletion
            if user_id:
                title = f"Report Deleted 🗑️"
                message = f"Your {report_type.lower()} report for {animal_type} ({breed}) has been removed by admin. If you believe this was done in error, please contact support."
                
                create_notification(user_id, title, message, 'report_deleted', {
                    'report_id': report_id,
                    'report_type': report_type.lower(),
                    'animal_type': animal_type
                })
                
                # Send email notification
                user_email = report.get('contact_email', '')
                if not user_email and user_id:
                    user = User.find_by_id(user_id)
                    if user:
                        user_email = user.get('email', '')
                
                if user_email:
                    email_message = f"""Your {report_type.lower()} report has been removed.

Report Details:
- Animal: {animal_type} ({breed})
- Report Type: {report_type}
- Status: Deleted by Admin

If you believe this was done in error or have questions, please contact our support team.

Thank you for your understanding."""
                    
                    send_notification_email(user_email, user_name, title, email_message)
            
            return JsonResponse({
                "success": True, 
                "message": "Report deleted successfully and user notified"
            })
        else:
            return JsonResponse({"error": "Failed to delete report"}, status=500)
        
    except Exception as e:
        print(f"Admin delete report error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


# ===== ADMIN SETTINGS VIEWS AND APIs =====

@never_cache
def admin_settings_view(request):
    """Admin Settings Dashboard"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        messages.error(request, "Admin access required!")
        return redirect("login")
    
    response = render(request, "admin_settings.html", {"user_name": request.session.get("user_name")})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@never_cache
def admin_settings_api(request):
    """API to get current admin settings"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Default settings
        default_settings = {
            'platformName': 'RescueMate',
            'platformVersion': '1.0.0',
            'maintenanceMode': False,
            'emailNotifications': True,
            'adminEmail': 'admin@rescuemate.com',
            'smtpServer': 'smtp.gmail.com',
            'sessionTimeout': 60,
            'maxLoginAttempts': 5,
            'requireEmailVerification': True,
            'chatEnabled': True,
            'maxMessageLength': 500,
            'chatModeration': True,
            'maxFileSize': 10,
            'allowedFileTypes': 'jpg, jpeg, png, gif',
            'imageCompression': True,
            'dbStatus': 'Connected',
            'autoBackup': True,
            'backupFrequency': 'daily'
        }
        
        # Try to get settings from database (you can implement a Settings model later)
        # For now, return default settings
        settings = default_settings
        
        return JsonResponse({
            "success": True,
            "settings": settings
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
@csrf_exempt
def admin_settings_save_api(request):
    """API to save admin settings"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        data = json.loads(request.body)
        settings = data.get('settings')
        
        if not settings:
            return JsonResponse({"error": "Settings data required"}, status=400)
        
        # Validate settings
        validation_errors = validate_admin_settings(settings)
        if validation_errors:
            return JsonResponse({"error": validation_errors[0]}, status=400)
        
        # TODO: Save settings to database
        # For now, just return success
        # You can implement a Settings model to store these values
        
        admin_name = request.session.get('user_name', 'Admin')
        
        return JsonResponse({
            "success": True,
            "message": f"Settings saved successfully by {admin_name}"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
@csrf_exempt
def admin_settings_reset_api(request):
    """API to reset admin settings to default"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        # TODO: Reset settings in database to default values
        # For now, just return success
        
        admin_name = request.session.get('user_name', 'Admin')
        
        return JsonResponse({
            "success": True,
            "message": f"Settings reset to default by {admin_name}"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
def admin_settings_export_api(request):
    """API to export admin settings as JSON file"""
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Get current settings
        settings = {
            'platformName': 'RescueMate',
            'platformVersion': '1.0.0',
            'maintenanceMode': False,
            'emailNotifications': True,
            'adminEmail': 'admin@rescuemate.com',
            'smtpServer': 'smtp.gmail.com',
            'sessionTimeout': 60,
            'maxLoginAttempts': 5,
            'requireEmailVerification': True,
            'chatEnabled': True,
            'maxMessageLength': 500,
            'chatModeration': True,
            'maxFileSize': 10,
            'allowedFileTypes': 'jpg, jpeg, png, gif',
            'imageCompression': True,
            'dbStatus': 'Connected',
            'autoBackup': True,
            'backupFrequency': 'daily'
        }
        
        # Add export metadata
        export_data = {
            'export_info': {
                'platform': 'RescueMate',
                'version': '1.0.0',
                'exported_by': request.session.get('user_name', 'Admin'),
                'exported_at': datetime.now().isoformat(),
                'export_type': 'admin_settings'
            },
            'settings': settings
        }
        
        # Create JSON response
        response = JsonResponse(export_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="rescuemate-settings-{datetime.now().strftime("%Y%m%d")}.json"'
        response['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def validate_admin_settings(settings):
    """Validate admin settings data"""
    errors = []
    
    # Email validation
    if settings.get('adminEmail'):
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, settings['adminEmail']):
            errors.append('Invalid admin email format')
    
    # Session timeout validation
    session_timeout = settings.get('sessionTimeout')
    if session_timeout and (session_timeout < 15 or session_timeout > 480):
        errors.append('Session timeout must be between 15 and 480 minutes')
    
    # Max login attempts validation
    max_attempts = settings.get('maxLoginAttempts')
    if max_attempts and (max_attempts < 3 or max_attempts > 10):
        errors.append('Max login attempts must be between 3 and 10')
    
    # Message length validation
    max_length = settings.get('maxMessageLength')
    if max_length and (max_length < 100 or max_length > 1000):
        errors.append('Max message length must be between 100 and 1000 characters')
    
    # File size validation
    max_size = settings.get('maxFileSize')
    if max_size and (max_size < 1 or max_size > 50):
        errors.append('Max file size must be between 1 and 50 MB')
    
    return errors
# ===== USER NOTIFICATION SYSTEM =====

@never_cache
def user_notifications_api(request):
    """API to get user notifications"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        user_id = request.session.get('user_id')
        
        # Get user notifications from database
        notifications = Notification.find_by_user_id(user_id, limit=50)
        
        # Format notifications for frontend
        formatted_notifications = []
        unread_count = 0
        
        for notification in notifications:
            if not notification.get('is_read', False):
                unread_count += 1
            
            formatted_notifications.append({
                'id': str(notification.get('_id', '')),
                'title': notification.get('title', ''),
                'message': notification.get('message', ''),
                'type': notification.get('type', 'general'),
                'is_read': notification.get('is_read', False),
                'created_at': notification.get('created_at', '').isoformat() if notification.get('created_at') else '',
                'time_ago': get_time_ago(notification.get('created_at')) if notification.get('created_at') else ''
            })
        
        return JsonResponse({
            "success": True,
            "notifications": formatted_notifications,
            "unread_count": unread_count
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@never_cache
@csrf_exempt
def mark_notifications_read_api(request):
    """API to mark all notifications as read"""
    if "user_id" not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        user_id = request.session.get('user_id')
        
        # Mark all user notifications as read
        result = Notification.mark_all_as_read_by_user_id(user_id)
        
        return JsonResponse({
            "success": True,
            "message": f"Marked {result.modified_count} notifications as read"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def create_notification(user_id, title, message, notification_type='general', extra_data=None):
    """Helper function to create notifications"""
    try:
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'extra_data': extra_data or {}
        }
        
        result = Notification.create(notification_data)
        return result
        
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None


def send_notification_email(user_email, user_name, title, message):
    """Helper function to send notification emails"""
    try:
        send_mail(
            subject=f"RescueMate Notification - {title}",
            message=f"""Hello {user_name},

{message}

You can view all your notifications by logging into your RescueMate account.

Best regards,
RescueMate Team

---
This is an automated message from RescueMate - Pet Adoption & Rescue Portal""",
            from_email="RescueMate - Pet Adoption & Rescue Portal <s23_gaidhani_tanmay@mgmcen.ac.in>",
            recipient_list=[user_email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Error sending notification email: {str(e)}")
        return False