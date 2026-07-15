import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_from_directory,
    url_for,
)
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from dbms.db import db

from models.institute import Institution
from models.batch import Batch
from models.assignment_submission import AssignmentSubmission
from models.assignment import Assignment

from models.student import Student
from utils.file_upload import save_pdf


student_assignment_submission_bp=Blueprint("student_assignment_submission_bp",__name__,url_prefix="/student/assessments/assignment_submission")
@student_assignment_submission_bp.route("/submit/<int:assignment_id>",methods=["POST"])
@jwt_required()
def submit_assignment(assignment_id):
    claims=get_jwt()
    if claims.get("role")!="student":
        return jsonify({
            "success":False,
            "message":"Student access only"
        }),403
    current_student_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success":False,
            "message":"Student not found"
        }),404
    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()

    if not assignment:
        return jsonify({
            "success":False,
            "message":"Assignment not found"
        }),404

    if assignment.batch_id!=student.batch_id:
        return jsonify({
            "success":False,
            "message":"Unauthorized to submit this assignment"
        })   ,403
    submission=AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id,
        student_id=student.id
    ).first()

    if submission:
        return jsonify({
            "success":False,
            "message":"Assignment is already submitted"
        })   ,400
    data=request.get_json(silent=True) if request.is_json else request.form
    uploaded_file=request.files.get("file")
    if not data and not uploaded_file:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        })   ,400
    file_url=data.get("file_url")
    saved_pdf=None
    if uploaded_file:
        try:
            saved_pdf=save_pdf(
                uploaded_file,
                current_app.config["ASSIGNMENT_UPLOAD_FOLDER"]
            )
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except OSError:
            current_app.logger.exception("Unable to save assignment PDF")
            return jsonify({
                "success": False,
                "message": "Unable to save assignment PDF"
            }), 500
        if saved_pdf:
            file_url = url_for(
                "student_assignment_submission_bp.download_assignment_pdf",
                filename=saved_pdf["stored_filename"]
            )
    if not file_url:
      return jsonify({
        "success": False,
        "message": "Either upload a file or provide a file URL"
    }), 400

    current_time=date.today()    
    submission_status="Submitted"
    if assignment.due_date and current_time>assignment.due_date:
        submission_status="Late"
             
    new_submission = AssignmentSubmission(
                 assignment_id=assignment.id,
                 institution_id=assignment.institution_id,
                 course_id=assignment.course_id,
                 batch_id=assignment.batch_id,
                 student_id=student.id,
                 file_url=file_url,
                 stored_filename=save_pdf["stored_filename"],               
                 status=submission_status)

    try:
        db.session.add(new_submission)
        db.session.commit()
    except Exception as e :
        db.session.rollback()
        current_app.logger.exception("Database error during submission")
        return jsonify({
        "success": False,
        "message": "Failed to save submission"
    }), 500    
    return jsonify({
            "success":True,
            "message":"Pdf uploaded successfully"
        })    ,200
#file download 
@student_assignment_submission_bp.route("/download", methods=["GET"])
@jwt_required()
def download_assignment_pdf(filename):
    claims=get_jwt()
    if claims.get("role")!="student":
        return jsonify({
            "success":False,
            "message":"Student access only"
        }),403
    current_student_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success":False,
            "message":"Student not found"
        }),404
    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()

    if not assignment:
        return jsonify({
            "success":False,
            "message":"Assignment not found"
        }),404

    if assignment.batch_id!=student.batch_id:
        return jsonify({
            "success":False,
            "message":"Unauthorized to submit this assignment"
        })   ,403
         
    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )        