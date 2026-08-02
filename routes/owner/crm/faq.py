from flask import Blueprint, jsonify, request,current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dbms.db import db
from models.faq import Faq
from models.institute import Institution


faq_bp = Blueprint(
    "owner_faq_bp",
    __name__,
    url_prefix="/owner/faq"
)


# add FAQ
@faq_bp.route("/add/<int:institution_id>", methods=["POST"])
@jwt_required()
def faq_add(institution_id):
    claims = get_jwt()
    if claims.get("role")!="owner":

        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Institute not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    question = data.get("question", "").strip()
    answer = data.get("answer", "").strip()
    category = data.get("category", "").strip() or None

    if not question or not answer:
        return jsonify({
            "success": False,
            "message": "Question and answer are required"
        }), 400

    faq = Faq(
        institution_id=institute.id,
        question=question,
        answer=answer,
        category=category,
        is_active=True
    )

    db.session.add(faq)
    try:
       db.session.commit()
       return jsonify({
        "success": True,
        "message": "FAQ added successfully",
        "faq": faq.to_dict()
    }), 201
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add FAQ")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500

# get FAQs
@faq_bp.route("/view/<int:institution_id>", methods=["GET"])
@jwt_required()
def get_faq(institution_id):
    claims = get_jwt()

    if claims.get("role")!="owner":

        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Institute not found"
        }), 404

    faqs = Faq.query.filter_by(
        institution_id=institution_id
    ).order_by(Faq.created_at.desc()).all()

    faq_list = []

    for faq in faqs:
        faq_list.append(faq.to_dict())

    return jsonify({
        "success": True,
        "message": "FAQ fetched successfully",
        "faqs": faq_list
    }), 200
 
# update FAQ
@faq_bp.route("/update/<int:faq_id>", methods=["PATCH"])
@jwt_required()
def update_faq(faq_id):
    claims = get_jwt()

    if claims.get("role")!="owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    faq = Faq.query.filter_by(id=faq_id).first()

    if not faq:
        return jsonify({
            "success": False,
            "message": "FAQ not found"
        }), 404

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=faq.institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Institute not found"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400
  
    if "category" in data:
       faq.category = data.get("category", "").strip() or None
    if "question" in data:
      question = data.get("question").strip()

      if not question:
        return jsonify({
            "success": False,
            "message": "Question cannot be empty"
        }), 400

      faq.question = question

    if "answer" in data:
      answer = data.get("answer", "").strip()

      if not answer:
        return jsonify({
            "success": False,
            "message": "Answer cannot be empty"
        }), 400

      faq.answer = answer
    
    if "is_active" in data:
        if not isinstance(data["is_active"],bool):
             return jsonify({
            "success": False,
            "message": "is_active must be true or false"
        }), 400
        faq.is_active = data["is_active"]
    try:
      db.session.commit()
      return jsonify({
        "success": True,
        "message": "FAQ updated successfully",
        "faq": faq.to_dict()
    }), 200
    except Exception:
      db.session.rollback()
      current_app.logger.exception("Failed to update FAQ")
      return jsonify({
        "success":False,
        "message":"Something went wrong"
      }),500

# delete FAQ
@faq_bp.route("/delete/<int:faq_id>", methods=["DELETE"])
@jwt_required()
def delete_faq(faq_id):
    claims = get_jwt()

    if claims.get("role") !="owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    faq = Faq.query.filter_by(id=faq_id).first()

    if not faq:
        return jsonify({
            "success": False,
            "message": "FAQ not found"
        }), 404

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=faq.institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Institute not found"
        }), 403

    
    try:
      db.session.delete(faq)   
      db.session.commit()
      return jsonify({
        "success": True,
        "message": "FAQ deleted successfully"
    }), 200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete FAQ")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500    
    