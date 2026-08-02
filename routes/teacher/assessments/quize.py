from flask import Blueprint,request,jsonify,current_app
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.batch import Batch
from models.quize import Quiz

quiz_bp=Blueprint("quize_bp",__name__,url_prefix="/quiz")
@quiz_bp.route("/add/<int:batch_id>",methods=["POST"])
@jwt_required()
def add_quize(batch_id):
    claims=get_jwt()
    if claims.get("role") not in["owner","teacher"]:
        return jsonify({
            "success":False,
            "message":"owner/teacher access only "
        }),403

    batch=Batch.query.filter_by(
        id=batch_id
    ).first()
    if not batch:
        return jsonify({
            "success":False,
            "message":"Batch not found"
        }),404
    if claims.get("role")=="owner":     
        current_user_id=int(get_jwt_identity())    
        institute=Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()

        if not institute:
         return jsonify({
            "success":False,
            "message":"Unauthorized to add quize"
        }),403

    if claims.get("role")=="teacher":
      current_teacher_id=int(get_jwt_identity())
      if batch.teacher_id != current_teacher_id:
        return jsonify({
        "success": False,
        "message": "Unauthorized"
    }), 403
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }) ,400

    title=data.get("title")
    if not title:
       return jsonify({
        "success": False,
        "message": "Quiz title is required"
    }), 400
    topic=data.get("topic")
    difficulty=data.get("difficulty","Easy")
    allowed_difficulty = ["Easy", "Medium", "Hard", "Very Hard"]
    if difficulty not in allowed_difficulty:
       return jsonify({
        "success": False,
        "message": "Invalid difficulty"
    }), 400
    total_marks=data.get("total_marks")
    status = data.get("status", "Draft")
    allowed_status = ["Draft", "Active", "Closed"]
    if status not in allowed_status:
      return jsonify({
        "success": False,
        "message": "Invalid quiz status"
    }), 400

    new_quiz = Quiz(
        institution_id=batch.institution_id,
        course_id=batch.course_id,
        batch_id=batch.id,
        title=title,
        topic=topic,
        difficulty=difficulty,
        total_marks=total_marks,
        status=status
    )

    db.session.add(new_quiz)
    try:
      db.session.commit()
      return jsonify({
        "success": True,
        "message": "Quiz created successfully",
        "quiz": new_quiz.to_dict()
    }), 201
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add quiz ")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 
         

#get
@quiz_bp.route("/get/<int:batch_id>",methods=["GET"])
@jwt_required()
def get_quiz(batch_id):
    claims=get_jwt()
    if claims.get("role") not in["owner","teacher"]:
        return jsonify({
            "success":False,
            "message":"owner/teacher access only "
        }),403
    batch=Batch.query.filter_by(
        id=batch_id
    ).first()
    if not batch:
        return jsonify({
            "success":False,
            "message":"Batch not found"
        }),404
    if claims.get("role")=="owner":
        current_user_id=int(get_jwt_identity())    
        institute=Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()
        if not institute:
          return jsonify({
            "success":False,
            "message":"Unauthorized to get quiz"
        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())
        if(batch.teacher_id!=current_teacher_id):
            return jsonify({
        "success": False,
        "message": "Unauthorized"
    }), 403

    quizes=Quiz.query.filter_by(
        batch_id=batch_id
    ).all()
    quiz_list=[]
    for quiz in quizes:
        quiz_list.append(quiz.to_dict())

    return jsonify({
        "success":True,
        "message":"Data fetched successfully",
        "quiz list":quiz_list
    }),200

#update
@quiz_bp.route("/update/<int:quiz_id>",methods=["PATCH"])
@jwt_required()
def update(quiz_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"owner/teacher access only "
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
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()

       if not institute:
         return jsonify({
            "success":False,
            "message":"Unauthorized to update quiz"
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
        }) ,400

    title = data.get("title", quiz.title)
    topic = data.get("topic", quiz.topic)
    difficulty = data.get("difficulty", quiz.difficulty)
    total_marks = data.get("total_marks", quiz.total_marks)
    status = data.get("status", quiz.status)

    allowed_difficulty = ["Easy", "Medium", "Hard", "Very Hard"]

    if difficulty not in allowed_difficulty:
        return jsonify({
            "success": False,
            "message": "Invalid difficulty"
        }), 400

    allowed_status = ["Draft", "Active", "Closed"]

    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": "Invalid quiz status"
        }), 400

    quiz.title = title
    quiz.topic = topic
    quiz.difficulty = difficulty
    quiz.total_marks = total_marks
    quiz.status = status

    try:
      db.session.commit()
      return jsonify({
        "success": True,
        "message": "Quiz updated successfully",
        "quiz": quiz.to_dict()
    }), 200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to update quiz ")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 

    
#delete      
@quiz_bp.route("/delete/<int:quiz_id>",methods=["DELETE"])
@jwt_required()
def quiz_delete(quiz_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"owner/teacher access only "
        }),403
    quiz=Quiz.query.filter_by(
        id=quiz_id
    )   .first()

    if not quiz:
        return jsonify({
            "success":False,
            "message":"Quiz not found"
        }),404
    current_user_id=int(get_jwt_identity())
    if claims.get("role")=="owner":   

       institute=Institution.query.filter_by(
        id=quiz.institution_id,
        user_id=current_user_id
    ).first()
    
       if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to delete this quiz",

        }),403
    if claims.get("role")=="teacher":
        current_teacher_id=int(get_jwt_identity())  
        # quiz.batch.teacher_id=current_teacher_id
        if quiz.batch.teacher_id != current_teacher_id:
         return jsonify({
        "success": False,
        "message": "Unauthorized"
    }), 403

    try: 
       db.session.delete(quiz)
       db.session.commit()
       return  jsonify({
        "success":True,
        "message":"Quiz deleted successfully"
    }),200

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete quiz ")
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500 
         