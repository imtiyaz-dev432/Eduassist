from flask import Blueprint,request,jsonify
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from datetime import datetime ,timedelta
from block import BLOCKLIST
from dbms.db import db
from models.user import User
from utils.security import hash_otp,hash_password,verify_password
from utils.otp import generate_otp
from utils.rate import limiter

auth_bp=Blueprint('auth_bp',__name__,url_prefix="/auth")
@auth_bp.route("/register",methods=["POST"])
@limiter.limit("3 per minute")
def register():
    data=request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message":"Request Body is required"
        }),400
    name=data.get("name")
    mobile_no=data.get("mobile_no")
    email=data.get("email")    
    password=data.get("password")
    if not name or not mobile_no or not email or not password:
        return jsonify({
            "message":"All fields are required"
        }),400

    existing_user = User.query.filter(
    (User.email == email) | (User.mobile_no == mobile_no)).first()

    if existing_user:
       return jsonify({
        "success": False,
        "message": "Email or mobile number is already registered"
    }), 409
    if len(password)<8:
        return jsonify({
            "success":False,
            "message":"Passwird must be of 8 character"
        }) ,403

    plain_otp=generate_otp()
    hashed_otp=hash_otp(plain_otp)
    now=datetime.utcnow()
    new_user=User(
        name=name,
        email=email,
        mobile_no=mobile_no,
        otp=hashed_otp,
        password=hash_password(password),
        otp_created_at=now,
        otp_expires_at=now+timedelta(minutes=5),
        is_verified=False

    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "message":"User registered successfully"

    }),201

#Login Route
@auth_bp.route("/login",methods=["POST"])
@limiter.limit("3 per minute")
def login():
    data=request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message":"Request body is required"
        }),400
    email=data.get("email")    
    mobile_no=data.get("mobile_no")    
    password=data.get("password")
    if not password:
        return jsonify({ "success": False,
        "message":"passwod is required for login"}),400

    if not mobile_no and not email:
        return jsonify({
             "success": False,
            "message":"Email/Mobie no is required"
        }),400

    user=User.query.filter((User.email==email) | (User.mobile_no==mobile_no)).first()

    if not user:
        return jsonify({
            "message":"Invalid email/mobile no.. or password"
        }),401
    
    if not user.is_verified:
        return jsonify({
            "success": False,
    "message": "OTP verification is required for login"
}), 403

    if not verify_password(user.password,password):
        return jsonify({
            "success": False,
            "message":"Invalid email/mobile or password"
        }),401

    access_token=create_access_token(identity=str(user.id),
    additional_claims={
        "role": "owner"
    })    

    return jsonify({
    "success": True,
    "message": "User logged in successfully",
    "access_token": access_token,
    "user": {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile_no": user.mobile_no
    }
}), 200


##FORGOT-PASSWORD
@auth_bp.route("/forgot-password",methods=["POST"])
@limiter.limit("3 per 10 minutes")
def forgot_password():
    data=request.get_json()
    if not data:
      return  jsonify({
        "success":False,
        "message":"Request body is required"
    }),400
    identifier=data.get("identifier")

    if not identifier:
        return jsonify({
            "success":False,
            "message":"Email/Mobile no.. is required"
        }),400
    user=User.query.filter((User.email==identifier) | (User.mobile_no==identifier)).first()
    if not user:
       return jsonify({
    "success": True,
    "message": "If the account exists, a password reset OTP has been sent."
}), 200
    plain_otp=generate_otp ()
    hashed_otp=hash_otp(plain_otp)
    user.otp=hashed_otp
    user.otp_created_at=datetime.utcnow()
    user.otp_expires_at=datetime.utcnow()+timedelta(minutes=5)
    db.session.commit()
    return jsonify({
        "success":True,

        "message": "Reset OTP sent to your registered email/mobile"
    }),200

#RESET-PASSWORD
@auth_bp.route("/reset-password",methods=["POST"])
@limiter.limit("3 per 10 minutes")
def reset_password():
    data=request.get_json()
    if not data:
      return  jsonify({
        "success":False,
        "message":"Request body is required"
    }),400
    identifier=data.get("identifier")
    otp=data.get("otp")
    new_password=data.get("new_password")
    if not otp or not new_password:
      return jsonify({
        "success": False,
        "message": "OTP and new password are required"
    }), 400

    if not identifier:
        return jsonify({
            "success":False,
            "message":"Email/Mobile no.. is required"
        }),400
    if len(new_password) < 8:
      return jsonify({
        "success": False,
        "message": "Password must be at least 8 characters long"
    }), 400    
    user=User.query.filter((User.email==identifier) | (User.mobile_no==identifier)).first()
    if not user:
       return jsonify({
    "success": True,
    "message": "If the account exists, a password reset OTP has been sent."
}), 200
    if not user.otp or not user.otp_created_at:
        return jsonify({
            "success":False,
            "message": "OTP not generated"}), 400

    if datetime.utcnow()>user.otp_expires_at :        
        return jsonify({
            "success":False,
            "message": "OTP expired. Please request a new OTP."}), 400

    if not verify_hashed_otp(user.otp, otp):
      return jsonify({"message": "Invalid OTP"}), 400
    user.otp=None
    user.otp_created_at=None
    user.otp_expires_at=None
    user.password=hash_password(new_password)
    db.session.commit()
    return jsonify({
        "success":True,
    "message": "Password reset successfully"
}), 200 
        

# logout
@auth_bp.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    jti=get_jwt()['jti']
    BLOCKLIST.add(jti)
    return jsonify ({
        "success": True,
        "message":"User logged out successfully"
    }),200