from flask import Blueprint, request, jsonify,current_app
from datetime import datetime,timedelta
from dbms.db import db
from utils.security import verify_otp,hash_otp
from utils.otp import generate_otp
from models.user import User
from utils.rate import limiter
from utils.validators import is_valid_email,is_valid_mobile
from utils.extensions import redis_client
from utils.email_otp import send_async_otp_email
  
otp_bp = Blueprint("otp_bp", __name__, url_prefix="/otp")
@otp_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("3 per 10 minutes")
def otp_verify():
    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    email=data.get("email")
    mobile_no=data.get("mobile_no"
    )
    if not email and not mobile_no:
        return jsonify({
            "success":False,
            "message":"Either email or mobile no is required for verifying"
        }),400
    if email and mobile_no:
        return jsonify({
            "success":False,
            "message":"Either email or mobile no.. is required for verifying ,not both"
        }),400
    if email:   
        if not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Incorrect email format"
            }) ,400

        user=User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400
    if mobile_no:
        if not is_valid_mobile(mobile_no):
            return jsonify({
                "success":False,
                "message":"Incorrect Mobile no format"
            }) ,400

        user=User.query.filter_by(mobile_no=mobile_no).first()
        if not user:
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400

    otp = data.get("otp")
    if not otp:
        return jsonify({
            "success":False,
            "message":"Otp is required for verifying"
        }),400

    if user.is_verified:
        return jsonify({
                "success": True,

            "message": "User is already verified"
        }), 200
    identifier=email.lower() if email else mobile_no    
    stored_otp=redis_client.get(f"otp:{identifier}")
    if not stored_otp:
        return jsonify({
            "success":False,
            "message":"OTP expired or not found"
        }),400

    if stored_otp!=str(otp):      
             return jsonify({
            "message":"Invalid OTP"
    
      }),400
    try:

       user.is_verified = True
       user.otp = None
       user.otp_created_at = None
       user.otp_expires_at = None
       db.session.commit()
       return jsonify({
        "message": "User verified successfully",
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
        f"OTP verification failed: {str(e)}",
        exc_info=True)
        return jsonify({
            "success": False,
        "message": "Something went wrong. Please try again later."
    }), 500      
 
#Resend otp Route
@otp_bp.route("/resend-otp",methods=["POST"])
@limiter.limit("3 per 10 minutes")
def resend_otp():
    data=request.get_json()
    if not data:
        return jsonify({
            "message":"request body is required"
        }),400
    identifier=data.get("identifier").lower()
    if not identifier:
        return jsonify({
            "message":"mobile no and email is required"
        }),400

    user=User.query.filter((User.email==identifier) | (User.mobile_no==identifier)).first()
    if not user:
        return jsonify({
            "message":"User not found"
        })  ,404

    if user.is_verified:
        return jsonify({
            "message":"User is already verified"
        })    ,400

    plain_otp=generate_otp()
    print(plain_otp)
    send_async_otp_email.delay(user.email,plain_otp,purpose="verification")
    redis_client.setex(
        f"otp:{identifier}",
        300,
        str(plain_otp)
    )
    return jsonify({
        "message":"New otp sent successfully"
    }),200