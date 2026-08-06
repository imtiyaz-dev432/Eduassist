import requests
from celery import shared_task
import os
from dotenv import load_dotenv
from dbms.db import db
from models.fee import Fee
from models.student import Student
from datetime import datetime, timedelta
from models.fee_reminder import FeeReminder 
from utils.notificationo_helper import create_notification

# YE LINE BAHUT ZAROORI HAI CELERY KE LIYE
load_dotenv() 

@shared_task()
def send_async_otp_email(email, otp, purpose="verification"):
    if purpose == "verification":
        subject = "Verify your email - EduAssist "
        body = f"Welcome to EduAssist AI! Your account verification OTP is: {otp}. This code is valid for 5 minutes."
    elif purpose == "forgot-password":
        subject = "Reset your password - EduAssist "
        body = f"You requested a password reset. Your OTP is: {otp}. Do not share this with anyone."     
    else:
        subject = "Your OTP - EduAssist AI"
        body = f"Your OTP is: {otp}"    
        
    try:
        api_key = os.getenv("BREVO_API_KEY")
        from_name = os.getenv("FROM_NAME", "EduAssist")    
        from_email = os.getenv("FROM_EMAIL")
        
        # Checking variables
        if not api_key:
            print(" ERROR: BREVO_API_KEY missing in .env file!")
            return False
        if not from_email:
            print(" ERROR: FROM_EMAIL missing in .env file!")
            return False
            
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {
                "name": from_name,
                "email": from_email
            },
            "to": [{"email": email}],
            "subject": subject,
            "textContent": body
        }
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        print(f" Sending email to {email}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # YE ASLI ERROR BATAYEGA
        print(f"Brevo Status: {response.status_code}")
        print(f"Brevo Response: {response.text}")
        
        if response.status_code not in [200, 201, 202]:
            return False
        return True
        
    except Exception as e:
        print(" Email sending failed (Exception):", str(e))
        return False


@shared_task(name='utils.email_otp.generate_fee_notifications')
def generate_fee_notifications():
    
    pending_fees = Fee.query.filter(
        Fee.due_amount > 0
    ).all()
    
    if not pending_fees:
        return "No pending fees!"

    now = datetime.utcnow()
    forty_eight_hours_ago = now - timedelta(hours=48)
    count = 0

    for fee_record in pending_fees:
        
        last_reminder = FeeReminder.query.filter_by(
            fee_id=fee_record.id
        ).order_by(FeeReminder.created_at.desc()).first()
        
        
        if not last_reminder or last_reminder.created_at < forty_eight_hours_ago:

            alert_msg = f"Reminder: Your fee of ₹{fee_record.due_amount} is pending. Please pay soon."
            
            new_reminder = FeeReminder(
                institution_id=fee_record.institution_id,
                student_id=fee_record.student_id,
                fee_id=fee_record.id,
                reminder_date=now.date(),
                message=alert_msg,
                status="Sent",
                sent_at=now
            )
            
            db.session.add(new_reminder)
            
            
            create_notification(fee_record.student_id, alert_msg) 
            
            count += 1

    if count > 0:
        db.session.commit()

    return f"Created {count} fee reminders and web notifications successfully."
        