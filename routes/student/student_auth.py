from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token,jwt_required,get_jwt,get_jwt_identity
from werkzeug.security import check_password_hash
import time
from models.student import Student
from utils.rate import limiter
from utils.validators import is_valid_email,is_valid_mobile
from utils.extensions import redis_client
student_auth_bp=Blueprint("student_auth_bp",__name__,url_prefix="/student_auth")
@student_auth_bp.route("/login",methods=["POST"])
@limiter.limit("3 per minute")
def login_student():
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    email=data.get("email")
    phone=data.get("phone")
    if email and phone:
        return jsonify({
            "success":False,
            "message":"Either email or mobile no.. is required ,not both"
        })  ,400
    if not email and not phone: 
        return jsonify({
            "success":False,
            "message":"Either email or phone is required for login only one field are required"
        }),400
    if email:
        email=email.lower()
        if not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Invalid Email Format"
            }) ,400
        student=Student.query.filter_by(email=email).first()
        if not student:
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400
    if phone:
        if not is_valid_mobile(phone):
            return jsonify({
                "success":False,
                "message":"Invalid Mobile no.. Format"
            })   ,400
        student=Student.query.filter_by(phone=phone).first()
        if not student:
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }) ,400         
    password=data.get("password")
    if not password:
        return jsonify({
            "success":False,
            "message":"Email/Mobile and password is required"
        }),400
    if not student.is_login_enabled:
        return jsonify({
            "success": False,
            "message": "Student login is not enabled. Please contact your institute."
        }), 403

    if not student.password_hash:
        return jsonify({ "success": False,
            "message": "Student password is not set. Please contact your institute."
        }), 403
    if not check_password_hash(student.password_hash, password):
        return jsonify({
            "success": False,
            "message": "Invalid phone/email or password"
        }), 401

    access_token = create_access_token(
        identity=str(student.id),
        additional_claims={
            "role": "student"
        }
    )

    return jsonify({
        "success": True,
        "message": "Student login successful",
        "access_token": access_token,
        "student": student.to_dict()
    }), 200        
#student logout
@student_auth_bp.route("/logout",methods=["POST"])
@jwt_required()
def student_logout():
    current_student_id=int(get_jwt_identity())    
    student = Student.query.get(current_student_id)
    if not student:
      return jsonify({
        "success": False,
        "message": "Student not found"
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
        "message":"Student logged out successfully"
    }),200