from dbms.db import db 
from datetime import datetime

class AssignmentSubmission(db.Model):
    __tablename__ = "assignment_submissions"
    id=db.Column(db.Integer,primary_key=True)
    assignment_id=db.Column(db.Integer,db.ForeignKey("assignments.id"),nullable=False)
    institution_id=db.Column(db.Integer,db.ForeignKey("institutions.id"),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey("students.id"),nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("courses.id"),nullable=False)
    batch_id = db.Column(db.Integer,db.ForeignKey("batches.id"),nullable=False)
    answer_text=db.Column(db.Text,nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    stored_filename = db.Column(db.String(255), nullable=True)
    marks = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Submitted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    def to_dict(self):
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "institution_id": self.institution_id,
            "course_id": self.course_id,
            "batch_id": self.batch_id,
            "student_id": self.student_id,
            "answer_text": self.answer_text,
            "file_url": self.file_url,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "marks": self.marks,
            "feedback": self.feedback,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 