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
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"Owner/teacher access only"
        }),403

    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()
    if not assignment:
        return  jsonify({
            "success":False,
            "message":"Assignment not found"
        }),404
    if claims.get("role")=="owner":   
       current_user_id=int(get_jwt_identity())   
       institute=Institution.query.filter_by(
         id=assignment.institution_id,
         user_id=current_user_id
    ).first()
       if not institute:
         return jsonify({
            "sucess":False,
            "message":"Unauthorized to fetch the data "
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        batch=Batch.query.filter_by(
            id=assignment.batch_id
        ).first()
        if(not batch or batch.teacher_id!=current_teacher_id):
            return jsonify({
                "success":False,
                "message":"Unauthorized to get submissions "
            }) ,403
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
@teacher_see_student_bp.route("/file/<int:assignment_submission_id>", methods=["GET"])
@jwt_required()
def download_pdf(assignment_submission_id):
    claims=get_jwt()
    if claims.get("role") not in ["owner","teacher"]:
        return jsonify({
            "success": False,
            "message": "Owner/teacher access only"
        }), 403

    # Find submission by stored filename
    assignment_submission = AssignmentSubmission.query.get_or_404(assignment_submission_id)
    if claims.get("role")=="owner":
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
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        batch=Batch.query.filter_by(
            id=assignment_submission.batch_id
        ).first()
        if (batch.teacher_id!=current_teacher_id):
            return jsonify({
                "success":False,
                "message":"Unauthorized to fetch submissions"
            }),403

    file_path = os.path.join(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        assignment_submission.stored_filename
    )
    
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
    if claims.get("role") not in ["owner","teacher"]:
        return jsonify({
            "success":False,
            "message":"Owner/teacher access only"
        }),403
    data=request.get_json()    
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    assignment_submission=AssignmentSubmission.query.filter_by(
        id=assignment_submission_id
    ).first()
    if not assignment_submission:
        return jsonify({
            "success":False,
            "message":"Assignment not fetched successfully"
        }),404
    if claims.get("role")=="owner":
        current_user_id=int(get_jwt_identity())    
        institute=Institution.query.filter_by(
        user_id=curren_user_id,
        id=assignment_submission.institution_id
    ).first()
        if not institute:
          return jsonify({
            "success":False,
            "message":"Unaouthorized to fetch the asssignmen"
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        batch=Batch.query.filter_by(
            id=assignment_submission.batch_id
        ).first()
        if (not batch or batch.teacher_id!=current_teacher_id):
            return jsonify({
            "success":False,
            "message":"Unauthorized to check this assignment"
        }),400
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
   