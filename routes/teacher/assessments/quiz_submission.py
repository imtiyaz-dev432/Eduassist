from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.batch import Batch
from models.quize import Quiz
from models.quiz_question import QuizQuestion
from models.quiz_submission_answer import QuizSubmissionAnswer
from models.student import Student
from models.quizsubmission import QuizSubmission

teacher_quiz_view_bp=Blueprint("teacher_quiz_view_bp",__name__,url_prefix="/teacher/quiz/submission/view")  
@teacher_quiz_view_bp.route("/<int:quiz_id>",methods=["GET"])
@jwt_required()
def view_quiz(quiz_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            'message':"Owner/Teacher access only"
        }),403
    current_user_id=int(get_jwt_identity())
    quiz=Quiz.query.filter_by(
        id=quiz_id
    ).first()
    if not quiz:
        return jsonify({
            "success":False,
            "message":"Quiz not found"
        }),404
    institute=Institution.query.filter_by(
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to view this quiz submissions"
        }),400     
    quiz_questions = QuizQuestion.query.filter_by(
    quiz_id=quiz.id
).all()
    question_ids = [q.id for q in quiz_questions]
    answers = QuizSubmissionAnswer.query.filter(
    QuizSubmissionAnswer.quiz_question_id.in_(question_ids)
).all()
    submission_ids = list(set([
    ans.quiz_submission_id for ans in answers
]))
    submissions = QuizSubmission.query.filter(
    QuizSubmission.id.in_(submission_ids)
).all()
   
    result = []

    for submission in submissions:
        student = Student.query.filter_by(
            id=submission.student_id
        ).first()

        result.append({
            "submission_id": submission.id,
            "student_id": student.id,
            "student_name": student.student_name if student else None,
            "total_marks": submission.total_marks,
            "obtained_marks": submission.obtained_marks,
            "status": submission.status
        })    
    
    return jsonify({
        "success": True,
        "message": "Quiz submissions fetched successfully",
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "topic": quiz.topic
        },
        "submissions": result
    }), 200