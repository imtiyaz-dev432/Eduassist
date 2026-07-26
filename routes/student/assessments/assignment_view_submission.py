from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from dbms.db import db
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

assignment_submission_view_bp=Blueprint("assignment_submission_view_bp",__name__,url_prefix="/student/assessments/assignment/view")
@assignment_submission_view_bp.route("/my",methods=["GET"])
@jwt_required()
def view_assignment():
    claims=get_jwt()
    if claims.get("role")!="student":
      return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403
    current_student_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return  jsonify({
            "success":False,
            "message":"Student not found"
        }),400
    submission_list = []
    submissions = AssignmentSubmission.query.filter_by(
        student_id=student.id
    ).all()
    for submission in submissions:
       assignment = Assignment.query.filter_by(
        id=submission.assignment_id
    ).first()    

       submission_list.append({
    "assignment_id": assignment.id,
    "title": assignment.title,
    "description": assignment.description,
    "due_date": assignment.due_date,
    "submitted_at": submission.submitted_at,
    "submission_status": submission.status,
    "marks": submission.marks,
    "feedback": submission.feedback
})
    return jsonify({
        "success": True,
        "message": "Assignment submissions fetched successfully",
        "submissions": submission_list
    }), 200