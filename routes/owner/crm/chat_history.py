from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dbms.db import db
from models.chat import ChatHistory
from models.institute import Institution
from models.leads import Lead

chat_history_bp=Blueprint("chat_history_bp",__name__,url_prefix="/teacher/chat_history")
#view
@chat_history_bp.route("/get/<int:institution_id>",methods=["GET"])
@jwt_required()
def get_chat(institution_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return  jsonify({
            "success":False,
            "message":"Owner access only "
        }),403
    current_user_id=int(get_jwt_identity())    
    institute=Institution.query.filter_by(
       user_id=current_user_id,
       id=institution_id
    )  .first()
    
    if not institute:
        return jsonify({
            "success":False,
            "message":"Institute not found or Unauthorized"
        }),403

    chats=ChatHistory.query.filter_by(
        institution_id=institute.id
    ).order_by(ChatHistory.created_at.desc()).all()
    
    return jsonify({
        "success":True,
        "message":"Data fetched successfully",
        "chats":[chat.to_dict() for chat in chats]
    })    
