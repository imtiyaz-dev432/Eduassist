from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.quize import Quiz
from models.student import Student
from models.quiz_question import QuizQuestion


student_quiz_question_bp = Blueprint(
    "student_quiz_question_bp",
    __name__,
    url_prefix="/student/quiz"
)
@student_quiz_question_bp.route("/questions/<int:quiz_id>", methods=["GET"])
@jwt_required()
def view_quiz_questions(quiz_id):
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

    quiz = Quiz.query.filter_by(
        id=quiz_id
    ).first()

    if not quiz:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if quiz.batch_id != student.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized to view this quiz"
        }), 403

    if quiz.status != "Active":
        return jsonify({
            "success": False,
            "message": "Quiz is not active"
        }), 400

    questions = QuizQuestion.query.filter_by(
        quiz_id=quiz.id
    ).all()

    question_list = []

    for question in questions:
        question_list.append({
            "id": question.id,
            "quiz_id": question.quiz_id,
            "question": question.question,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
            "marks": question.marks
        })

    return jsonify({
        "success": True,
        "message": "Quiz questions fetched successfully",
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "topic": quiz.topic if hasattr(quiz, "topic") else None,
            "difficulty": quiz.difficulty if hasattr(quiz, "difficulty") else None
        },
        "questions": question_list
    }), 200

@student_quiz_question_bp.route("/list",methods=["GET"])
@jwt_required()
def get_quiz_list():
    claims=get_jwt()
    if claims.get("role")!="student":
        return jsonify({
            "success":False,
            "message":"Student access only"
        }),404
    current_student_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=current_student_id
    )    .first()
    if not student:
        return jsonify({
            "success":False,
            "message":"Student not found"
        }),404
    
    quizzes=Quiz.query.filter_by(batch_id=student.batch_id).all()
    quiz_list=[]
    for q in quizzes:
        quiz_list.append({
            "id": q.id,
            "title": q.title,
            "topic": q.topic if hasattr(q, "topic") else "General",
            "difficulty": q.difficulty if hasattr(q, "difficulty") else "Normal",
            "total_marks": q.total_marks,
            "status": q.status
        })

    return jsonify({
         "success": True,
        "message": "Quiz list fetched successfully",
        "quizzes": quiz_list
    })
       