from models.notification import Notification
from dbms.db import db

def create_notification(student_id,message):
    try:
        new_alert=Notification(
            student_id=student_id,
            message=message,
            is_read=False
        )
        db.session.add(new_alert)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return False