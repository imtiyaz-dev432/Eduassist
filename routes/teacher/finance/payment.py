from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime ,timedelta
from dbms.db import db

from models.institute import Institution
from models.payment import Payment
from models.student import Student
from models.fee import Fee

payment_bp=Blueprint("payment_bp",__name__,url_prefix="/teacher/payment")
@payment_bp.route("/create/<int:fee_id>",methods=["POST"])
@jwt_required()
def add_payment(fee_id):
    current_user_id=int(get_jwt_identity())
    fee=Fee.query.filter_by(id=fee_id).first()
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
        }),404

         
    data=request.get_json()
    if not data:
        return  jsonify({
            "message":"Request body is required"
        }),400
    amount = data.get("amount")
    payment_method = data.get("payment_method")
    transaction_id = data.get("transaction_id")

    if amount is None or not payment_method:
        return jsonify({
            "message": "Amount and payment method are required"
        }), 400

    allowed_payment_methods = [
        "Cash",
        "UPI",
        "Bank Transfer",
        "Card",
        "Cheque",
        "DD",
        "Other"
    ]
    if payment_method not in allowed_payment_methods:
        return jsonify({
            "message": "Invalid payment method"
        }), 400

    amount = float(amount)

    if amount <= 0:
        return jsonify({
            "message": "Amount must be greater than 0"
        }), 400

    if amount > fee.due_amount:
        return jsonify({
            "message": "Payment amount cannot be greater than due amount"
        }), 400
    receipt_no = f"RCPT-{fee.id}-{int(datetime.utcnow().timestamp())}"

    new_payment = Payment(
        institution_id=fee.institution_id,
        student_id=fee.student_id,
        fee_id=fee.id,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_status="Success",
        receipt_no=receipt_no
    )

    fee.paid_amount = fee.paid_amount + amount
    fee.due_amount = fee.total_fee - fee.paid_amount

    if fee.due_amount == 0:
        fee.status = "Paid"
    elif fee.paid_amount > 0:
        fee.status = "Partially Paid"
    else:
        fee.status = "Pending"

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({
        "message": "Payment added successfully",
        "payment": new_payment.to_dict(),
        "updated_fee": fee.to_dict()
    }), 201
        
#get 
@payment_bp.route("/get/<int:fee_id>",methods=["GET"])
@jwt_required()
def get_payment(fee_id):
    current_user_id=int(get_jwt_identity())
    fee=Fee.query.filter_by(id=fee_id).first()
    if not fee:
        return jsonify({
            "message":"Fee not found"
        }),404
    institute=Institution.query.filter_by(
        id=fee.institution_id,
        user_id=current_user_id
    ).first()
    if  not institute:
        return jsonify({
            "message":"Institue not found"
        }),404
    payments=Payment.query.filter_by(
        fee_id=fee_id
    ).all()
    payment_list=[]
    for payment in payments:
        payment_list.append(
            payment.to_dict()
        )  
    
    return jsonify({
        "message":"Payment fetched successfully",
        "payments": payment_list
    }), 200

#update
@payment_bp.route("/update/<int:payment_id>",methods=["PATCH"])
@jwt_required()
def update_payment(payment_id):
    current_user_id=int(get_jwt_identity())
    payment=Payment.query.filter_by(
        id=payment_id
    ).first()
    if not payment:
        return jsonify({
            "message":"Payment not found"
        }),404
    institute=Institution.query.filter_by(
        id=payment.institution_id,
        user_id=current_user_id
    ) .first()
    if not institute:
        return jsonify({
            "message":"Institute not found"
        })   ,404

    fee=Fee.query.filter_by(
        id=payment.fee_id
    ).first()
    if not fee:
        return jsonify({
            "message":"Fee not found"
        }),404

    data=request.get_json()
    if not data:
        return jsonify({
            "message":"Request body is required"
        }),400
    
    new_amount = data.get("amount", payment.amount)
    payment_method = data.get("payment_method", payment.payment_method)
    transaction_id = data.get("transaction_id", payment.transaction_id)
    payment_status = data.get("payment_status", payment.payment_status)

    allowed_payment_methods = [
        "Cash",
        "UPI",
        "Bank Transfer",
        "Card",
        "Cheque",
        "DD",
        "Other"
    ]

    if payment_method not in allowed_payment_methods:
        return jsonify({
            "message": "Invalid payment method"
        }), 400

    allowed_status = ["Success", "Pending", "Failed"]

    if payment_status not in allowed_status:
        return jsonify({
            "message": "Invalid payment status"
        }), 400

    new_amount = float(new_amount)

    if new_amount <= 0:
        return jsonify({
            "message": "Amount must be greater than 0"
        }), 400
    old_amount = payment.amount

    new_paid_amount = fee.paid_amount - old_amount + new_amount

    if new_paid_amount < 0:
        return jsonify({
            "message": "Invalid payment update"
        }), 400

    if new_paid_amount > fee.total_fee:
        return jsonify({
            "message": "Updated paid amount cannot be greater than total fee"
        }), 400

    payment.amount = new_amount
    payment.payment_method = payment_method
    payment.transaction_id = transaction_id
    payment.payment_status = payment_status

    fee.paid_amount = new_paid_amount
    fee.due_amount = fee.total_fee - fee.paid_amount

    if fee.due_amount == 0:
        fee.status = "Paid"
    elif fee.paid_amount > 0:
        fee.status = "Partially Paid"
    else:
        fee.status = "Pending"
    db.session.commit()

    return jsonify({
        "message": "Payment updated successfully",
        "payment": payment.to_dict(),
        "updated_fee": fee.to_dict()
    }), 200

   