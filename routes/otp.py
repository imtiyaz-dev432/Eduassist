from flask import Blueprint, request, jsonify
from datetime import datetime,timedelta
from dbms.db import db
from utils.security import verify_otp,hash_otp
from utils.otp import generate_otp
from models.user import User
  
otp_bp = Blueprint("otp_bp", __name__, url_prefix="/otp")
@otp_bp.route("/verify-otp", methods=["POST"])
def otp_verify():
    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    identifier = data.get("identifier")
    otp = data.get("otp")

    if not identifier or not otp:
        return jsonify({
            "message": "Identifier and OTP are required"
        }), 400

    if "@" in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(mobile_no=identifier).first()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if user.is_verified:
        return jsonify({
                "success": True,

            "message": "User is already verified"
        }), 200

    if not user.otp or not user.otp_expires_at:
        return jsonify({
            "message": "OTP not found. Please request new OTP"
        }), 400

    if datetime.utcnow() > user.otp_expires_at:
        return jsonify({
            "message": "OTP expired. Please request new OTP"
        }), 400

    if not verify_otp(user.otp, otp):
        return jsonify({
            "message": "Invalid OTP"
        }), 400

    user.is_verified = True
    user.otp = None
    user.otp_created_at = None
    user.otp_expires_at = None

    db.session.commit()

    return jsonify({
        "message": "User verified successfully",
        
    }), 200

#Resend otp Route
@otp_bp.route("/resend-otp",methods=["POST"])
def resend_otp():
    data=request.get_json()
    if not data:
        return jsonify({
            "message":"request body is required"
        }),400
    identifier=data.get("identifier")
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
    hashed_otp=hash_otp(plain_otp)
    now=datetime.utcnow()
    user.otp=hashed_otp 
    user.otp_created_at=now
    user.otp_expires_at=now+timedelta(minutes=5)
    db.session.commit()
    return jsonify({
        "message":"New otp sent successfully"
    }),200