from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.student import Student

student_result_bp = Blueprint(
    "student_result_bp",
    __name__,
    url_prefix="/student/result"
)


@student_result_bp.route("/<int:assignment_id>", methods=["GET"])
@jwt_required()
def student_result(assignment_id):

    # Role check
    if get_jwt().get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    current_student_id = int(get_jwt_identity())

    # Student check
    student = Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    # Assignment check
    assignment = Assignment.query.filter_by(
        id=assignment_id
    ).first()

    if not assignment:
        return jsonify({
            "success": False,
            "message": "Assignment not found"
        }), 404

    # Authorization
    if assignment.batch_id != student.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized to view this assignment"
        }), 403

    if assignment.institution_id != student.institution_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized to view this assignment"
        }), 403

    # Submission
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id,
        student_id=student.id
    ).first()

    if not submission:
        return jsonify({
            "success": False,
            "message": "Assignment submission not found"
        }), 404

    # Result not checked yet
    if submission.status != "Checked":
        return jsonify({
            "success": False,
            "message": "Assignment has not been checked yet"
        }), 400

    # Success
    return jsonify({
        "success": True,
        "message": "Assignment result fetched successfully",
        "result": {
            "assignment_id": assignment.id,
            "assignment_title": assignment.title,
            "submission_id": submission.id,
            "marks": submission.marks,
            "feedback": submission.feedback,
            "status": submission.status
        }
    }), 200