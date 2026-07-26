from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.security import generate_password_hash

from dbms.db import db
from models.institute import Institution
from models.batch import Batch
from models.student import Student
from utils.rate import limiter


teacher_student_bp = Blueprint("teacher_student_bp", __name__,  url_prefix="/teacher/academics/student"
)
@teacher_student_bp.route("/add/<int:batch_id>", methods=["POST"])
@jwt_required()
def add_student(batch_id):
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
            "message": "Unauthorized to add student in this batch"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    student_name = data.get("student_name", "")
    email = data.get("email")
    phone = data.get("phone", "")
    parent_phone =data.get("parent_phone")
    address = data.get("address")
    admission_date = data.get("admission_date")
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
        email = email.lower()

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


    if admission_date == "invalid":
        return jsonify({
            "success": False,
            "message": "Invalid admission_date format. Use YYYY-MM-DD"
        }), 400

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
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Student added successfully",
        "student": new_student.to_dict()
    }), 201

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
    if new_email:
        new_email = new_email.lower()
    if "phone" in data:
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
    if "email" in data and new_email:
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
        parsed_admission_date = parse_date(data.get("admission_date"))

        if parsed_admission_date == "invalid":
            return jsonify({
                "success": False,
                "message": "Invalid admission_date format. Use YYYY-MM-DD"
            }), 400

        student.admission_date = parsed_admission_date
    student.student_name = data.get("student_name", student.student_name)
    student.email = new_email
    student.phone = new_phone
    student.parent_phone = data.get("parent_phone", student.parent_phone)
    student.address = data.get("address", student.address)
    student.status = data.get("status", student.status)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Student updated successfully",
        "student": student.to_dict()
    }), 200
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
            "success": False,
            "message": "Password is required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters"
        }), 400
    student.password_hash = generate_password_hash(password)
    student.is_login_enabled = True
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Student login enabled successfully",
        "student": student.to_dict()
    }), 200
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