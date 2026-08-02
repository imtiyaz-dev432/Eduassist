from dbms.db import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__="quizzes"
    id=db.Column(db.Integer,primary_key=True)
    institution_id=db.Column(db.Integer,db.ForeignKey("institutions.id"),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey("courses.id"),nullable=False)
    batch_id=db.Column(db.Integer,db.ForeignKey("batches.id"),nullable=False)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    difficulty = db.Column(db.String(50), default="Easy")
    total_marks = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="Active")    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    questions = db.relationship(
    "QuizQuestion",
    backref="quiz",
    lazy=True,
    cascade="all, delete-orphan")

    submissions = db.relationship(
    "QuizSubmission",
    backref="quiz",
    lazy=True,
    cascade="all, delete-orphan")

    batch = db.relationship(
    "Batch",
    backref="quizzes",
    lazy=True
)
    def to_dict(self):
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "course_id": self.course_id,
            "batch_id": self.batch_id,
            "title": self.title,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "total_marks": self.total_marks,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }