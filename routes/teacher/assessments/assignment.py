import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_from_directory,
    url_for,
)
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime 
from dbms.db import db

from models.institute import Institution
from models.batch import Batch
from models.assignment import Assignment
from models.student import Student
from utils.file_upload import save_pdf

assignment_for_student_bp=Blueprint("assignment_for_student_bp",__name__,url_prefix="/teacher/assessments/assignment")
@assignment_for_student_bp.route("/add/<int:batch_id>",methods=['POST'])
@jwt_required()
def add_assignment(batch_id):
    claims=get_jwt()
    if claims.get("role") !="owner":
        return jsonify({
            "success":False,

            "message":"owner access only "
        }),403
    current_user_id=int(get_jwt_identity())
    batch=Batch.query.filter_by(
        id=batch_id
    ).first()

    if not batch:
        return jsonify({
            "success":False,
            "message":"Batch not found"
        }),404

    institute=Institution.query.filter_by(
        id=batch.institution_id,
        user_id=current_user_id
    ).first()

    if not institute:
        return jsonify({
            "success":False,
            "message":"Institute not found"
        }),404

    # A file upload must use multipart/form-data. JSON remains supported for
    # clients that create an assignment without uploading a PDF.
    data = request.get_json(silent=True) if request.is_json else request.form
    uploaded_file = request.files.get("file")
   


    if not data and not uploaded_file:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        })    ,400

    title=data.get("title")
    description=data.get("description")
    file_url=data.get("file_url")
    due_date=data.get("due_date")
    max_marks=data.get("max_marks")
    status=data.get("status","Active")
    if not title:
        return jsonify({
            "success":False,
           "message":"Title is required"}),400

    due_date_obj=None
    if due_date:
        try:
            due_date_obj=datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).date()
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Due date must use YYYY-MM-DD format"
            }), 400

    if max_marks not in (None, ""):
        try:
            max_marks = int(max_marks)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Max marks must be a whole number"
            }), 400

        if max_marks < 0:
            return jsonify({
                "success": False,
                "message": "Max marks cannot be negative"
            }), 400
    else:
        max_marks = None

    allowed_status = ["Active", "Closed", "Draft"]
    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": "Invalid assignment status"
        }), 400

    saved_pdf = None
    if uploaded_file:
        try:
            saved_pdf = save_pdf(
                uploaded_file,
                current_app.config["ASSIGNMENT_UPLOAD_FOLDER"]
            )
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400
        except OSError:
            current_app.logger.exception("Unable to save assignment PDF")
            return jsonify({
                "success": False,
                "message": "Unable to save assignment PDF"
            }), 500

        if saved_pdf:
            file_url = url_for(
                "assignment_for_student_bp.download_assignment_pdf",
                filename=saved_pdf["stored_filename"]
            )
        
    new_assignment = Assignment(
        institution_id=batch.institution_id,
        course_id=batch.course_id,
        batch_id=batch.id,
        title=title,
        description=description,
        file_url=file_url,
        due_date=due_date_obj,
        max_marks=max_marks,
        status=status
    )

    try:
        db.session.add(new_assignment)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        if saved_pdf:
            saved_file_path = os.path.join(
                current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
                saved_pdf["stored_filename"]
            )
            try:
                os.remove(saved_file_path)
            except OSError:
                current_app.logger.exception(
                    "Unable to remove assignment PDF after database failure"
                )
        current_app.logger.exception("Unable to create assignment")
        return jsonify({
            "success": False,
            "message": "Unable to create assignment"
        }), 500


    return jsonify({
        "success": True,
        "message": "Assignment created successfully",
        "assignment": new_assignment.to_dict()
    }), 201               


@assignment_for_student_bp.route("/file/<string:filename>", methods=["GET"])
@jwt_required()
def download_assignment_pdf(filename):
    assignment = Assignment.query.filter(
        Assignment.file_url.like(f"%{filename}%")
    ).first()

    if not assignment:
        return jsonify({
            "success": False,
            "message": "Assignment file not found"
        }), 404
    file_url = url_for(
    "assignment_bp.download_assignment_pdf",
    filename=filename
)
   
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role == "owner":
        is_authorized = Institution.query.filter_by(
            id=assignment.institution_id,
            user_id=current_user_id
        ).first() is not None
    else:
        is_authorized = False

    if not is_authorized:
        return jsonify({
            "success": False,
            "message": "Unauthorized to access this assignment file"
        }), 403
    print(current_app.config["ASSIGNMENT_UPLOAD_FOLDER"])
    print(filename)
    print(os.path.join(current_app.config["ASSIGNMENT_UPLOAD_FOLDER"], filename))
    print(os.path.exists(os.path.join(current_app.config["ASSIGNMENT_UPLOAD_FOLDER"], filename)))    

    

    return send_from_directory(
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
        filename,
        mimetype="application/pdf"
    )

@assignment_for_student_bp.route("/file/replace/<int:assignment_id>",methods=["PATCH"])
@jwt_required()
def replace(assignment_id):
    claims=get_jwt().get("role")
    if claims!="owner":
        return jsonify({
            "success":False,
            "message":"Owner access only"
        }),403
    assignment=Assignment.query.filter_by(
        id=assignment_id
    ).first()
    if not assignment:
        return jsonify({
            "success":False,
            "message":"Assignment not found"
        }),404
    current_user_id=int(get_jwt_identity())    
    institute=Institution.query.filter_by(
     id=assignment.institution_id,
     user_id=current_user_id
    ).first()
    if not institute:
        return jsonify({
            "success":False,
            "message":"Unauthorized to replace the file"
        }),403
    data = request.get_json(silent=True) if request.is_json else request.form
    
    
    assignment.title=data.get("title",assignment.title)
    assignment.description=data.get("description",assignment.description)
    assignment.due_date=data.get("due_date",assignment.due_date)
    assignment.max_marks=data.get("max_marks",assignment.max_marks)
    assignment.status=data.get("status",assignment.status)
    uploaded_file = request.files.get("file")

    if uploaded_file:
        saved_pdf = save_pdf(
        uploaded_file,
        current_app.config["ASSIGNMENT_UPLOAD_FOLDER"]
    )

    if assignment.file_url:
        old_filename = assignment.file_url.split("/")[-1]
        old_file_path = os.path.join(
            current_app.config["ASSIGNMENT_UPLOAD_FOLDER"],
            old_filename
        )
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

    assignment.file_url = url_for(
        "assignment_bp.download_assignment_pdf",
        filename=saved_pdf["stored_filename"]
    )

    db.session.commit()

    return jsonify({
    "success": True,
    "message": "Assignment updated successfully"
}), 200