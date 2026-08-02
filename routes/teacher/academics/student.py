from flask import Blueprint, request, jsonify,current_app
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from datetime import datetime
from werkzeug.security import generate_password_hash

from dbms.db import db
from models.institute import Institution
from models.batch import Batch
from models.student import Student
from utils.rate import limiter
from utils.validators import is_valid_email,is_valid_mobile,is_valid_password

teacher_student_bp = Blueprint("teacher_student_bp", __name__,  url_prefix="/teacher/academics/student"
)
@teacher_student_bp.route("/add/<int:batch_id>", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def add_student(batch_id):
    claims=get_jwt()
    if claims.get("role") not in ["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"Owner/Teacher access only"
        }),403 
    current_user_id = int(get_jwt_identity())
    batch = Batch.query.filter_by(id=batch_id).first()

    if not batch:
        return jsonify({
            "success": False,
            "message": "Batch not found"
        }), 404

    institution = Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success": False,
            "message": "Unauthorized to add student in this batch"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    student_name = data.get("student_name")
    email = data.get("email")
    phone = data.get("phone", "")
    parent_phone =data.get("parent_phone")
    address = data.get("address")
    admission_date = data.get("admission_date")
    admission_date_obj = None

    if admission_date:
     try:
        admission_date_obj = datetime.strptime(admission_date, "%Y-%m-%d").date()
     except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid admission_date format. Use YYYY-MM-DD"
        }), 400
    status = data.get("status", "Active")

    if email:
        if not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Invalid Email ,Enter in the correct format"
            }),400
        email = email.lower()

    if parent_phone:
        if not is_valid_mobile(parent_phone):
            return jsonify({
                "success":False,
                "message":"Invalid Format of mobile no.."
            }) ,400

    if not student_name or not phone:
        return jsonify({
            "success": False,
            "message": "Student name and phone are required"
        }), 400

    allowed_status = ["Active", "Inactive", "Completed", "Dropped"]

    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Allowed values are: {', '.join(allowed_status)}"
        }), 400

    if not is_valid_mobile(phone):
            return jsonify({
                "success":False,
                "message":"Invalid Mobile no  ,Enter in the correct format"
            }),400
    existing_phone = Student.query.filter_by(
        institution_id=batch.institution_id,
        phone=phone
    ).first()

    if existing_phone:
        return jsonify({
            "success": False,
            "message": "Student with this phone number already exists"
        }), 409

    if email:
        
        existing_email = Student.query.filter_by(
            institution_id=batch.institution_id,
            email=email
        ).first()

        if existing_email:
            return jsonify({
                "success": False,
                "message": "Student with this email already exists"
            }), 409

    new_student = Student(
        institution_id=batch.institution_id,
        course_id=batch.course_id,
        batch_id=batch.id,
        student_name=student_name,
        email=email,
        phone=phone,
        parent_phone=parent_phone,
        address=address,
        admission_date=admission_date_obj,
        status=status
    )

    db.session.add(new_student)
    try:
      db.session.commit()
      return  jsonify({
        "success":True,
        "message":"Student added successfully"
      }),201
    except Exception:
        db.session.rollback()
        return jsonify({
        "success": False,
        "message": "Something went wrong."
    }), 500


#get
@teacher_student_bp.route("/get/<int:batch_id>", methods=["GET"])
@jwt_required()
def get_student(batch_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    batch = Batch.query.filter_by(id=batch_id).first()

    if not batch:
        return jsonify({
            "success": False,
            "message": "Batch not found"
        }), 404

    institution = Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success": False,
            "message": "Unauthorized to view students in this batch"
        }), 403

    students = Student.query.filter_by(
        batch_id=batch_id
    ).all()

    student_list = []

    for student in students:
        student_list.append(student.to_dict())

    return jsonify({
        "success": True,
        "message": "Students fetched successfully",
        "students": student_list
    }), 200

#for teacher
@teacher_student_bp.route("/update/<int:student_id>", methods=["PATCH"])
@limiter.limit("20 per minute")
@jwt_required()
def update_student(student_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404
    institution = Institution.query.filter_by(
        id=student.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success": False,
            "message": "Unauthorized to update this student"
        }), 403
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400
    allowed_status = ["Active", "Inactive", "Completed", "Dropped"]
    if "status" in data and data.get("status") not in allowed_status:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Allowed values are: {', '.join(allowed_status)}"
        }), 400
    new_phone = data.get("phone", student.phone)
    new_email = data.get("email", student.email)   
    if "phone" in data:
        if not is_valid_mobile(new_phone):
            return jsonify({
                "success":False,
                "message":"Ivalid mobile format"
            }),400

        existing_phone = Student.query.filter(
            Student.institution_id == student.institution_id,
            Student.phone == new_phone,
            Student.id != student.id
        ).first()

        if existing_phone:
            return jsonify({
                "success": False,
                "message": "Student with this phone number already exists"
            }), 409
    if "email" in data:
        if not is_valid_email(new_email):
            return jsonify({
                "success":False,
                "message":"Invalid Email format"
            }),400
      
        new_email = new_email.lower()
        existing_email = Student.query.filter(
            Student.institution_id == student.institution_id,
            Student.email == new_email,
            Student.id != student.id
        ).first()

        if existing_email:
            return jsonify({
                "success": False,
                "message": "Student with this email already exists"
            }), 409
    
    if "admission_date" in data:
        raw_data = data.get("admission_date")
        try:
           student.admission_date = datetime.strptime(raw_data, "%Y-%m-%d").date()
        except ValueError:
           return jsonify({
            "success": False,
            "message": "Invalid admission_date format. Use YYYY-MM-DD"
        }), 400    

   
    student.student_name = data.get("student_name", student.student_name)
    student.email = new_email
    student.phone = new_phone
    student.address = data.get("address", student.address)
    student.status = data.get("status", student.status)
    if "parent_phone" in data:
        parent_phone=data.get("parent_phone")
        if parent_phone!="" and not is_valid_mobile(parent_phone):
            return jsonify({
                "success":False,
                "message":"Ivalid mobile format"
            }),400
        else:
            student.parent_phone = data.get("parent_phone", student.parent_phone)    

    try:

      db.session.commit()
      return jsonify({
        "success": True,
        "message": "Student updated successfully",
        "student": student.to_dict()
    }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "success":False,
            "message": "Something went wrong."
    }), 500

#for student
@teacher_student_bp.route("/enable-login/<int:student_id>", methods=["PATCH"])
@limiter.limit("3 per minute")
@jwt_required()
def enable_student_login(student_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    student = Student.query.filter_by(
        id=student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    institution = Institution.query.filter_by(
        id=student.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success": False,
            "message": "Unauthorized to enable login for this student"
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    password = data.get("password")
    if not password:
        return jsonify({
            "success":False,
            "message":"Password is required to enable login"
        }),400
    if not is_valid_password(password):
        return jsonify({
            "success":False,
            "message":"Password must be of atleast 8 character and "
            "cotain atleast one special character "
        })    
    student.password_hash = generate_password_hash(password)
    student.is_login_enabled = True
    try:
       db.session.commit()
       return jsonify({
        "success": True,
        "message": "Student login enabled successfully",
        "student": student.to_dict()
    }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(
            f"DB Error: Failed to update student ID {student_id} by User ID {current_user_id}. Error: {str(e)}"
        )
        return jsonify({
            "success": False,
            "message": "An internal error occurred while saving. Please try again."
        }),500
#delete
@teacher_student_bp.route("/delete/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404
    institution = Institution.query.filter_by(
        id=student.institution_id,
        user_id=current_user_id
    ).first()
    if not institution:
        return jsonify({
            "success": False,
            "message": "Unauthorized to delete this student"
        }), 403
    db.session.delete(student)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Student record deleted successfully"
    }), 200