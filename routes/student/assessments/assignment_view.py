from flask import Blueprint, request, jsonify,url_for,send_from_directory,current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from dbms.db import db
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

student_assignment_bp=Blueprint("student_assignment_bp",__name__,url_prefix="/student/assessments/assignment")
# raise Exception("assignment_view imported")
print("assignment_view.py loaded")

# @student_assignment_bp.route("/file/<string:filename>", methods=["GET"])
# @jwt_required()
@student_assignment_bp.route("/file/<string:filename>", methods=["GET"])
@jwt_required()
def download_assignment_pdf(filename):
    assignment = Assignment.query.filter(
        Assignment.file_url.like(f"%/{filename}")
    ).first()

    if not assignment:
        return jsonify({
            "success": False,
            "message": "Assignment file not found"
        }), 404

    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role == "student":
        student = Student.query.get(current_user_id)

        is_authorized = (
            student is not None
            and student.batch_id == assignment.batch_id
            and assignment.status == "Active"
        )
    else:
        is_authorized = False

    if not is_authorized:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename,
        mimetype="application/pdf"
    )
# def download_assignment_pdf(filename):
#     file_url= url_for(
#     "student_assignment_bp.download_assignment_pdf",
#     filename=filename
# ) 
#     assignment = Assignment.query.filter_by(file_url=file_url).first()

#     if not assignment:
#         return jsonify({
#             "success": False,
#             "message": "Assignment file not found"
#         }), 404
#     print(file_url)
#     print("========== ROUTE HIT ==========")
#     print("Filename:", filename)

#     return jsonify({"ok": True})

#     assignments = Assignment.query.all()
#     print("Total Assignments:", len(assignments))

#     for a in assignments:
#        print(a.id, a.file_url)   
#        current_user_id = int(get_jwt_identity())
#        role = get_jwt().get("role")

#     if role == "student":
#         student = Student.query.filter_by(id=current_user_id).first()
#         is_authorized = (
#             student is not None
#             and student.batch_id == assignment.batch_id
#             and assignment.status == "Active"
#         )
#     else:
#         is_authorized = False

#     if not is_authorized:
#         return jsonify({
#             "success": False,
#             "message": "Unauthorized to access this assignment file"
#         }), 403

#     return send_from_directory(
#         current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
#         filename,
#         mimetype="application/pdf"
#     )
