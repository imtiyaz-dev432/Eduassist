from datetime import datetime
from dbms.db import db

class Teacher(db.Model):
    __tablename__="teachers"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    mobile_no=db.Column(db.String(30),nullable=False,unique=True)
    email=db.Column(db.String(250),nullable=False,unique=True)
    password=db.Column(db.String(260),nullable=True)
    institution_id=db.Column(db.Integer,db.ForeignKey("institutions.id"),nullable=False)
    login_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )
    batches=db.relationship(
        "Batch",
        back_populates="teacher",
        lazy=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    institution = db.relationship(
        "Institution",
        back_populates="teachers"
    )


    def to_dict(self):
       return {
        "id": self.id,
        "name":self.name,
        "institution_id": self.institution_id,
        "email": self.email,
        "mobile_no": self.mobile_no,
        "login_enabled": self.login_enabled,
        "is_active":self.is_active,
        "created_at":self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None
    }

  