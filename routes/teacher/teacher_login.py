from flask import Blueprint, request, jsonify,current_app
from flask_jwt_extended import create_access_token,jwt_required
from datetime import datetime
from dbms.db import db
import time
from utils.validators import is_valid_email,is_valid_mobile,is_valid_password
from utils.rate import limiter
from models.teacher import Teacher
from models.institute import Institution
from utils.security import verify_password,generate_password_hash
from utils.extensions import redis_client

teacher_login_bp=Blueprint("teacher_login_bp",__name__,url_prefix="/teacher/auth")
@teacher_login_bp.route("/login",methods=["POST"]
)
@limiter.limit("3 per minute")
def teacher_login():
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    email=data.get("email")
    mobile_no=data.get("mobile_no")
    if email and mobile_no:
        return jsonify({
            "success":False,
            "message":"Either email or mobile no is required ,not both"
        }),400
    if not email and not mobile_no:
        return jsonify({
            "success":False,
            "message":"Either email or mobile no is required for login"
        }) ,400
    if email:
        email=email.lower()
        if not is_valid_email(email):
                return jsonify({
                    "success":False,
                    "message":"Invalid email format"
                }),400
        teacher=Teacher.query.filter_by(
            email=email).first()

        if not teacher:
            return jsonify({
                "success":False,
                "message":"Invalid credentials"
            })  ,401
    if mobile_no:
        if not is_valid_mobile(mobile_no):
            return jsonify({
                "success":False,
                "message":"Invalid mobile no.. format"
            }) ,400
        teacher=Teacher.query.filter_by(
            mobile_no=mobile_no
        ).first()
        if not teacher:
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400
    password=data.get("password")
    if not password:
        return jsonify({
            "success":False,
            "message":"Password is required for login"
        }),400

    if not teacher.login_enabled:
         return jsonify({
            "success": False,
            "message": "teacher login is not enabled. Please contact your institute."
        }), 403
    if not teacher.password:
        return jsonify({
            "success":False,
            "message":"Password is not set by Owner ,Please contact your institute "
        })  ,400
    if not verify_password(teacher.password, password):
      return jsonify({
        "success": False,
        "message": "Invalid credentials"
    }), 400
    if not teacher.is_active:
       return jsonify({
        "success": False,
        "message": "Your account has been deactivated. Please contact your institute."
    }), 403
    access_token=create_access_token(
        identity=str(teacher.id),
        additional_claims={
            "role":"teacher"
        }
    )    
    return jsonify({
        "success": True,
        "message": "Teacher login successful",
        "access_token": access_token,
        "teacher": teacher.to_dict()
    }), 200   

#teacher logout
@teacher_login_bp.route("/logout/<int:teacher_id>",methods=["POST"])
@jwt_required()
def teacher_logout(teacher_id):
    current_teacher_id=int(get_jwt_identity())
    teacher = Teacher.query.get(current_teacher_id)
    if not teacher:
      return jsonify({
        "success": False,
        "message": "Teacher not found"
    }), 404 
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
        "message":"Teacher logged out successfully"
    }),200
    