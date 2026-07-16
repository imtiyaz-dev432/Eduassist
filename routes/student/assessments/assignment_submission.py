import os
from datetime import date

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    url_for,
    send_from_directory
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)

from dbms.db import db

from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

from utils.file_upload import save_pdf


student_assignment_submission_bp = Blueprint(
    "student_assignment_submission_bp",
    __name__,
    url_prefix="/student/assessments/assignment_submission"
)


@student_assignment_submission_bp.route(
    "/submit/<int:assignment_id>",
    methods=["POST"]
)
@jwt_required()
def submit_assignment(assignment_id):

    # ---------------- Role Check ---------------- #

    if get_jwt().get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    # ---------------- Student Check ---------------- #

    current_student_id = int(get_jwt_identity())

    student = Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    # ---------------- Assignment Check ---------------- #

    assignment = Assignment.query.filter_by(
        id=assignment_id
    ).first()

    if not assignment:
        return jsonify({
            "success": False,
            "message": "Assignment not found"
        }), 404

    # ---------------- Batch Check ---------------- #

    if assignment.batch_id != student.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized to submit this assignment"
        }), 403

    # ---------------- Already Submitted ---------------- #

    existing_submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id,
        student_id=student.id
    ).first()

    if existing_submission:
        return jsonify({
            "success": False,
            "message": "Assignment already submitted"
        }), 400

    # ---------------- File Check ---------------- #

    uploaded_file = request.files.get("file")

    if not uploaded_file:
        return jsonify({
            "success": False,
            "message": "Assignment PDF is required"
        }), 400

    # ---------------- Save PDF ---------------- #

    try:

        saved_pdf = save_pdf(
            uploaded_file,
            current_app.config["ASSIGNMENT_UPLOAD_FOLDER"]
        )

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception:

        current_app.logger.exception("Unable to save assignment PDF")

        return jsonify({
            "success": False,
            "message": "Unable to save assignment PDF"
        }), 500

    # ---------------- File URL ---------------- #

    file_url = url_for(
        "student_assignment_submission_bp.download_assignment_pdf",
        assignment_submission_id=0
    ).replace("/0", f"/{saved_pdf['stored_filename']}")

    # ---------------- Submission Status ---------------- #

    submission_status = "Submitted"

    if assignment.due_date:

        if date.today() > assignment.due_date:
            submission_status = "Late Submitted"

    # ---------------- Save Submission ---------------- #

    new_submission = AssignmentSubmission(

        assignment_id=assignment.id,

        institution_id=assignment.institution_id,

        course_id=assignment.course_id,

        batch_id=assignment.batch_id,

        student_id=student.id,

        file_url=file_url,

        stored_filename=saved_pdf["stored_filename"],

        # original_filename=saved_pdf["original_filename"],

        status=submission_status
    )

    try:

        db.session.add(new_submission)

        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception("Database Error")

        return jsonify({
            "success": False,
            "message": "Failed to submit assignment"
        }), 500

    # ---------------- Success ---------------- #

    return jsonify({

        "success": True,

        "message": "Assignment submitted successfully",

        "submission_id": new_submission.id,

        "file_name": new_submission.stored_filename,

        "status": new_submission.status,

        "download_url": new_submission.file_url

    }), 201

@student_assignment_submission_bp.route(
    "/my-submissions",
    methods=["GET"]
)
@jwt_required()
def my_submissions():

    student_id = int(get_jwt_identity())

    submissions = AssignmentSubmission.query.filter_by(
        student_id=student_id
    ).all()


    data = []

    for submission in submissions:
        data.append({
            "submission_id": submission.id,
            "assignment_id": submission.assignment_id,
            "file_name": submission.stored_filename,
            "download_url": url_for(
    "student_assignment_submission_bp.download_assignment_pdf",
    assignment_submission_id=submission.id
),

             "submission_id":submission.id    
            
        })


    return jsonify({
        "success": True,
        "data": data
    })       
import os     
#file download 
@student_assignment_submission_bp.route(
    "/download/<int:assignment_submission_id>",
    methods=["GET"]
)
@jwt_required()
def download_assignment_pdf(assignment_submission_id):

    # ---------------- Role Check ---------------- #

    if get_jwt().get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    # ---------------- Student Check ---------------- #

    current_student_id = int(get_jwt_identity())

    student = Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    # ---------------- Submission Check ---------------- #

    submission = AssignmentSubmission.query.filter_by(
        id=assignment_submission_id
    ).first()

    if not submission:
        return jsonify({
            "success": False,
            "message": "Submission not found"
        }), 404

    # ---------------- Ownership Check ---------------- #

    if submission.student_id != student.id:
        return jsonify({
            "success": False,
            "message": "Unauthorized access"
        }), 403

    # ---------------- File Exists Check ---------------- #

    file_path = os.path.join(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        submission.stored_filename
    )

    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "PDF file not found"
        }), 404

    # ---------------- Download ---------------- #

    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        submission.stored_filename,
        mimetype="application/pdf",
        as_attachment=False
    )