from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from flask import Blueprint, request, jsonify,url_for,send_from_directory,current_app
from dbms.db import db
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models.student import Student
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission

student_assignment_bp = Blueprint(
    "student_assignment_bp",
    __name__,
    url_prefix="/student/assessments/assignment"
)

@student_assignment_bp.route("/my", methods=["GET"])
@jwt_required()
def my_assignments():
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403
    current_student_id = int(get_jwt_identity())
    student = Student.query.filter_by(id=current_student_id).first()
    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404
    assignments = Assignment.query.filter_by(
        batch_id=student.batch_id,
        status="Active"
    ).all()
    data = []
    for assignment in assignments:
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        data.append({
            "assignment_id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "max_marks": assignment.max_marks,

            # Teacher assignment file
            "assignment_file_url": assignment.file_url,

            # Submission
            "is_submitted": submission is not None,
            "submission_id": submission.id if submission else None,
            "submission_status": submission.status if submission else None,

            # Result
            "marks": submission.marks if submission else None,
            "feedback": submission.feedback if submission else None
        })

    return jsonify({
        "success": True,
        "message": "Assignments fetched successfully",
        "assignments": data
    }), 200

#file
@student_assignment_bp.route("/file/<string:filename>", methods=["GET"])
@jwt_required()
def download_assignment_pdf(filename):
    assignment = Assignment.query.filter_by(
        file_url=filename
    ).first()

    if not assignment:
        return jsonify({
            "success": False,
            "message": "Assignment file not found"
        }), 404

    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    student = Student.query.get(current_user_id)

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    if student.batch_id != assignment.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized - not your batch"
        }), 403

    if assignment.status != "Active":
        return jsonify({
            "success": False,
            "message": "Assignment is not active"
        }), 403

    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename,
        mimetype="application/pdf"
    )