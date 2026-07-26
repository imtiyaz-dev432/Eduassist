from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime 
from dbms.db import db
from models.institute import Institution
from models.batch import Batch
from models.quize import Quiz
from models.quiz_question import QuizQuestion

quiz_question_bp=Blueprint("quiz_question_bp",__name__,url_prefix='/quiz_question')
@quiz_question_bp.route("/add/<int:quiz_id>",methods=["POST"])
@jwt_required()
def add_quiz_question(quiz_id):
    claims=get_jwt()
    if claims.get("role") !="owner":
        return jsonify({
            "success":False,
            "message":"owner access only "
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
            "message":"Unauthorized to add quiz question"
        }),403

    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request bod is required"
        })    ,400

    question = data.get("question")
    option_a = data.get("option_a")
    option_b = data.get("option_b")
    option_c = data.get("option_c")
    option_d = data.get("option_d")
    correct_answer = data.get("correct_answer")
    explanation = data.get("explanation")
    marks = data.get("marks", 1)

    if not question:
        return jsonify({
            "success": False,
            "message": "Question is required"
        }), 400    
    if not option_a  or not option_b or not option_c or not option_d:
        return jsonify({
            "success":False,
            "message":"All option are required"
        }),400
    if not correct_answer:
        return jsonify({
            "success": False,
            "message": "Correct answer is required"
        }), 400

    allowed_answers = ["A", "B", "C", "D"]
    correct_answer = correct_answer.upper()
    if correct_answer not in allowed_answers:
        return jsonify({
            "success": False,
            "message": "Correct answer must be A, B, C, or D"
        }), 400    

    if correct_answer not in allowed_answers:
        return jsonify({
            "success": False,
            "message": "Correct answer must be A, B, C, or D"
        }), 400

    try:
        marks = int(marks)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Marks must be a valid number"
        }), 400

    if marks <= 0:
        return jsonify({
            "success": False,
            "message": "Marks must be greater than 0"
        }), 400

    new_question = QuizQuestion(
        quiz_id=quiz.id,
        question=question,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=correct_answer,
        explanation=explanation,
        marks=marks
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({
        "success":True,
        "message":"Quiz quetion added successfully ",
         "question": new_question.to_dict()
    }),201

#get
@quiz_question_bp.route("/get/<int:quiz_id>",methods=["GET"])
@jwt_required()
def get_all_question(quiz_id):
    claims=get_jwt()
    if claims.get("role") !="owner":
        return jsonify({
            "success":False,
            "message":"owner access only "
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
        user_id=current_user_id,
        id=quiz.institution_id
    ).first()

    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to get quiz question"
        }),403

    quiz_questions=QuizQuestion.query.filter_by(
        quiz_id=quiz_id
    ) .all()

    quiz_question_list=[]

    for question in quiz_questions:
        quiz_question_list.append(question.to_dict())

    return jsonify({
        "success":True,
        "message":"Data fetched successfully",
        "question_list":quiz_question_list
    }) ,200

#update
@quiz_question_bp.route("/update/<int:quiz_question_id>",methods=["PATCH"])
@jwt_required()
def update_question(quiz_question_id):
    claims=get_jwt()
    if claims.get("role") !="owner":
        return jsonify({
            "success":False,
            "message":"owner access only "
        }),403
    current_user_id=int(get_jwt_identity())
    quiz_question=QuizQuestion.query.filter_by(
        id=quiz_question_id
    ).first()

    if not quiz_question:
        return jsonify({
            "success":False,
            "message":"Quiz not found"
        }),404
    quiz = Quiz.query.filter_by(
        id=quiz_question.quiz_id
    ).first()

    if not quiz:
        return jsonify({
            "success": False,
            "message": "Quiz question not found"
        }), 404

    institute=Institution.query.filter_by(
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()

    if not institute:
        return jsonify({
            "success":False,
            "message":'Unauthorized to update quiz question'
        }),403

    data=request.get_json()

    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400

    question=data.get("question",quiz_question.question)
    option_a = data.get("option_a", quiz_question.option_a)
    option_b = data.get("option_b", quiz_question.option_b)
    option_c = data.get("option_c", quiz_question.option_c)
    option_d = data.get("option_d", quiz_question.option_d)
    correct_answer = data.get("correct_answer", quiz_question.correct_answer)
    explanation = data.get("explanation", quiz_question.explanation)
    marks = data.get("marks", quiz_question.marks)
    if not question:
        return jsonify({
            "success":False,
            "message":"Question is required"
        })   ,400

    if not option_a or not option_b or not option_c or not option_d:
        return jsonify({
            "success":False,

            "message":"All options are required"
        }),400

    if not  correct_answer:
        return jsonify({
            "success":False,
            "message":"Correct Answer is required"
        }),400

    correct_answer=correct_answer.upper()
    allowed_answer=["A","B","C","D"]
    if correct_answer not in allowed_answer:
        return jsonify({
            "success": False,
            "message": "Correct answer must be A, B, C, or D"
        }), 400

    try:
        marks=int(marks)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Marks must be a valid number"
        }), 400

    if marks<=0:
        return jsonify({
            "success":False,
            "message":"Marks must be greater than 0"
        }),400
    quiz_question.question = question
    quiz_question.option_a = option_a
    quiz_question.option_b = option_b
    quiz_question.option_c = option_c
    quiz_question.option_d = option_d
    quiz_question.correct_answer = correct_answer
    quiz_question.explanation = explanation
    quiz_question.marks = marks
    db.session.commit()
    return jsonify({
        "success":True,
        "message":"Quiz question updated successfully",
        "question":quiz_question.to_dict()
    }),200

#delete
@quiz_question_bp.route("/delete/<int:quiz_question_id>",methods=["DELETE"])
@jwt_required()
def delete_quiz_question(quiz_question_id):
    claims=get_jwt()
    if claims.get("role") !="owner":
        return jsonify({
            "success":False,
            "message":"owner access only "
        }),403
    current_user_id=int(get_jwt_identity())
    quiz_question=QuizQuestion.query.filter_by(
        id=quiz_question_id
    ).first()
    if not quiz_question:
        return jsonify({
            "success":False,
            "message":"Quiz question not found"
        }),404
    quiz=Quiz.query.filter_by(
        id=quiz_question.quiz_id
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
            "message":"Unauthorized to delete this quiz question"
        }),403

    db.session.delete(quiz_question)
    db.session.commit()
    return jsonify({
        "success":True,
        "message": "Quiz question deleted successfully"
    }) ,200   
