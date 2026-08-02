from dbms.db import db
from datetime import datetime
class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )
    teacher_id=db.Column(db.Integer,db.ForeignKey("teachers.id"),nullable=False)

    batch_name = db.Column(db.String(150), nullable=False)
    batch_code = db.Column(db.String(50), nullable=True)

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    days = db.Column(db.String(150), nullable=True)
  

    start_time = db.Column(db.String(50), nullable=True)
    end_time = db.Column(db.String(50), nullable=True)

    mode = db.Column(db.String(50), nullable=False, default="Offline")
    

    classroom = db.Column(db.String(100), nullable=True)

    total_seats = db.Column(db.Integer, nullable=True)
    filled_seats = db.Column(db.Integer, default=0)

    fee_amount = db.Column(db.Float, nullable=True)
    monthly_fee = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(50), default="Active")
    

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    teacher = db.relationship(
    "Teacher",
    back_populates="batches"
)
    students = db.relationship(
    "Student",
    backref="batch",
    lazy=True,
    cascade="all, delete-orphan")
    
    fees = db.relationship("Fee", backref="batch", lazy=True, cascade="all, delete-orphan") 
    attendance_records = db.relationship(
    "Attendance",
    backref="batch",
    lazy=True,
    cascade="all, delete-orphan")

    assignments = db.relationship(
    "Assignment",
    backref="batch",
    lazy=True,
    cascade="all, delete-orphan")

    assignment_submissions = db.relationship(
    "AssignmentSubmission",
    backref="batch",
    lazy=True,
    cascade="all, delete-orphan")