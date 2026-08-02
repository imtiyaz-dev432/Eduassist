from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt
from dbms.db import db
from models.course import Course
from models.institute import Institution

course_bp=Blueprint("course_bp",__name__,url_prefix="/owner/academics/courses")
#add course
@course_bp.route("/add/<int:institution_id>",methods=["POST"])
@jwt_required()
def add_course(institution_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    institution=Institution.query.filter_by(
        id=institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success":False,
            "message":"Institution not found"
        }),404

    course_name=data.get("course_name")
    category=data.get("category")
    course_fee=data.get("course_fee")
    duration=data.get("duration")
    syllabus=data.get("syllabus")
    eligibility=data.get("eligibility")
    certificate_available=data.get("certificate_available",False)
    placement_support=data.get("placement_support",False)
    mode=data.get('mode')
    level=data.get("level")
    description=data.get("description")

    if not course_name :
        return jsonify({
            "message":"Course name is required"
        }),400

    new_course = Course(
        institution_id=institution_id,
        course_name=course_name,
        category=category,
        course_fee=course_fee,
        duration=duration,
        mode=mode,
        level=level,
        description=description,
        syllabus=syllabus,
        eligibility=eligibility,
        certificate_available=certificate_available,
        placement_support=placement_support
    )

    db.session.add(new_course)
    db.session.commit()

    return jsonify({
        "success":True,
        "message": "Course created successfully"
       
    }), 201    

#get courses
@course_bp.route("/get/<int:institution_id>",methods=["GET"])
@jwt_required()
def get_course(institution_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id=int(get_jwt_identity())    
    institution=Institution.query.filter_by(
    id=institution_id,
    user_id=current_user_id
).first()

    if not institution:
        return jsonify({
            "message":"Institution not found"
        }),404
    
    courses=Course.query.filter_by(
         institution_id=institution_id
     ).all()

    course_list = []
    for course in courses:
       course_list.append({
        "id": course.id,
        "institution_id": course.institution_id,
        "course_name": course.course_name,
        "category": course.category,
        "course_fee": course.course_fee,
        "duration": course.duration,
        "mode": course.mode,
        "level": course.level,
        "description": course.description,
        "syllabus": course.syllabus,
        "eligibility": course.eligibility,
        "certificate_available": course.certificate_available,
        "placement_support": course.placement_support,
        "created_at": course.created_at.isoformat() if course.created_at else None
    })
    
    return jsonify({
    "success": True,
    "message": "Courses fetched successfully",
        "courses":course_list
    }),200

#update
@course_bp.route("/update/<int:course_id>", methods=["PATCH"])
@jwt_required()
def update_course(course_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())
    course = Course.query.filter_by(id=course_id).first()

    if not course:
        return jsonify({
            "success":False,
            "message": "Course not found"
        }), 404

    institution = Institution.query.filter_by(
        id=course.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success":False,
            "message": "Unauthorized to update this course"
        }), 403
    data = request.get_json()
    if not data:
        return jsonify({
            "success":False,
            "message": "Request body is required"
        }), 400

    course.course_name = data.get("course_name", course.course_name)
    course.category = data.get("category", course.category)
    course.course_fee = data.get("course_fee", course.course_fee)
    course.duration = data.get("duration", course.duration)
    course.mode = data.get("mode", course.mode)
    course.level = data.get("level", course.level)
    course.description = data.get("description", course.description)
    course.syllabus = data.get("syllabus", course.syllabus)
    course.eligibility = data.get("eligibility", course.eligibility)
    course.certificate_available = data.get(
        "certificate_available",
        course.certificate_available
    )
    course.placement_support = data.get(
        "placement_support",
        course.placement_support
    )

    db.session.commit()

    return jsonify({
        "message": "Course updated successfully"
    }), 200

#delete 
@course_bp.route("/delete/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    claims=get_jwt()
    if claims.get("role")!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    current_user_id = int(get_jwt_identity())

    course = Course.query.filter_by(id=course_id).first()

    if not course:
        return jsonify({
            "success":False,
            "message": "Course not found"
        }), 404

    institution = Institution.query.filter_by(
        id=course.institution_id,
        user_id=current_user_id
    ).first()

    if not institution:
        return jsonify({
            "success":False,
            "message": "Unauthorized to delete this course"
        }), 403

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "success":False,
        "message": "Course deleted successfully"
    }), 200