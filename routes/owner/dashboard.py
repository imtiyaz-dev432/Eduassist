from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from dbms.db import db

# Import your models
from models.institute import Institution
from models.teacher import Teacher
from models.student import Student
from models.batch import Batch
from models.course import Course

owner_dashboard_bp = Blueprint("owner_dashboard_bp", __name__, url_prefix="/owner/dashboard")

@owner_dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard_stats():
    # 1. Security Check: Only owners allowed
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({
            "success": False,
            "message": "Owner access only"
        }), 403

    current_user_id = int(get_jwt_identity())

    try:
        # 2. Fetch the Owner's Institution
        institute = Institution.query.filter_by(user_id=current_user_id).first()
        if not institute:
            return jsonify({
                "success": False,
                "message": "Institution not found. Please set up your institution first."
            }), 404

        # 3. Calculate Core Metrics using .count() (Extremely fast database query)
        total_teachers = Teacher.query.filter_by(institution_id=institute.id).count()
        total_students = Student.query.filter_by(institution_id=institute.id).count()
        total_courses = Course.query.filter_by(institution_id=institute.id).count()
        total_batches = Batch.query.filter_by(institution_id=institute.id).count()
        
        # Assuming your Batch model has a 'status' field. If not, you can remove this!
        active_batches = Batch.query.filter_by(institution_id=institute.id, status="Active").count()

        # 4. Fetch Recent Activity (e.g., 5 most recently created batches)
        recent_batches = Batch.query.filter_by(
            institution_id=institute.id
        ).order_by(Batch.id.desc()).limit(5).all()

        recent_batch_list = []
        for batch in recent_batches:
            # Note: If your Batch model uses different names (like 'name' instead of 'batch_name', 
            # or 'capacity' instead of 'total_seats'), update them here!
            recent_batch_list.append({
                "id": batch.id,
                "batch_name": getattr(batch, 'batch_name', 'Unnamed Batch'),
                "status": getattr(batch, 'status', 'Active'),
                "total_seats": getattr(batch, 'total_seats', 0)
            })

        # 5. Return the aggregated data
        return jsonify({
            "success": True,
            "message": "Dashboard data fetched successfully",
            "data": {
                # FIXED: Changed institute.name to institute.institution_name based on your model
                "id":institute.id,
                "institution_name": institute.institution_name, 
                "metrics": {
                    "total_teachers": total_teachers,
                    "total_students": total_students,
                    "total_courses": total_courses,
                    "total_batches": total_batches,
                    "active_batches": active_batches
                },
                "recent_batches": recent_batch_list
            }
        }), 200

    except Exception as e:
        current_app.logger.exception("Failed to fetch owner dashboard data")
        # This will output the exact reason if it crashes again (e.g., if a Batch column is wrong)
        return jsonify({
            "success": False,
            "message": f"Server crash reason: {str(e)}" 
        }), 500