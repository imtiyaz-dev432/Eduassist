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

student_result_bp=Blueprint("student_result_bp",__name__,url_prefix="/student/result")
@student_result_bp.route("/<int:assignment_id>",methods=["GET"])
@jwt_required()
def student_result(assignment_id):
    current_student_id=int(get_jwt_identity())
    claims=get_jwt()
    if claims.get("role")!="student":
        return jsonify({
            "success":False,
            "message":"Student access only"
        }),403
    student=Student.query.filter_by(
        id=current_student_id
    ).first()
    if not student:
        return jsonify({
            "success":False,
            "message":"Student  not found"}),404 
    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()
    if not assignment:
     return jsonify({
        "success":False,
        "message":"Assignment not found"
    }),404
    if assignment.status.lower()!="checked":
        return jsonify({
            "success":False,
            "message":"Assignment not checked"
        })        ,400
  
    if student.batch_id!=assignment.batch_id:
        return jsonify({
            "success":False,
            "message":"Unauthorized to fetch the assignment"
        }),403    
    if student.institution_id!=assignment.institution_id:
        return jsonify({
            "success":False,
            "message":"Unauthorized to fetch the assignment"
        }),403           
    submission=AssignmentSubmission.query.filter_by(
        student_id=student.id,
        assignment_id=assignment.id
    ).first()
    
    if not submission:
        return jsonify({
            "success":False,
            "message":"Assignment submission not found"
        }),400
    
    return jsonify({
        "assignment_title":assignment.title,
        "marks":submission.marks,
        "feedback":submission.feedback,
        "status":assignment.status
    }),200