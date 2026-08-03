from dbms.db import db 
from datetime import datetime

class Institution(db.Model):
    __tablename__="institutions"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    institution_name = db.Column(db.String(250), nullable=False)

    institution_type = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=True)

    address = db.Column(db.Text, nullable=True)

    city = db.Column(db.String(100), nullable=False)

    state = db.Column(db.String(60), nullable=False)

    country = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(35), nullable=True)

    email = db.Column(db.String(150), nullable=True)

    website_url = db.Column(db.String(350), nullable=True)

    opening_hours = db.Column(db.String(100), nullable=True)

    logo_url = db.Column(db.String(400), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    courses = db.relationship(
        "Course",
        backref="institution",
        lazy=True,
        cascade="all, delete-orphan")
        
    batches = db.relationship(
    "Batch",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    students = db.relationship(
    "Student",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    fees = db.relationship("Fee", backref="institution", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship(
    "Payment",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    attendance_records = db.relationship(
    "Attendance",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    fee_reminders = db.relationship(
    "FeeReminder",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    assignments = db.relationship(
    "Assignment",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    assignment_submissions = db.relationship(
    "AssignmentSubmission",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    leads = db.relationship(
    "Lead",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    faqs = db.relationship(
    "Faq",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")

    chat_history = db.relationship(
    "ChatHistory",
    backref="institution",
    lazy=True,
    cascade="all, delete-orphan")
    teachers = db.relationship(
    "Teacher",
    back_populates="institution",
    cascade="all, delete-orphan"
)