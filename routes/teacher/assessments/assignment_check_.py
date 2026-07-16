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
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.batch import Batch
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student
from utils.file_upload import save_pdf

teacher_see_student_bp=Blueprint("teacher_check_bp",__name__,url_prefix="/teacher/check")
@teacher_see_student_bp.route("/<int:assignment_id>",methods=["GET"])
@jwt_required()
def assignment_check(assignment_id):
    current_user_id=int(get_jwt_identity())
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403

    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()
    if not assignment:
        return  jsonify({
            "success":False,
            "message":"Assignment not found"
        })
    institute=Institution.query.filter_by(
         id=assignment.institution_id,
         user_id=current_user_id
    ).first()
    if not institute:
        return jsonify({
            "sucess":False,
            "message":"Unauthorized to fetch the data "
        }),403

    submissions=AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id
    ).all()
    submission_list=[]
    for submission in submissions:
        submission_list.append(submission.to_dict())
        
    return jsonify({
        "success":True,
        "message":"Data fetch successfully",
        "submission_list":submission_list
    })     ,200

#downlaod 
@teacher_see_student_bp.route("/file/<string:filename>", methods=["GET"])
@jwt_required()
def download_pdf(filename):

    if get_jwt().get("role") != "owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    # Find submission by stored filename
    assignment_submission = AssignmentSubmission.query.filter_by(
        stored_filename=filename
    ).first()

    if not assignment_submission:
        return jsonify({
            "success": False,
            "message": "Assignment submission not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    institute = Institution.query.filter_by(
        id=assignment_submission.institution_id,
        user_id=current_user_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    file_path = os.path.join(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        assignment_submission.stored_filename
    )
    print("Requested filename:", filename)

    assignment_submission = AssignmentSubmission.query.filter_by(
    stored_filename=filename
).first()

   

    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "PDF file not found on disk"
        }), 404

    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        assignment_submission.stored_filename,
        mimetype="application/pdf",
        as_attachment=False
    )  

#check marking 
@teacher_see_student_bp.route("/<int:assignment_submission_id>",methods=["PATCH"])
@jwt_required()
def check(assignment_submission_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    data=request.get_json()    
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    curren_user_id=int(get_jwt_identity())
    assignment_submission=AssignmentSubmission.query.filter_by(
        id=assignment_submission_id
    ).first()
    if not assignment_submission:
        return jsonify({
            "success":False,
            "message":"Assignment not fetched successfully"
        }),404
    institute=Institution.query.filter_by(
        user_id=curren_user_id,
        id=assignment_submission.institution_id
    ).first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unaouthorized to fetch the asssignmen"
        }),403
    assignment_submission.marks=data.get("marks",assignment_submission.marks)
    assignment_submission.feedback=data.get("feedback",assignment_submission.feedback)
    assignment_submission.status = "Checked"
    try:
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"Record updated successfully",
            "submission": assignment_submission.to_dict()
        }),200
    except Exception as e :
        db.session.rollback()    
        return jsonify({
            "success":False,
            "message":"Unable to update assignment submission"
        }),500
   