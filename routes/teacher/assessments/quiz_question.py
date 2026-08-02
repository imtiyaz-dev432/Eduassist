from flask import Blueprint,request,jsonify,current_app
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from datetime import datetime 
from dbms.db import db
from models.institute import Institution
from models.batch import Batch
from models.quize import Quiz
from models.quiz_question import QuizQuestion
from models.teacher import Teacher

quiz_question_bp=Blueprint("quiz_question_bp",__name__,url_prefix='/quiz_question')
@quiz_question_bp.route("/add/<int:quiz_id>",methods=["POST"])
@jwt_required()
def add_quiz_question(quiz_id):
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
    if claims.get("role")=="owner":       
       institute=Institution.query.filter_by(
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()

       if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to add quiz question"
        }),403
    if claims.get("role")=="teacher":
       current_teacher_id=int(get_jwt_identity())
       if quiz.batch.teacher_id != current_teacher_id:
           return jsonify({
        "success": False,
        "message": "Unauthorized"
                      }), 403
   
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        })    ,400

    question = data.get("question").strip()
    option_a = data.get("option_a").strip()
    option_b = data.get("option_b").strip()
    option_c = data.get("option_c").strip()
    option_d = data.get("option_d").strip()
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

    try:
        marks = int(marks)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Marks must be a valid number"
        }), 400

    if marks <= 0 or marks>100:
        return jsonify({
            "success": False,
            "message": "Marks must be greater than 0 and less than 100"
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

    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Quiz question added successfully",
        "question":new_question.to_dict()
    }),200
    except Exception :
        db.session.rollback()
        current_app.logger.exception("Failed to add quiz question")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 

#get
@quiz_question_bp.route("/get/<int:quiz_id>",methods=["GET"])
@jwt_required()
def get_all_question(quiz_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            'message':"Owner/Teacher access only"
        }),403 
    quiz=Quiz.query.filter_by(
        id=quiz_id
    ).first()

    if not quiz:
        return jsonify({
            "success":False,
            "message":"Quiz not found"
        }),404
    if claims.get("role")=="owner":
        current_user_id=int(get_jwt_identity())
        institute=Institution.query.filter_by(
        user_id=current_user_id,
        id=quiz.institution_id
    ).first()

        if  not institute:
         return jsonify({
            "success":False,
            "message":"Unauthorized to get quiz question"
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        if(quiz.batch.teacher_id!=current_teacher_id):
            return jsonify({
                "success":False,
                "message":"Teacher not found"
            }),400
        
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
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            'message':"Owner/Teacher access only"
        }),403
    
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
            "message": "Quiz  not found"
        }), 404
    if claims.get("role")=="owner":
        current_user_id=int(get_jwt_identity())           
        institute=Institution.query.filter_by(
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()

        if not institute:
          return jsonify({
            "success":False,
            "message":'Unauthorized to update quiz question'
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        if(quiz.batch.teacher_id!=current_teacher_id):
            return jsonify({
                "success":False,
                "message":"Teacher not found"
            }),400
    data=request.get_json()

    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400

    question=data.get("question",quiz_question.question).strip()
    option_a = data.get("option_a", quiz_question.option_a).strip()
    option_b = data.get("option_b", quiz_question.option_b).strip()
    option_c = data.get("option_c", quiz_question.option_c).strip()
    option_d = data.get("option_d", quiz_question.option_d).strip()
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

    if marks<=0 or marks>100:
        return jsonify({
            "success":False,
            "message":"Marks must be greater than 0 or less than 100"
        }),400
    quiz_question.question = question
    quiz_question.option_a = option_a
    quiz_question.option_b = option_b
    quiz_question.option_c = option_c
    quiz_question.option_d = option_d
    quiz_question.correct_answer = correct_answer
    quiz_question.explanation = explanation
    quiz_question.marks = marks
    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Quiz question updated successfully",
        "question":quiz_question.to_dict()
    }),200
    except Exception :
        db.session.rollback()
        current_app.logger.exception("Failed to update quiz question")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 

#delete
@quiz_question_bp.route("/delete/<int:quiz_question_id>",methods=["DELETE"])
@jwt_required()
def delete_quiz_question(quiz_question_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            'message':"Owner/Teacher access only"
        }),403
  
    
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
    if claims.get("role")=="owner":
        current_user_id=int(get_jwt_identity())

        institute=Institution.query.filter_by(
          id=quiz.institution_id,
          user_id=current_user_id
    ).first()

        if not institute:
           return jsonify({
            "success":False,
            "message":"Unauthorized to delete this quiz question"
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        if (quiz.batch.teacher_id!=current_teacher_id):
            return jsonify({
                "success":False,
                "message":"Teacher not found"
            }),400
    try:
        db.session.delete(quiz_question)
        db.session.commit()
        return jsonify({
        "success":True,
        "message":"Quiz question deleted successfully",
        "question":quiz_question.to_dict()
    }),200
    except Exception :
        db.session.rollback()
        current_app.logger.exception("Failed to delete quiz question")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 
    
