import os
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for, send_from_directory, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dbms.db import db
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

student_assignment_bp = Blueprint(
    "student_assignment_bp",
    __name__,
    url_prefix="/student/assessments/assignment"
)

# 1. MY ASSIGNMENTS LIST
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
    student = Student.query.get(current_student_id)
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

        # Generate complete viewable file URL for Frontend
        file_download_url = None
        if assignment.file_url:
            file_download_url = url_for(
                "student_assignment_bp.download_assignment_pdf", 
                assignment_id=assignment.id, 
                _external=True
            )

        data.append({
            "assignment_id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "max_marks": assignment.max_marks,

            # Pure filename & Full View URL
            "assignment_filename": assignment.file_url,
            "assignment_file_url": file_download_url,

            # Submission & Results
            "is_submitted": submission is not None,
            "submission_id": submission.id if submission else None,
            "submission_status": submission.status if submission else None,
            "marks": submission.marks if submission else None,
            "feedback": submission.feedback if submission else None
        })

    return jsonify({
        "success": True,
        "message": "Assignments fetched successfully",
        "assignments": data
        
    }), 200

#file download

@student_assignment_bp.route("/file/<int:assignment_id>", methods=["GET"])
@jwt_required()
def download_assignment_pdf(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    student = Student.query.get(int(get_jwt_identity()))
    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    if student.batch_id != assignment.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    if assignment.status != "Active":
        return jsonify({
            "success": False,
            "message": "Assignment is not active"
        }), 403
    if not assignment.file_url:
        return jsonify({
            "success": False,
            "message": "No file was attached to this assignment by the teacher."
        }), 404    

    filename = os.path.basename(str(assignment.file_url))

    path = os.path.join(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename
    )
    print(path)
    print("-----------------------------------------")
    print("DEBUG 1: DB se mila URL ->", assignment.file_url)
    print("DEBUG 2: Nikala gaya Naam ->", filename)
    print("DEBUG 3: Poora Rasta (Path) ->", path)
    print("DEBUG 4: Kya file sach mein hai? ->", os.path.exists(path))
    print("-----------------------------------------")

    if not os.path.exists(path):
        return jsonify({
            "success": False,
            "message": "Assignment file not found"
        }), 404
    
    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename,       
        mimetype="application/pdf"
    )