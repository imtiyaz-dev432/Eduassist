import time
from flask import Blueprint,request,jsonify
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from datetime import datetime ,timedelta
from dbms.db import db
from datetime import timedelta
from models.user import User
from utils.security import hash_otp,hash_password,verify_password,verify_otp
from utils.otp import generate_otp
from utils.rate import limiter
from utils.validators import is_valid_email,is_valid_password,is_valid_mobile
from utils.extensions import redis_client
from utils.email_otp import send_async_otp_email


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
    if not is_valid_mobile(mobile_no):
        return jsonify({
            "success":False,
            "message":"Invalid Mobile No.."
        }),400
    
    if not is_valid_email(email):
        return jsonify({
            "success":False,
            "message":"Invalid Email"
        }),400
    if not is_valid_password(password):
        return jsonify({
            "success":False,
            "message":("Password must be at least 8 characters long and include an"
              " uppercase letter, lowercase letter, number, and special"
              " character (@$!%*?&)" 
        ),}),400
    existing_user = User.query.filter(
    (User.email == email) | (User.mobile_no == mobile_no)).first()

    if existing_user:
       return jsonify({
        "success": False,
        "message": "Email or mobile number is already registered"
    }), 409
    plain_otp=generate_otp()
    print(plain_otp)
    hashed_otp=hash_otp(plain_otp)
    identifier = email.lower() if email else mobile_no
    redis_client.setex(
        f"otp:{identifier}",
        300,
        str(plain_otp)
    )
    now=datetime.utcnow()
    new_user=User(
        name=name,
        email=email,
        mobile_no=mobile_no,
        
        password=hash_password(password),
        is_verified=False

    )

    db.session.add(new_user)
    try:
       db.session.commit()
       send_async_otp_email.delay(email, plain_otp, purpose="verification")
       return jsonify({
        "message":"User registered successfully"
    }),201
    except Exception as e:
        db.session.rollback()
        redis_client.delete(f"otp:{identifier}")        
        return jsonify({
            "success": False,
            "message": "Database error during registration",
            "error": str(e)
        }), 500


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

    if email and mobile_no:
        return jsonify({
            "succes":False,
            "message":"Only one field is required for login"
        }),400
    
    if mobile_no:
        if not is_valid_mobile(mobile_no):
           return jsonify({
            "success":False,
            "message":"Invalid Mobile No.."
        }),400
    if email:
        if not is_valid_email(email):
          return jsonify({
            "success":False,
            "message":"Invalid Email"
        }),400
    if not is_valid_password(password):
        return jsonify({
            "success":False,
            "message":("Password must be at least 8 characters long and include an"
              " uppercase letter, lowercase letter, number, and special"
              " character (@$!%*?&)" 
        ),}),400  


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
    email=data.get("email")
    mobile_no=data.get("mobile_no")
    
    if not email and not mobile_no:
        return jsonify({
            "success":False,
            "message":"Email/Mobile no.. is required"
        }),400
    if email and mobile_no:
      return jsonify({
        "success":False,
        "message":"Provide either email or mobile number, not both."
    }),400    
    if email:
        if not is_valid_email(email):
           return jsonify({
            "success":False,
            "message":"Invalid Email"
        }),400
        user=User.query.filter_by(
            email=email
        ).first()
        if not user:
            return jsonify({
                 "success": True,
                 "message": "If the account exists, a password reset OTP has been sent."}),200

    if mobile_no:
        if not is_valid_mobile(mobile_no):
           return jsonify({
            "success":False,
            "message":"Invalid Mobile Number"
        }),400   
        user=User.query.filter_by(
            mobile_no=mobile_no
        ).first()
        if not user:
            return jsonify({
                 "success": True,
                 "message": "If the account exists, a password reset OTP has been sent."}),200
      
    plain_otp=generate_otp ()
    print(plain_otp) ##only for development 
    send_async_otp_email.delay(user.email,plain_otp,purpose="forgot-password")
    hashed_otp=hash_otp(plain_otp)
    user.otp=hashed_otp
    now = datetime.utcnow()
    user.otp_created_at=now
    user.otp_expires_at=now+timedelta(minutes=5)
    db.session.commit()
    return jsonify({
        "success":True,

        "message":"If an account with those details exists, a password reset OTP has been sent."
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
    mobile_no=data.get("mobile_no")
    email=data.get("email")
    if not email and not mobile_no:
        return jsonify({
            "success":False,
            "message":"Provide Either email or mobile no is required"
        }),400
    if email and mobile_no:
       return jsonify({
        "success": False,
        "message": "Provide either email or mobile number, not both."
    }), 400    
    otp=data.get("otp")
    new_password=data.get("new_password")
    if not otp or not new_password:
      return jsonify({
        "success": False,
        "message": "OTP and new password are required"
    }), 400
    if not is_valid_password(new_password):
        return jsonify({
            "success":False,
            "message":("Password must be at least 8 characters long and include an"
              " uppercase letter, lowercase letter, number, and special"
              " character (@$!%*?&)" 
        ),}),400  

    if email:
        if not is_valid_email(email):
            return  jsonify({
                 "success":False,
            "message":"Invalid Email"
            }),400
        user=User.query.filter_by(
            email=email
        ).first()
        if not user:
            return jsonify({
                 "success": False,
                 "message": "Invalid Credentials or OTP."}),400    

    if  mobile_no:
        if not is_valid_mobile(mobile_no):
            return  jsonify({
                 "success":False,
            "message":"Invalid MobiLE NO.."
            }),400

        user=User.query.filter_by(
            mobile_no=mobile_no
        ).first()

        if not user:
            return jsonify({
                 "success": False,
                 "message": "Invalid credentials or OTP."}),400        
    
    if not user.otp or not user.otp_created_at or not user.otp_expires_at:
        return jsonify({
            "success":False,
            "message": "Invalid credentials or OTP"}), 400

    if  datetime.utcnow()>user.otp_expires_at :        
        return jsonify({
            "success":False,
            "message": "OTP expired. Please request a new OTP."}), 400

    if not verify_otp(user.otp, otp):

      return jsonify({
        "success":False,
        "message": "Invalid OTP"}), 400
    user.otp=None
    user.otp_created_at=None
    user.otp_expires_at=None
    user.password=hash_password(new_password)
    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Password updated successfully"
       })
    except Exception:
       db.session.rollback()
       return jsonify({
        "success": False,
        "message": "Something went wrong."
    }), 500

# logout
@auth_bp.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    token=get_jwt()
    jti=token['jti']
    ttl=max(token['exp']-int(time.time()),1)
    redis_client.setex(
    f"blocklist:{jti}",
    ttl,
    "revoked"
    )
    return jsonify ({
        "success": True,
        "message":"User logged out successfully"
    }),200