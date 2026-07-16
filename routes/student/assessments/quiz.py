from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.quize import Quiz
from models.quizsubmission import QuizSubmission
from models.student import Student


student_quiz_bp = Blueprint(
    "student_quiz_bp",
    __name__,
    url_prefix="/student/assessments/quiz"
)


@student_quiz_bp.route("/my", methods=["GET"])
@jwt_required()
def my_quizzes():
    claims = get_jwt()

    if claims.get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    current_student_id = int(get_jwt_identity())

    student = Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    quizzes = Quiz.query.filter_by(
        batch_id=student.batch_id,
        status="Active"
    ).all()

    quiz_list = []

    for quiz in quizzes:
        submission = QuizSubmission.query.filter_by(
            quiz_id=quiz.id,
            student_id=student.id
        ).first()

        quiz_list.append({
            "id": quiz.id,
            "institution_id": quiz.institution_id,
            "course_id": quiz.course_id,
            "batch_id": quiz.batch_id,
            "title": quiz.title,
            "description": quiz.description if hasattr(quiz, "description") else None,
            "topic": quiz.topic if hasattr(quiz, "topic") else None,
            "difficulty": quiz.difficulty if hasattr(quiz, "difficulty") else None,
            "total_marks": quiz.total_marks if hasattr(quiz, "total_marks") else None,
            "status": quiz.status,
            "created_at": quiz.created_at.isoformat() if quiz.created_at else None,

            "is_submitted": True if submission else False,
            "submission_id": submission.id if submission else None,
            "submission_status": submission.status if submission else None,
            "obtained_marks": submission.obtained_marks if submission else None,
            "teacher_feedback": submission.teacher_feedback if submission else None
        })   

    all_quizzes = Quiz.query.all()
    return jsonify({
        "success": True,
        "message": "Quizzes fetched successfully",
        "quizzes": quiz_list
    }), 200
    
