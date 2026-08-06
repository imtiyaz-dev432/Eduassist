from flask import Blueprint,request,jsonify,current_app
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from dbms.db import db
from datetime import datetime
from models.batch import Batch
from models.institute import Institution
from models.course import Course
from models.teacher import Teacher
batch_bp=Blueprint("batch_bp",__name__,url_prefix="/owner/academics/batch")
@batch_bp.route("/add/<int:course_id>",methods=["POST"])
@jwt_required()
def add_batch(course_id):
    claims=get_jwt()
    if claims.get("role") not in ["owner","teacher"]:
        return jsonify({
            "success":False,
            "message":"Owner/teacher access only"
        }),403
    current_user_id=int(get_jwt_identity())
    course=Course.query.filter_by(
        id=course_id
    ).first()

    if not course:
        return jsonify({
            "success":False,
            "message":"Course not found"
        }),404
    institution=Institution.query.filter_by(
        user_id=current_user_id,
        id=course.institution_id
    ).first()

    if not institution:
        return jsonify({
            "success":False,
                    "message": "Unauthorized to add batch for this course"}),403
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400

    batch_name=data.get("batch_name")
    batch_code=data.get("batch_code")
    teacher_id=data.get("teacher_id")
    start_date=data.get("start_date")
    end_date=data.get("end_date")
    days=data.get("days")
    start_time=data.get("start_time")
    end_time=data.get('end_time')    
    mode = data.get("mode", "Offline")
    classroom = data.get("classroom")
    total_seats = data.get("total_seats")
    fee_amount = data.get("fee_amount")
    monthly_fee = data.get("monthly_fee")
    status = data.get("status", "Active")
    if not batch_name :
        return jsonify({
            "message":"Batch name is required"
        }),400
    if not teacher_id:
        return jsonify({
            "success":False,
            "message":'Teacher id is required for creating a batch'
        })    ,403
    teacher=Teacher.query.filter_by(
        id=teacher_id,
        institution_id=course.institution_id
    ).first()

    if not teacher:
        return jsonify({
            "success": False,
            "message": "Invalid teacher or teacher does not belong to your institute"
        }), 400
    new_batch=Batch(
        institution_id=course.institution_id,
        course_id=course_id,
        batch_name=batch_name,
        batch_code=batch_code,
        teacher_id=teacher.id,
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
        end_date=datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
        days=days,
        start_time=start_time,
        end_time=end_time,
        mode=mode,
        classroom=classroom,
        total_seats=total_seats,
        filled_seats=0,
        fee_amount=fee_amount,
        monthly_fee=monthly_fee,
        status=status
    )    
    db.session.add(new_batch)
    try:
        db.session.commit()
        return jsonify({
        "success":True,
        "message": "Batch created successfully"
    }), 201
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to create a batch")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500


#get 
@batch_bp.route("/get/<int:course_id>",methods=["GET"])
@jwt_required()
def get_course_batch(course_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())
    course=Course.query.filter_by(
        
        id=course_id
    ).first()

    if not course:
      return jsonify({
        "message":"Course not found"
      }),404

    institution=Institution.query.filter_by(
        id=course.institution_id,
        user_id=current_user_id
    ).first()
    if not institution:
        return jsonify({
            "message":"institute not found"
        }),404

    batches = Batch.query.filter_by(course_id=course_id).all()

    batch_list = []

    for batch in batches:
        batch_list.append({
    "id": batch.id,
    "institution_id": batch.institution_id,
    "course_id": batch.course_id,
    "batch_name": batch.batch_name,
    "batch_code": batch.batch_code,
    "start_date": batch.start_date.isoformat() if batch.start_date else None,
    "end_date": batch.end_date.isoformat() if batch.end_date else None,
    "days": batch.days,
    "start_time": batch.start_time,
    "end_time": batch.end_time,
    "mode": batch.mode,
    "classroom": batch.classroom,
    "total_seats": batch.total_seats,
    "filled_seats": batch.filled_seats,
    "fee_amount": batch.fee_amount,
    "monthly_fee": batch.monthly_fee,
    "status": batch.status,
    "created_at": batch.created_at.isoformat() if batch.created_at else None,
    "updated_at": batch.updated_at.isoformat() if batch.updated_at else None
})
    return jsonify({
    "success": True,
    "message": "Batches fetched successfully",
        "batches": batch_list
    }), 200    

#Update
@batch_bp.route("/update/<int:batch_id>",methods=["PATCH"])
@jwt_required()
def update_batches(batch_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())
    batch=Batch.query.filter_by(
        id=batch_id
    )    .first()

    if not batch:
        return jsonify({
            "success":False,
            "message":"Batch not found"
        }),404

    institution=Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success":False,
            "message":"Unauthorized to update this batch"
        }),403

    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    batch.batch_name = data.get("batch_name", batch.batch_name).strip()
   
    batch.batch_code = data.get("batch_code", batch.batch_code)
    batch.days = data.get("days", batch.days)
    batch.start_time = data.get("start_time", batch.start_time)
    batch.end_time = data.get("end_time", batch.end_time)
    batch.mode = data.get("mode", batch.mode).strip()
    batch.classroom = data.get("classroom", batch.classroom)
    batch.total_seats = data.get("total_seats", batch.total_seats)
    batch.fee_amount = data.get("fee_amount", batch.fee_amount)
    batch.monthly_fee = data.get("monthly_fee", batch.monthly_fee)
    batch.status = data.get("status", batch.status).strip()    
    if "teacher_id" in data:
        teacher_id=data.get("teacher_id")
        teacher=Teacher.query.filter_by(
            id=teacher_id,
            institution_id=batch.institution_id
        ).first()
        if not teacher:
            return jsonify({
                "success":False,
                "message":"Invalid Teacher Id or Teacher does not exist"
            }),404
        batch.teacher_id=teacher_id    
    if data.get("start_date"):
        batch.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()

    if data.get("end_date"):
        batch.end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()
    try:
        db.session.commit()
        return jsonify({
        "message": "Batch updated successfully"
    }), 200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to update a batch")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500        

#delete 
@batch_bp.route("/delete/<int:batch_id>",methods=["DELETE"])
@jwt_required()
def delete_batch(batch_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())
    batch=Batch.query.filter_by(id=batch_id).first()
    if not batch:
        return jsonify({
            "success": False,
            "message": "Batch not found"
        }), 404
    institution=Institution.query.filter_by(
        user_id=current_user_id,
        id=batch.institution_id
    ).first()
    if not institution:
        return jsonify({
            "success":False,
            "message":"Unauthorized to delete this batch"
        }),403
    try:
       db.session.delete(batch)
       db.session.commit()
       return jsonify({
        "success":True,
        "message": "Batch deleted successfully"
    }), 200    
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete a batch")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500        

