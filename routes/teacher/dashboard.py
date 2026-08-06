from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from dbms.db import db

# Import your models
from models.batch import Batch
from models.student import Student
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.quize import Quiz # Note: you spelled this quize.py in your imports earlier

teacher_dashboard_bp = Blueprint("teacher_dashboard_bp", __name__, url_prefix="/teacher/dashboard")

@teacher_dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_teacher_dashboard():
    # 1. Security Check: Only Teachers allowed
    claims = get_jwt()
    if claims.get("role") != "teacher":
        return jsonify({
            "success": False,
            "message": "Teacher access only"
        }), 403

    current_teacher_id = int(get_jwt_identity())

    try:
        # 2. Fetch all batches assigned to this teacher
        teacher_batches = Batch.query.filter_by(teacher_id=current_teacher_id).all()
        
        if not teacher_batches:
            return jsonify({
                "success": True,
                "message": "Welcome! You haven't been assigned to any batches yet.",
                "data": {
                    "metrics": {
                        "total_batches": 0,
                        "total_students": 0,
                        "pending_grading": 0
                    },
                    "my_batches": []
                }
            }), 200

        # Extract just the IDs of the batches to use in our next queries
        batch_ids = [batch.id for batch in teacher_batches]

        # 3. Calculate Core Metrics using SQL's "IN" clause
        # Count all students enrolled in ANY of this teacher's batches
        total_students = Student.query.filter(Student.batch_id.in_(batch_ids)).count()

        # Count how many assignment submissions are waiting to be checked
        pending_grading = AssignmentSubmission.query.filter(
            AssignmentSubmission.batch_id.in_(batch_ids),
            AssignmentSubmission.status == "Submitted" # Assuming "Checked" is for graded ones
        ).count()

        # 4. Format the batch list for the UI
        batch_list = []
        for batch in teacher_batches:
            batch_list.append({
                "batch_id": batch.id,
                "batch_name": batch.batch_name,
                "status": batch.status,
                "total_seats": batch.total_seats
            })

        # 5. Return the aggregated data
        return jsonify({
            "success": True,
            "message": "Teacher dashboard fetched successfully",
            "data": {
                "metrics": {
                    "total_batches": len(batch_ids),
                    "total_students": total_students,
                    "pending_grading": pending_grading
                },
                "my_batches": batch_list
            }
        }), 200

    except Exception:
        current_app.logger.exception("Failed to fetch teacher dashboard data")
        return jsonify({
            "success": False,
            "message": "Server error while fetching dashboard data"
        }), 500