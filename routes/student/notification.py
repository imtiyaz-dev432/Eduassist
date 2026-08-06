from flask import jsonify,Blueprint,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import Notification
from dbms.db import db

notif_bp=Blueprint('notif_bp',__name__,url_prefix="/notifications")

@notif_bp.route("/my-alerts",methods=["GET"])
@jwt_required()
def get_my_alerts():
    student_id=get_jwt_identity()
    alerts=Notification.query.filter_by(student_id=student_id,is_read=False).all()
    alert_list=[a.to_dict() for a in alerts]
    return jsonify({
        "success": True,
        "count": len(alert_list), # Badge number yahan se aayega
        "data": alert_list
    }), 200
@notif_bp.route("/mark-read", methods=["PATCH"])
@jwt_required()
def mark_alert_read():
    try:
        student_id = get_jwt_identity()

        updated = Notification.query.filter_by(
            student_id=student_id,
            is_read=False
        ).update(
            {"is_read": True},
            synchronize_session=False
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{updated} alerts marked as read."
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error updating alerts."
        }), 500