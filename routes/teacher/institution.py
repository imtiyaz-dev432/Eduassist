from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt

from dbms.db import db
from models.institute import Institution

institute_bp=Blueprint("institution_bp",__name__,url_prefix="/teacher/institution")
#add institute
@institute_bp.route("/register",methods=["POST"])
@jwt_required()
def create_institution():
    claims=get_jwT()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner accss only"
        }),403
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    if not data:
        return jsonify({
            "message":"Request body is required"
        }),400

    institution_name=data.get("institution_name")
    institution_type = data.get("institution_type")
    description = data.get("description")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    country = data.get("country")
    phone = data.get("phone")
    email = data.get("email")
    website_url = data.get("website_url")
    opening_hours = data.get("opening_hours")
    logo_url = data.get("logo_url")
    if not institution_name or not institution_type or not city or not state or not country:
        return jsonify({
            "message": "Institution name, type, city, state and country are required"
        }), 400
    
    new_institution=Institution(
        user_id=current_user_id,
        institution_name=institution_name,
        institution_type=institution_type,
        description=description,
        address=address,
        city=city,
        state=state,
        country=country,
        phone=phone,
        email=email,
        website_url=website_url,
        opening_hours=opening_hours,
        logo_url=logo_url
    )

    db.session.add(new_institution)
    db.session.commit()
    return jsonify({
        "success":True,
        "message": "Institution created successfully"
    }), 201
#get institute
@institute_bp.route("/get",methods=["GET"])
@jwt_required()
def get_institute():
    claims=get_jwT()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner accss only"
        }),403
    current_user_id=int(get_jwt_identity())
    existing_institutions=Institution.query.filter_by(user_id=current_user_id).all()
    get_institute=[]
    for institution in existing_institutions:
        get_institute.append({
            "id": institution.id,
            "user_id": institution.user_id,
            "institute_name": institution.institution_name,
            "institute_type": institution.institution_type,
            "description": institution.description,
            "address": institution.address,
            "city": institution.city,
            "state": institution.state,
            "country": institution.country,
            "phone": institution.phone,
            "email": institution.email,
            "website_url": institution.website_url,
            "opening_hours": institution.opening_hours,
            "logo_url": institution.logo_url,
            "created_at": institution.created_at.isoformat() if institution.created_at else None
        })

    return jsonify({
       "success":True,
        "institutions":get_institute
    })   ,200

#Update  institute
@institute_bp.route("/update/<int:institute_id>",methods=["PATCH"])
@jwt_required()
def update_institute(institute_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    if not data:
        return jsonify({
            "message":"Request body is required"
        }),400
    institute=Institution.query.filter_by(id=institute_id,user_id=current_user_id).first()

    if not institute:
        return jsonify({
            "message":"Institute not found"
        }) ,404

    institute.institution_name = data.get("institution_name", institute.institution_name)
    institute.institution_type = data.get("institution_type", institute.institution_type)
    institute.description = data.get("description", institute.description)
    institute.address = data.get("address", institute.address)
    institute.city = data.get("city", institute.city)
    institute.state = data.get("state", institute.state)
    institute.country = data.get("country", institute.country)
    institute.phone = data.get("phone", institute.phone)
    institute.email = data.get("email", institute.email)
    institute.website_url = data.get("website_url", institute.website_url)
    institute.opening_hours = data.get("opening_hours", institute.opening_hours)
    institute.logo_url = data.get("logo_url", institute.logo_url)
    db.session.commit()
    return jsonify({
        "success":True,
        "message": "Institute updated successfully"       
    }), 200    
#delete institute
@institute_bp.route("/delete/<int:institute_id>",methods=["DELETE"]) 
@jwt_required()
def delete_institute(institute_id):
    current_user_id=int(get_jwt_identity())
    institute=Institution.query.filter_by(
        id=institute_id,
        user_id=current_user_id
    )   .first()

    if not institute:
        return jsonify({
            "success":False,
            "message":"Institute not found"
        }),404
    db.session.delete(institute)
    db.session.commit()
    return jsonify({
        "success":True,
        "message":"Institute deleted successfully"
    })    ,200