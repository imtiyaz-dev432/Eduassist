from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from models.batch import Batch
from models.student import Student

teacher_batch_student_bp=Blueprint("teacher_batch_student_bp",__name__,url_prefix="/teacher/batch")
@teacher_batch_student_bp.route("/<int:batch_id>/students",methods=["GET"])
@jwt_required()
def get_batch_student(batch_id):
    claims=get_jwt()
    
    print("🔥 TOKEN CLAIMS:", claims)
    print("🔥 LOGGED IN USER ID:", get_jwt_identity())
    if claims.get("role") not in ["teacher","owner"]:
        return jsonify({
            "success":False,
            "message":"Teacher/Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    if claims.get("role") == "teacher":
        batch = Batch.query.filter_by(id=batch_id, teacher_id=current_user_id).first()
    else:
        # Owner ke liye teacher_id check nahi karna hai
        batch = Batch.query.filter_by(id=batch_id).first()
    if not batch:
        return jsonify({
            "success":False,
            "message":"Batch Not found"
        }),404
    students=Student.query.filter_by(batch_id=batch_id).all()
    if not students:
        return jsonify({
            "success":False,
            "message":"This batch doesnot have student"
        }),400
    student_list=[]
    for s in students:
        student_list.append({
            "id": s.id,
            "name": s.student_name,
            "mobile_no": s.phone
        })
        

    return jsonify({
        "success": True,
        "batch_name": batch.batch_name,
        "students": student_list
    }), 200