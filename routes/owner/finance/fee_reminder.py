from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from dbms.db import db
from models.institute import Institution
from models.student import Student
from models.fee import Fee
from models.fee_reminder import FeeReminder

fee_reminder_bp = Blueprint("fee_reminder_bp", __name__, url_prefix="/owner/fee_reminder")


@fee_reminder_bp.route("/add/<int:fee_id>", methods=["POST"])
@jwt_required()
def fee_reminder(fee_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"success": False, "message": "Owner access only"}), 403 
        
    current_user_id = int(get_jwt_identity())
    
    fee = Fee.query.filter_by(id=fee_id).first()
    if not fee:
        return jsonify({"success": False, "message": "Fee not found"}), 404

    institute = Institution.query.filter_by(id=fee.institution_id, user_id=current_user_id).first()
    if not institute:
        return jsonify({"success": False, "message": "Institute not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400
    
    reminder_date = data.get("reminder_date")
    message = data.get("message")
    
    if not reminder_date:
        return jsonify({"success": False, "message": "Reminder date is required"}), 400

    # Date Validation
    try:
        reminder_date_obj = datetime.strptime(reminder_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if not message:
        message = f"Your pending fee amount is ₹{fee.due_amount}. Please pay before the due date."

    try:
        new_reminder = FeeReminder(
            institution_id=fee.institution_id,
            student_id=fee.student_id,
            fee_id=fee.id,
            reminder_date=reminder_date_obj,
            message=message,
            status="Pending"
        )    
        db.session.add(new_reminder)
        db.session.commit()
        return jsonify({"success": True, "message": "Fee Reminder created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500


@fee_reminder_bp.route("/get/<int:fee_id>", methods=["GET"])
@jwt_required()
def get_reminder(fee_id):
    current_user_id = int(get_jwt_identity())
    
    fee = Fee.query.filter_by(id=fee_id).first()
    if not fee:
        return jsonify({"success": False, "message": "Fee not found"}), 404
        
    institute = Institution.query.filter_by(id=fee.institution_id, user_id=current_user_id).first()
    if not institute:
        return jsonify({"success": False, "message": "Institute not found"}), 404

    fees_reminders = FeeReminder.query.filter_by(fee_id=fee_id).all()
    fee_reminder_list = [reminder.to_dict() for reminder in fees_reminders]

    return jsonify({
        "success": True,
        "message": "Data fetched successfully",
        "fee_reminder_list": fee_reminder_list
    }), 200


@fee_reminder_bp.route("/update/<int:fee_reminder_id>", methods=["PATCH"])
@jwt_required()
def update_fee_reminder(fee_reminder_id):
    current_user_id = int(get_jwt_identity())

    reminder = FeeReminder.query.filter_by(id=fee_reminder_id).first()
    if not reminder:
        return jsonify({"success": False, "message": "Fee reminder not found"}), 404

    institute = Institution.query.filter_by(id=reminder.institution_id, user_id=current_user_id).first()
    if not institute:
        return jsonify({"success": False, "message": "Unauthorized to update this fee reminder"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400

    reminder_date = data.get("reminder_date")
    message = data.get("message", reminder.message)
    status = data.get("status", reminder.status)

    allowed_status = ["Pending", "Sent", "Failed", "Cancelled"]
    if status not in allowed_status:
        return jsonify({"success": False, "message": "Invalid reminder status"}), 400

    try:
        if reminder_date:
            reminder.reminder_date = datetime.strptime(reminder_date, "%Y-%m-%d").date()

        reminder.message = message
        reminder.status = status

        if status == "Sent":
            reminder.sent_at = datetime.utcnow()

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Fee reminder updated successfully",
            "reminder": reminder.to_dict()
        }), 200
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error"}), 500


@fee_reminder_bp.route("/delete/<int:fee_reminder_id>", methods=['DELETE'])
@jwt_required()
def delete_fee(fee_reminder_id):
    current_user_id = int(get_jwt_identity()) 
    
    reminder = FeeReminder.query.filter_by(id=fee_reminder_id).first()
    if not reminder:
        return jsonify({"success": False, "message": "Reminder not found"}), 404
    
    institute = Institution.query.filter_by(id=reminder.institution_id, user_id=current_user_id).first()
    if not institute:
        return jsonify({"success": False, "message": "Unauthorized to delete this reminder"}), 403

    try:
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({"success": True, "message": "Reminder deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error"}), 500