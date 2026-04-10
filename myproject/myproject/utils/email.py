import requests
import os


SENDER_NAME = "RescueMate"


def send_brevo_email(to_email, subject, html_content):
    """Send email via Brevo (Sendinblue) API"""
    # Read at call time so dotenv is already loaded
    api_key = os.getenv("BREVO_API_KEY", "")
    sender_email = os.getenv("SENDER_EMAIL", "")

    if not api_key:
        return 401, "BREVO_API_KEY not set in environment"

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    data = {
        "sender": {"name": SENDER_NAME, "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }

    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.text


def send_otp_email(to_email, otp):
    """Send OTP verification email"""
    subject = "Your OTP Verification Code - RescueMate"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 30px;
                border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #667eea; text-align: center;">🐾 RescueMate</h2>
        <h3 style="text-align: center;">Email Verification</h3>
        <p>Hello,</p>
        <p>Your OTP verification code is:</p>
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 2.5rem; font-weight: bold; letter-spacing: 8px;
                         color: #667eea; background: #f0f4ff; padding: 12px 24px;
                         border-radius: 8px;">{otp}</span>
        </div>
        <p style="color: #888; font-size: 0.9rem;">This code expires in <strong>10 minutes</strong>.</p>
        <p style="color: #888; font-size: 0.85rem;">If you didn't request this, please ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #aaa; font-size: 0.8rem; text-align: center;">
            RescueMate - Pet Adoption &amp; Rescue Portal
        </p>
    </div>
    """
    return send_brevo_email(to_email, subject, html_content)


def send_notification_email_brevo(to_email, user_name, title, message):
    """Send notification email via Brevo"""
    subject = f"RescueMate Notification - {title}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 30px;
                border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #667eea; text-align: center;">🐾 RescueMate</h2>
        <h3>{title}</h3>
        <p>Hello {user_name},</p>
        <p style="white-space: pre-line;">{message}</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #aaa; font-size: 0.8rem; text-align: center;">
            RescueMate - Pet Adoption &amp; Rescue Portal
        </p>
    </div>
    """
    return send_brevo_email(to_email, subject, html_content)
