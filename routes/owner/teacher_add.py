from flask import Blueprint, request, jsonify,current_app
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt,create_access_token
from datetime import datetime
from dbms.db import db
from utils.validators import is_valid_email,is_valid_mobile,is_valid_password
from models.teacher import Teacher
from models.institute import Institution
from utils.security import verify_password,generate_password_hash

teacher_add_bp=Blueprint("teacher_add_bp",__name__,url_prefix="/teacher")
@teacher_add_bp.route("/add/<int:institution_id>",methods=["POST"])
@jwt_required()
def teacher_add(institution_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())
    institute=Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
     ).first()
     
    if not institute:
        return jsonify({
            "success":False,
            "message":"Institute not found"
        }),400
    
    data=request.get_json()
    if  not data:
        return jsonify({
            'success':False,
            "message":"Request body is required "
        }),400
    name=data.get("name")
    email=data.get("email")
    mobile_no=data.get("mobile_no")
    if not name or not email or not mobile_no :
        return  jsonify({
            "success":False,
            "message":"All fields are required"
        }),400
    if not is_valid_email(email) :
        return jsonify({
            "success":False,
            "message":"Invalid email format"
        }) ,400
    if not is_valid_mobile(mobile_no) :
        return jsonify({
            "success":False,
            "message":"Invalid mobile no.. format"}),400
  
    teacher=Teacher(
        name=name,
        email=email,
        mobile_no=mobile_no,
        institution_id=institution_id
    )
    try:
        db.session.add(teacher)
        db.session.commit()
        return jsonify({
            "success":True,
            "message":"Teacher added successfully"
        }),201
    except Exception as e :
        db.session.rollback()
        current_app.logger.exception(f"Failed to create teacher:{e}")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500

#teacher list get
@teacher_add_bp.route("/get/<int:institution_id>",methods=["GET"])
@jwt_required()
def get_teacher(institution_id):
    current_user_id=int(get_jwt_identity())
    institute=Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
     ).first()

    if not institute:
        return jsonify({
            "success":False,
            "message":"Institute Not found"
        }),400
    
    teachers=Teacher.query.filter_by(
        institution_id=institution_id
    ).all()
    teacher_list=[]

    for teacher in teachers:
        teacher_list.append(teacher.to_dict())
    return jsonify({
        "success":True,
        "message":"All Teachers are fetched successfully",
        "teacher_list":teacher_list
    })    ,200

#Update
@teacher_add_bp.route("/update/<int:teacher_id>",methods=["PATCH"])
@jwt_required()
def update_teacher(teacher_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner Access Only"
        }),403
    teacher=Teacher.query.filter_by(
        id=teacher_id
    ).first()
    if not teacher:
        return jsonify({
            "success":False,

            "message":"Teacher not found"
        }),400
    current_user_id=int(get_jwt_identity())
    institute=Institution.query.filter_by(
         user_id=current_user_id,
         id=teacher.institution_id
    ) .first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to update teacher field"
        }) ,400
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400  
   
    if "name" in data:
        name=data.get("name")
        if not name.strip():
          return jsonify({
            "success": False,
            "message": "Teacher name cannot be empty"
        }), 400

        teacher.name = name
        
    if "mobile_no" in data:
        new_mobile_no=data.get("mobile_no")
        if not is_valid_mobile(new_mobile_no):
            return jsonify({
                "success":False,
                "message":"Invalid Mobile no.. format"
            }),400
        existing_user=Teacher.query.filter(
             teacher.institution_id==Teacher.institution_id,
             Teacher.mobile_no==new_mobile_no,
             Teacher.id!=teacher.id           
        ).first()

        if existing_user:
              return jsonify({
                "success": False,
                "message": "Teacher  with this phone number already exists"
            }), 409
        teacher.mobile_no=new_mobile_no    
    if "email" in data:
        new_email=data.get("email")
        if  not is_valid_email(new_email):
                return jsonify({
                "success":False,
                "message":"Invalid Email.. format"
            }),400
        existing_user=Teacher.query.filter(
             teacher.institution_id==Teacher.institution_id,
             Teacher.email==new_email,
             Teacher.id!=teacher.id           
        ).first()
        
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Teacher  with this email already exists"
            }), 409
        teacher.email=new_email    
    is_active = data.get("is_active")

    if is_active is not None:
        teacher.is_active = is_active

    login_enabled = data.get("login_enabled")
    if login_enabled is not None:
        teacher.login_enabled = login_enabled  
          
    try:
        db.session.commit()

        current_app.logger.info(
        f"Teacher {teacher.id} updated successfully."
    )

        return jsonify({
        "success": True,
        "message": "Teacher updated successfully",
        
    }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e))

        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500      

#enable login and set teacher password
@teacher_add_bp.route("/enable-teacher-login/<int:teacher_id>",methods=['PATCH'])
@jwt_required()
def enable_teacher(teacher_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":'Owner access only'
        }) ,403
    current_user_id=int(get_jwt_identity())
    teacher=Teacher.query.filter_by(
        id=teacher_id
    ).first()
    if not teacher:
        return jsonify({
            "success":False,
            "message":"Teacher not found"
        }),404
    institute=Institution.query.filter_by(
        user_id=current_user_id,
        id=teacher.institution_id
    ).first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to enable login"
        }),403
    data=request.get_json()
    if data is None:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        })    ,400
    password=data.get("password")
    if not password:
        return jsonify({
            "success":False,
            "message":"Password is required for enable login"
        })  ,400
    if not is_valid_password(password):
        return jsonify({
            "success":False,
            'message':"Password must be atleast 8 character and contain atleast one special character,letter and digit"
        })  ,400
    if teacher.login_enabled:
       return jsonify({
        "success": False,
        "message": "Teacher login is already enabled"
    }), 400    
    teacher.password=generate_password_hash(password)    
    teacher.login_enabled=True
    try:
        db.session.commit(
        )
        return jsonify({
        "success": True,
        "message": "Teacher login enabled successfully",
        "teacher": teacher.to_dict()
    }), 200  
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(str(e))
        return jsonify({
        "success": False,
        "message": "Something went wrong"
    }), 500   
