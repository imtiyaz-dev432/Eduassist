from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dbms.db import db
from models.faq import Faq
from models.institute import Institution


teacher_faq_bp = Blueprint(
    "teacher_faq_bp",
    __name__,
    url_prefix="/teacher/faq"
)


# add FAQ
@teacher_faq_bp.route("/add/<int:institution_id>", methods=["POST"])
@jwt_required()
def faq_add(institution_id):
    claims = get_jwt()
    if claims.get("role") not in ["teacher", "owner"]:
        return jsonify({
            "success": False,
            "message": "Teacher access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Unauthorized to add FAQ"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    question = data.get("question")
    answer = data.get("answer")
    category = data.get("category")

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
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "FAQ added successfully",
        "faq": faq.to_dict()
    }), 201


# get FAQs
@teacher_faq_bp.route("/view/<int:institution_id>", methods=["GET"])
@jwt_required()
def get_faq(institution_id):
    claims = get_jwt()

    if claims.get("role") not in ["teacher", "owner"]:
        return jsonify({
            "success": False,
            "message": "Teacher access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Unauthorized to get FAQ"
        }), 403

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
@teacher_faq_bp.route("/update/<int:faq_id>", methods=["PATCH"])
@jwt_required()
def update_faq(faq_id):
    claims = get_jwt()

    if claims.get("role") not in ["teacher", "owner"]:
        return jsonify({
            "success": False,
            "message": "Teacher access only"
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
            "message": "Unauthorized to update FAQ"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    faq.question = data.get("question", faq.question)
    faq.answer = data.get("answer", faq.answer)
    faq.category = data.get("category", faq.category)

    if "is_active" in data:
        faq.is_active = data.get("is_active")

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "FAQ updated successfully",
        "faq": faq.to_dict()
    }), 200


# delete FAQ
@teacher_faq_bp.route("/delete/<int:faq_id>", methods=["DELETE"])
@jwt_required()
def delete_faq(faq_id):
    claims = get_jwt()

    if claims.get("role") not in ["teacher", "owner"]:
        return jsonify({
            "success": False,
            "message": "Teacher access only"
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
            "message": "Unauthorized to delete FAQ"
        }), 403

    db.session.delete(faq)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "FAQ deleted successfully"
    }), 200