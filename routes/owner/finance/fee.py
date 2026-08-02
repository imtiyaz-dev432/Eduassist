from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.student import Student
from models.fee import Fee
from utils.rate import limiter
#add fee 
fee_bp=Blueprint("fee_bp",__name__,url_prefix="/teacher/fees")
@fee_bp.route("/create/<int:student_id>",methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def add_fees(student_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403 
    current_user_id=int(get_jwt_identity())
    student=Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify ({
            "success":False,
            "message":"Student not found"
        }),404

    institution=Institution.query.filter_by(
        id=student.institution_id,
        user_id=current_user_id
    ).first()
    if not institution:
        return jsonify({
            "success":False,
            "message":"Unauthorized to add fee"
        }),403

    data=request.get_json()
    if not data:
        return jsonify ({
            "success":False,
            "message":"Request body is required"
        }),400

    total_fee=data.get("total_fee")
    paid_amount=data.get("paid_amount",0)
    due_date=data.get("due_date")  

    if total_fee is None:
        return jsonify({
            "success":False,
            "message":"Total fee is required"
        }),400    
    try:
      total_fee = float(total_fee)
      paid_amount = float(paid_amount)
    except ValueError:
       return jsonify({
        "success": False,
        "message": "Total fee and paid amount must be valid numbers"
    }), 400
    
    if total_fee <= 0:
        return jsonify({
        "success": False,
        "message": "Total fee must be greater than 0"
    }), 400  

    if paid_amount < 0:
        return jsonify({
            "success":False,
            "message": "Paid amount cannot be negative"
        }), 400

    if paid_amount > total_fee:
        return jsonify({
            "success":False,
            "message": "Paid amount cannot be greater than total fee"
        }), 400
    
    due_date_obj = None

    if due_date:
     try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
     except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid due_date format. Use YYYY-MM-DD"
        }), 400
    due_amount = total_fee - paid_amount

    if due_amount == 0:
        status = "Paid"
    elif paid_amount > 0:
        status = "Partially Paid"
    else:
        status = "Pending"
    new_fee = Fee(
        institution_id=student.institution_id,
        course_id=student.course_id,
        batch_id=student.batch_id,
        student_id=student.id,
        total_fee=total_fee,
        paid_amount=paid_amount,
        due_amount=due_amount,
        due_date=due_date_obj,
        status=status
    )

    db.session.add(new_fee)
    db.session.commit()

    return jsonify({
        "success":True,
        "message": "Fee record created successfully",
        "fee": new_fee.to_dict()
    }), 201

#get fees
@fee_bp.route("/find/<int:student_id>",methods=['GET'])
@jwt_required()
def get_student(student_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403 
    current_user_id=int(get_jwt_identity())
    student=Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            "success":False,
            "message":"Student not found"
        }),404

    institute=Institution.query.filter_by(
        id=student.institution_id,
        user_id=current_user_id
    ).first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to view fees for this student"
        }),403

    fees = Fee.query.filter_by(
        student_id=student_id
    ).all()
    fee_list=[]
    for fee in fees:
        fee_list.append(
                 fee.to_dict()
        )
    
    return jsonify({
        "success":True,
        "message": "Fees fetched successfully",
        "fees": fee_list
    }), 200

#update
@fee_bp.route("/update/<fee_id>",methods=["PATCH"])
@jwt_required()
def update_fee(fee_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403 
    current_user_id=int(get_jwt_identity())
    fee=Fee.query.filter_by(
        id=fee_id
    ).first()
    if not fee:
        return jsonify({
            "success":False,
            "message":"Fee record Not Found"
        }),404

    institution=Institution.query.filter_by(
        id=fee.institution_id,
        user_id=current_user_id
    ).first()
    if not institution:
        return jsonify({
            "message":"Unauthorized to update this fee record"
        }),404
    data=request.get_json()
    if not data:
        return jsonify({
            "message":"Request body is required"
        }),400
    total_fee = data.get("total_fee", fee.total_fee)
    paid_amount = data.get("paid_amount", fee.paid_amount)
    due_date = data.get("due_date")

    total_fee = float(total_fee)
    paid_amount = float(paid_amount)

    if total_fee <= 0:
        return jsonify({
            "success":False,
            "message": "Total fee must be greater than 0"
        }), 400

    if paid_amount < 0:
        return jsonify({
            "success":False,
            "message": "Paid amount cannot be negative"
        }), 400

    if paid_amount > total_fee:
        return jsonify({
            "success":False,
            "message": "Paid amount cannot be greater than total fee"
        }), 400

    due_amount = total_fee - paid_amount

    if due_amount == 0:
        status = "Paid"
    elif paid_amount > 0:
        status = "Partially Paid"
    else:
        status = "Pending"

    fee.total_fee = total_fee
    fee.paid_amount = paid_amount
    fee.due_amount = due_amount
    fee.status = status
    if due_date:
        fee.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

    db.session.commit()

    return jsonify({
        "success":True,
        "message": "Fee record updated successfully",
        "fee": fee.to_dict()
    }), 200
    
#delete
@fee_bp.route("/delete/<int:fee_id>",methods=["DELETE"])
@jwt_required()
def delete_fee(fee_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403 
    current_user_id=int(get_jwt_identity())
    fee=Fee.query.filter_by(
        id=fee_id
    ).first()
    if not fee:
        return jsonify({
            "message":"Fee not found"
        }),404

    institute=Institution.query.filter_by(
        id=fee.institution_id,
        user_id=current_user_id
    ).first()
    if not institute:
        return jsonify({
            "message":"Institute not found"
        }),403

    db.session.delete(fee)
    db.session.commit()
    return jsonify({
        "message":"Fee record deleted successfully"
    }),200