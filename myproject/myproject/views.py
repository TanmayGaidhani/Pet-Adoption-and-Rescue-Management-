from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from .models import User, Rescue, PetFound
import random
import json
import os
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

        print(f"DEBUG - Entered OTP: '{entered_otp}'")  # Debug
        print(f"DEBUG - Session OTP: '{session_otp}'")  # Debug

        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP!")
            return redirect("signup")
        # ----------------------------------------------

        hashed_password = make_password(password)
        User.create(fullname=fullname, email=email, phone=phone, password=hashed_password)

        # Clear OTP from session
        request.session.pop('otp', None)
        
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

        print(f"Attempting to send OTP {otp} to {email}")  # Debug logging

        try:
            result = send_mail(
                subject="Your OTP Verification Code - RescueMate",
                message=f"Hello!\n\nYour OTP verification code is: {otp}\n\nThis code will expire in 10 minutes.\n\nThank you for joining RescueMate - Pet Adoption & Rescue Portal!\n\nBest regards,\nRescueMate Team",
                from_email="RescueMate - Pet Adoption & Rescue Portal <s23_gaidhani_tanmay@mgmcen.ac.in>",
                recipient_list=[email],
                fail_silently=False,
            )
            print(f"Email sent successfully! Result: {result}")  # Debug logging
            return JsonResponse({"success": True, "message": f"OTP sent to {email}"})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Email error: {str(e)}")  # Debug logging
            print(f"Full error: {error_details}")  # Debug logging
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
                request.session.set_expiry(3600)  # Session expires in 1 hour
                
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
    
    if request.method == "POST":
        report_type = request.POST.get('reportType')  # 'found' or 'rescue'
        
        # Get form data
        report_data = {
            'user_id': request.session.get('user_id'),
            'user_name': request.session.get('user_name'),
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
            'contact_name': request.POST.get('contactName'),
            'contact_phone': request.POST.get('contactPhone'),
            'contact_email': request.POST.get('contactEmail'),
            'description': request.POST.get('description'),
            'urgency': request.POST.get('urgency'),
            'additional_notes': request.POST.get('additionalNotes', ''),
        }
        
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
        
        # Save to appropriate database collection based on report type
        try:
            if report_type == 'found':
                PetFound.create(report_data)
                messages.success(request, "Pet Found report submitted successfully! It will be reviewed by our admin team and published once approved.")
            elif report_type == 'rescue':
                Rescue.create(report_data)
                messages.success(request, "Animal Rescue report submitted successfully! It will be reviewed by our admin team and published once approved.")
            else:
                messages.error(request, "Invalid report type selected!")
                return redirect("rescue")
            
            return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Error submitting report: {str(e)}")
    
    response = render(request, "rescue.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# PET REPORT (Lost/Missing Pet)
@never_cache
def pet_report_view(request):
    if "user_id" not in request.session:
        messages.error(request, "Please login first!")
        return redirect("login")
    
    if request.method == "POST":
        # Get form data
        pet_data = {
            'user_id': request.session.get('user_id'),
            'user_name': request.session.get('user_name'),
            'pet_name': request.POST.get('petName'),
            'pet_type': request.POST.get('petType'),
            'breed': request.POST.get('breed'),
            'age': request.POST.get('age'),
            'gender': request.POST.get('gender'),
            'color_markings': request.POST.get('colorMarkings'),
            'last_seen_location': request.POST.get('lastSeenLocation'),
            'city': request.POST.get('city'),
            'date_lost': request.POST.get('dateLost'),
            'time_lost': request.POST.get('timeLost', ''),
            'microchip': request.POST.get('microchip', ''),
            'special_features': request.POST.get('specialFeatures'),
            'owner_name': request.POST.get('ownerName'),
            'contact_phone': request.POST.get('contactPhone'),
            'contact_email': request.POST.get('contactEmail'),
            'reward': request.POST.get('reward', ''),
            'additional_info': request.POST.get('additionalInfo', ''),
        }
        
        # Handle file upload
        if 'petPhoto' in request.FILES:
            pet_photo = request.FILES['petPhoto']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'pet_reports'))
            
            # Create unique filename
            import uuid
            ext = pet_photo.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            
            # Save file
            saved_filename = fs.save(filename, pet_photo)
            pet_data['image_path'] = f"pet_reports/{saved_filename}"
        
        # Save to database
        try:
            PetReport.create(pet_data)
            messages.success(request, "Pet report submitted successfully! We'll help you find your pet.")
            return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Error submitting report: {str(e)}")
    
    response = render(request, "pet_report.html")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

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
        # Get only approved pet found reports for public view
        found_pets = PetFound.find_approved()
        
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
        # Get only approved rescue reports for public view
        rescue_reports = Rescue.find_approved()
        
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
    
    # Placeholder for now
    messages.info(request, "Reports management page coming soon!")
    return redirect("admin_dashboard")

# API for admin dashboard stats
@never_cache
def admin_stats_api(request):
    if "user_id" not in request.session or not request.session.get("is_admin"):
        return JsonResponse({"error": "Admin access required"}, status=403)
    
    try:
        # Count users
        total_users = len(User.find_all_users())
        
        # Count found pets
        found_pets = len(PetFound.find_all())
        
        # Count rescue reports
        rescue_reports = len(Rescue.find_all())
        
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
        # Get pending found pets
        pending_found = PetFound.find_pending()
        found_data = []
        for pet in pending_found:
            pet_data = {
                'id': str(pet['_id']),
                'type': 'found',
                'animal_type': pet.get('animal_type', ''),
                'breed': pet.get('breed', ''),
                'color': pet.get('color', ''),
                'location': pet.get('location', ''),
                'city': pet.get('city', ''),
                'contact_name': pet.get('contact_name', ''),
                'contact_phone': pet.get('contact_phone', ''),
                'contact_email': pet.get('contact_email', ''),
                'description': pet.get('description', ''),
                'special_marks': pet.get('special_marks', ''),
                'condition': pet.get('condition', ''),
                'report_date': pet.get('report_date', ''),
                'image_path': pet.get('image_path', ''),
                'created_at': pet.get('created_at', '').strftime('%Y-%m-%d') if pet.get('created_at') else ''
            }
            found_data.append(pet_data)
        
        # Get pending rescue reports
        pending_rescue = Rescue.find_pending()
        rescue_data = []
        for report in pending_rescue:
            report_data = {
                'id': str(report['_id']),
                'type': 'rescue',
                'animal_type': report.get('animal_type', ''),
                'breed': report.get('breed', ''),
                'color': report.get('color', ''),
                'condition': report.get('condition', ''),
                'urgency': report.get('urgency', ''),
                'location': report.get('location', ''),
                'city': report.get('city', ''),
                'contact_name': report.get('contact_name', ''),
                'contact_phone': report.get('contact_phone', ''),
                'contact_email': report.get('contact_email', ''),
                'description': report.get('description', ''),
                'special_marks': report.get('special_marks', ''),
                'report_date': report.get('report_date', ''),
                'image_path': report.get('image_path', ''),
                'created_at': report.get('created_at', '').strftime('%Y-%m-%d') if report.get('created_at') else ''
            }
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
        
        if report_type == 'found':
            if action == 'approve':
                result = PetFound.approve(report_id)
            elif action == 'reject':
                result = PetFound.reject(report_id)
            else:
                return JsonResponse({"error": "Invalid action"}, status=400)
        elif report_type == 'rescue':
            if action == 'approve':
                result = Rescue.approve(report_id)
            elif action == 'reject':
                result = Rescue.reject(report_id)
            else:
                return JsonResponse({"error": "Invalid action"}, status=400)
        else:
            return JsonResponse({"error": "Invalid report type"}, status=400)
        
        if action == 'approve':
            if result.modified_count > 0:
                return JsonResponse({"success": True, "message": f"Report approved successfully"})
            else:
                return JsonResponse({"error": "Report not found or already processed"}, status=404)
        elif action == 'reject':
            if result.deleted_count > 0:
                return JsonResponse({"success": True, "message": f"Report rejected and deleted successfully"})
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


# ===== AI CHATBOT API WITH GOOGLE GEMINI =====
from google import genai
from google.genai import types
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat_api(request):
    """
    API endpoint for AI chatbot using Google Gemini
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        # Configure Google Gemini API
        GEMINI_API_KEY = "AIzaSyCNWnHTt03MBKLx1m6NHBFkjlHVl-tdbEo"
        
        # Initialize client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # STRICT system prompt - ONLY answer pet/animal questions
        system_instruction = """You are PetCare AI, a STRICT expert assistant that ONLY answers questions about animals and pets.

        IMPORTANT RULES:
        1. ONLY answer questions related to:
           - Pets (dogs, cats, birds, rabbits, hamsters, fish, reptiles, etc.)
           - Animal care, health, nutrition, behavior
           - Pet training, grooming, adoption
           - Wildlife and animal rescue
           - Veterinary topics (general advice only)
        
        2. If the question is NOT about animals/pets, you MUST respond with:
           "I'm sorry, but I can only answer questions related to pets and animals. 🐾 Please ask me about pet care, animal health, training, nutrition, or any animal-related topics!"
        
        3. DO NOT answer questions about:
           - Technology, programming, math, science (unless related to animals)
           - Politics, history, geography (unless related to animals)
           - Entertainment, sports, cooking (unless related to pet food)
           - Any other non-animal topics
        
        4. Be friendly but firm - redirect ALL non-animal questions
        5. Keep responses concise (2-4 sentences)
        6. Use emojis: 🐾, 🐕, 🐱, 🐦, 🐰, etc.
        7. For medical emergencies, recommend consulting a veterinarian"""
        
        # Generate response using new API
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=1024,
            )
        )
        
        bot_response = response.text
        
        return JsonResponse({
            'success': True,
            'response': bot_response
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': 'Sorry, I encountered an error. Please try again.'
        }, status=500)
