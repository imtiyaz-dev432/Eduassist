from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.student import Student
from models.attendance import Attendance
from models.batch import Batch
attendance_bp=Blueprint("attendance_bp",__name__,url_prefix="/teacher/operation/attendance")
@attendance_bp.route("/mark/<int:student_id>",methods=["POST"])
@jwt_required()
def mark_attendence(student_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"Owner or teacher access only"
        }),403
    current_user_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=student_id
    ).first()
    if not student:
        return jsonify ({
            "success":False,
            "message":"Student not found"
        }),404

    if claims.get("role") == "teacher":
        batch = Batch.query.filter_by(id=student.batch_id, teacher_id=current_user_id).first()
        if not batch:
            return jsonify({"success": False, "message": "Teacher not authorized for this student"}), 403
    else:
        institute = Institution.query.filter_by(id=student.institution_id, user_id=current_user_id).first()
        if not institute:
            return jsonify({"success": False, "message": "Institute not found"}), 403

    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400

    attendance_date=data.get("attendance_date") 
    status=data.get("status")
    remarks=data.get("remarks")
    if not attendance_date or not status:
        return jsonify({
            "message": "Attendance date and status are required"
        }), 400

    allowed_status = ["Present", "Absent", "Late", "Leave"]

    if status not in allowed_status:
        return jsonify({
            "message": "Invalid attendance status"
        }), 400

    attendance_date_obj = datetime.strptime(
        attendance_date,
        "%Y-%m-%d"
    ).date()

    existing_attendance = Attendance.query.filter_by(
        student_id=student.id,
        attendance_date=attendance_date_obj
    ).first()

    if existing_attendance:
        return jsonify({
            "message": "Attendance already marked for this student on this date"
        }), 409

    new_attendance = Attendance(
        institution_id=student.institution_id,
        course_id=student.course_id,
        batch_id=student.batch_id,
        student_id=student.id,
        attendance_date=attendance_date_obj,
        status=status,
        remarks=remarks
    )

    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({
        "message": "Attendance marked successfully",
        "attendance": new_attendance.to_dict()
    }), 201       

#get attendance
@attendance_bp.route("/get/<int:student_id>",methods=["GET"])
@jwt_required()
def get_attendance(student_id):
    claims=get_jwt()
    if claims.get("role") not in["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"Owner/Teacher access only"
        }),403
    current_user_id=int(get_jwt_identity())
    student=Student.query.filter_by(
        id=student_id
    )    .first()

    if not student:
        return jsonify({
            "success":False,
            "message":"Student not found"
        }),404

    if claims.get("role") == "teacher":
        batch = Batch.query.filter_by(id=student.batch_id, teacher_id=current_user_id).first()
        if not batch:
            return jsonify({"success": False, "message": "Teacher not authorized"}), 403
    else:
        institute = Institution.query.filter_by(id=student.institution_id, user_id=current_user_id).first()
        if not institute:
            return jsonify({"success": False, "message": "Institute not found"}), 403
    attendance_records=Attendance.query.filter_by(
        student_id=student_id
    ).all()
    attendance_list=[]
    for attendance in attendance_records:
        attendance_list.append(
            attendance.to_dict()
        )

    return jsonify({
        "message": "Attendance fetched successfully",
        "records":attendance_list}),200

#update route
@attendance_bp.route("/update/<int:attendance_id>",methods=["PATCH"])
@jwt_required()
def update_attendance(attendance_id):
    claims=get_jwt()
    current_user_id=int(get_jwt_identity())
    attendance=Attendance.query.filter_by(
        id=attendance_id
    ).first()
    if not attendance:
        return jsonify({
            "success":False,
            "message":"Attendance not found"
        }),400

    if claims.get("role") == "teacher":
        batch = Batch.query.filter_by(id=attendance.batch_id, teacher_id=current_user_id).first()
        if not batch:
            return jsonify({"success": False, "message": "Teacher not authorized"}), 403
    else:
        institute = Institution.query.filter_by(id=attendance.institution_id, user_id=current_user_id).first()
        if not institute:
            return jsonify({"success": False, "message": "Institute not found"}), 403

    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    
    status = data.get("status", attendance.status)
    remarks = data.get("remarks", attendance.remarks)
    attendance_date = data.get("attendance_date")

    allowed_status = ["Present", "Absent", "Late", "Leave"]

    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": "Invalid attendance status"
        }), 400
    default_remarks = {
    "Present": "On time",
    "Absent": "Student was absent",
    "Late": "Came late",
    "Leave": "On leave"
}
    if "status" in data and "remarks" not in data:
       remarks = default_remarks.get(status)   

    attendance.status = status
    attendance.remarks = remarks

    if attendance_date:
        attendance_date_obj = datetime.strptime(
            attendance_date,
            "%Y-%m-%d"
        ).date()

        existing_attendance = Attendance.query.filter_by(
            student_id=attendance.student_id,
            attendance_date=attendance_date_obj
        ).first()

        if existing_attendance and existing_attendance.id != attendance.id:
            return jsonify({
                "success": False,
                "message": "Attendance already marked for this student on this date"
            }), 409

        attendance.attendance_date = attendance_date_obj

    db.session.commit()  
    return jsonify({
        "success": True,
        "message": "Attendance updated successfully",
        "attendance": attendance.to_dict()
    }), 200  
       
#delete
@attendance_bp.route("/delete/<int:attendance_id>",methods=["DELETE"])
@jwt_required()
def delete_attendance(attendance_id):
    current_user_id=int(get_jwt_identity())
    attendance=Attendance.query.filter_by(
        id=attendance_id
    ).first()

    if not attendance:
        return jsonify({
            "message":"Attendance not found"
        }),400

    claims = get_jwt()
    
    print("🔥 TOKEN CLAIMS:", claims)
    print("🔥 LOGGED IN USER ID:", get_jwt_identity())
    if claims.get("role") == "teacher":
        batch = Batch.query.filter_by(id=attendance.batch_id, teacher_id=current_user_id).first()
        if not batch:
            return jsonify({"success": False, "message": "Teacher not authorized"}), 403
    else:
        institute = Institution.query.filter_by(id=attendance.institution_id, user_id=current_user_id).first()
        if not institute:
            return jsonify({"success": False, "message": "Institute not found"}), 403

    db.session.delete(attendance)   
    db.session.commit()
    return jsonify({
        "success":True,
        "message":"Attendance deleted successfully"
    }),200