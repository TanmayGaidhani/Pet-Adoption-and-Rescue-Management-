from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from .models import User
import random
import json


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
    # If already logged in, redirect to dashboard
    if "user_id" in request.session:
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
                request.session.set_expiry(3600)  # Session expires in 1 hour
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
