from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.student import Student
from models.institute import Institution
from models.course import Course
from models.batch import Batch
from models.fee import Fee
from models.payment import Payment
from models.attendance import Attendance
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission

student_dashboard_bp = Blueprint(
    "student_dashboard_bp",
    __name__,
    url_prefix="/student"
)
@student_dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():
    claims = get_jwt()

    if claims.get("role") != "student":
        return jsonify({
            "success": False,
            "message": "Student access only"
        }), 403

    current_student_id = int(get_jwt_identity())

    student = Student.query.filter_by(
        id=current_student_id
    ).first()

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    institute = Institution.query.filter_by(
        id=student.institution_id
    ).first()

    course = Course.query.filter_by(
        id=student.course_id
    ).first()

    batch = Batch.query.filter_by(
        id=student.batch_id
    ).first()

    
    fee = Fee.query.filter_by(
        student_id=student.id
    ).first()
    
    fee_summary = {
        "total_fee": fee.total_fee if fee else 0,
        "paid_amount": fee.paid_amount if fee else 0,
        "due_amount": fee.due_amount if fee else 0,
        "status": fee.status if fee else "Not Created",
        "due_date": fee.due_date.isoformat() if fee and fee.due_date else None,
        "is_due":fee.due_amount if fee and fee.due_amount else 0
        
    }
      
    total_payments = Payment.query.filter_by(
        student_id=student.id
    ).count()

  
    total_attendance = Attendance.query.filter_by(
        student_id=student.id
    ).count()

    present_count = Attendance.query.filter_by(
        student_id=student.id,
        status="Present"
    ).count()

    absent_count = Attendance.query.filter_by(
        student_id=student.id,
        status="Absent"
    ).count()

    late_count = Attendance.query.filter_by(
        student_id=student.id,
        status="Late"
    ).count()

    attendance_percentage = 0

    if total_attendance > 0:
        attendance_percentage = round((present_count / total_attendance) * 100, 2)

    attendance_summary = {
        "total_attendance": total_attendance,
        "present": present_count,
        "absent": absent_count,
        "late": late_count,
        "attendance_percentage": attendance_percentage
    }

    
    total_assignments = Assignment.query.filter_by(
        batch_id=student.batch_id,
        status="Active"
    ).count()

    submitted_assignments = AssignmentSubmission.query.filter_by(
        student_id=student.id
    ).count()

    pending_assignments = total_assignments - submitted_assignments

    if pending_assignments < 0:
        pending_assignments = 0

    assignment_summary = {
        "total_assignments": total_assignments,
        "submitted_assignments": submitted_assignments,
        "pending_assignments": pending_assignments,
        "has_pending":True if pending_assignments>0 else False
    }

    return jsonify({
        "success": True,
        "message": "Student dashboard fetched successfully",
        "student": {
            "id": student.id,
            "student_name": student.student_name,
            "email": student.email,
            "phone": student.phone,
            "status": student.status
        },
        "institution": {
            "id": institute.id if institute else None,
            "name": institute.institution_name if institute else None
        },
        "course": {
            "id": course.id if course else None,
            "course_name": course.course_name if course else None
        },
        "batch": {
            "id": batch.id if batch else None,
            "batch_name": batch.batch_name if batch else None
        },
        "fee_summary": fee_summary,
        "payment_summary": {
            "total_payments": total_payments
        },
        "attendance_summary": attendance_summary,
        "assignment_summary": assignment_summary
    }), 200