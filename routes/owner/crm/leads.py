from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from dbms.db import db
from models.leads import Lead
from models.institute import Institution


lead_bp = Blueprint(
    "lead_bp",
    __name__,
    url_prefix="/owner/leads"
)


#owner only
@lead_bp.route("/add/<int:institution_id>", methods=["POST"])
@jwt_required()
def add_lead(institution_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
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
            "message": "Institute not found or unauthorized"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    course_interest = data.get("course_interest")
    message = data.get("message")
    source = data.get("source", "Website")

    if not name or not phone:
        return jsonify({
            "success": False,
            "message": "Name and phone are required"
        }), 400

    lead = Lead(
        institution_id=institute.id,
        name=name,
        phone=phone,
        email=email,
        course_interest=course_interest,
        message=message,
        source=source,
        status="New"
    )

    db.session.add(lead)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Lead added successfully",
        "lead": lead.to_dict()
    }), 201


#view lead owner only
@lead_bp.route("/view/<int:institution_id>", methods=["GET"])
@jwt_required()
def view_leads(institution_id):
    claims = get_jwt()

    if claims.get("role") != "owner":
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
            "message": "Institute not found or unauthorized"
        }), 403

    leads = Lead.query.filter_by(
        institution_id=institute.id
    ).order_by(Lead.created_at.desc()).all()

    return jsonify({
        "success": True,
        "message": "Leads fetched successfully",
        "leads": [lead.to_dict() for lead in leads]
    }), 200


# Update lead owner only
@lead_bp.route("/update/<int:lead_id>", methods=["PATCH"])
@jwt_required()
def update_lead(lead_id):
    claims = get_jwt()

    if claims.get("role") != "owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    lead = Lead.query.filter_by(id=lead_id).first()

    if not lead:
        return jsonify({
            "success": False,
            "message": "Lead not found"
        }), 404

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=lead.institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Unauthorized to update this lead"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    lead.name = data.get("name", lead.name)
    lead.phone = data.get("phone", lead.phone)
    lead.email = data.get("email", lead.email)
    lead.course_interest = data.get("course_interest", lead.course_interest)
    lead.message = data.get("message", lead.message)
    lead.source = data.get("source", lead.source)
    lead.status = data.get("status", lead.status)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Lead updated successfully",
        "lead": lead.to_dict()
    }), 200


# Delete lead owner only
@lead_bp.route("/delete/<int:lead_id>", methods=["DELETE"])
@jwt_required()
def delete_lead(lead_id):
    claims = get_jwt()

    if claims.get("role") != "owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    lead = Lead.query.filter_by(id=lead_id).first()

    if not lead:
        return jsonify({
            "success": False,
            "message": "Lead not found"
        }), 404

    institute = Institution.query.filter_by(
        user_id=current_user_id,
        id=lead.institution_id
    ).first()

    if not institute:
        return jsonify({
            "success": False,
            "message": "Unauthorized to delete this lead"
        }), 403

    db.session.delete(lead)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Lead deleted successfully"
    }), 200
