from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from dbms.db import db

from models.quize import Quiz
from models.student import Student
from models.quiz_question import QuizQuestion
from models.quizsubmission import QuizSubmission
from models.quiz_submission_answer import QuizSubmissionAnswer

student_quiz_submission_bp = Blueprint(
    "student_quiz_check_bp",
    __name__,
    url_prefix="/student/quiz"
)


@student_quiz_submission_bp.route("/my/<int:quiz_id>", methods=["POST"])
@jwt_required()
def quiz_submission(quiz_id):
    claims = get_jwt()

    if claims.get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    current_student_id = int(get_jwt_identity())

    student = Student.query.filter_by(id=current_student_id).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    quiz = Quiz.query.filter_by(id=quiz_id).first()

    if not quiz:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if quiz.batch_id != student.batch_id:
        return jsonify({
            "success": False,
            "message": "Unauthorized to submit this quiz"
        }), 403

    existing_submission = QuizSubmission.query.filter_by(
        quiz_id=quiz.id,
        student_id=student.id
    ).first()

    if existing_submission:
        return jsonify({
            "success": False,
            "message": "Quiz already submitted"
        }), 409

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    answers = data.get("answers")

    if not answers or not isinstance(answers, list):
        return jsonify({
            "success": False,
            "message": "Answers list is required"
        }), 400

    allowed_options = ["A", "B", "C", "D"]

    total_marks = 0
    obtained_marks = 0

    new_submission = QuizSubmission(
        institution_id=quiz.institution_id,
        course_id=quiz.course_id,
        batch_id=quiz.batch_id,
        quiz_id=quiz.id,
        student_id=student.id,
        total_marks=0,
        obtained_marks=0,
        status="Checked"
    )

    db.session.add(new_submission)
    db.session.flush()

    submitted_question_ids = set()

    for item in answers:

        if not isinstance(item, dict):
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Each answer must be an object"
            }), 400

        question_id = item.get("question_id")
        selected_option = item.get("student_answer")

        if not question_id or not selected_option:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "question_id and student_answer are required"
            }), 400

        if question_id in submitted_question_ids:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Duplicate question answer is not allowed"
            }), 400

        submitted_question_ids.add(question_id)

        if isinstance(selected_option, list):
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Only one option is allowed per question"
            }), 400

        selected_option = selected_option.upper()

        if selected_option not in allowed_options:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Invalid answer. Allowed options are A, B, C, D"
            }), 400

        question = QuizQuestion.query.filter_by(
            id=question_id,
            quiz_id=quiz.id
        ).first()

        if not question:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"Question not found for id {question_id}"
            }), 404

        question_marks = question.marks if question.marks else 1

        total_marks += question_marks

        correct_answer = question.correct_answer.upper()

        is_correct = selected_option == correct_answer

        if is_correct:
            obtained_marks += question_marks
        new_answer = QuizSubmissionAnswer(
    quiz_submission_id=new_submission.id,
    quiz_question_id=question.id,
    student_id=student.id,          # <-- Add this
    student_answer=selected_option,
    is_correct=is_correct,
    marks_awarded=question_marks if is_correct else 0,
    checked_at=datetime.utcnow()
)

        db.session.add(new_answer)

    new_submission.total_marks = total_marks
    new_submission.obtained_marks = obtained_marks

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Quiz submitted successfully",
        "data": {
            "submission_id": new_submission.id,
            "total_marks": total_marks,
            "obtained_marks": obtained_marks
        }
    }), 201


