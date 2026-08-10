from dbms.db import db
from datetime import datetime
class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=True)
    mobile_no=db.Column(db.String(20),unique=True)
    password=db.Column(db.String(257),nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    institutions = db.relationship(
        "Institution",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


    