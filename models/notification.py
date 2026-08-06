from dbms.db import db
from datetime import datetime
class Notification(db.Model):
    __tablename__="notifications"
    id = db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey("students.id"),nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)     
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat()
        }