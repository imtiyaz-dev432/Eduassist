# The working of this page is loading .env 
import os
from dotenv import load_dotenv
from flask_sqlalchemy  import SQLAlchemy
load_dotenv()


class Config:
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    REDIS_URL=os.getenv("REDIS_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")    
    SQLALCHEMY_TRACK_MODIFICATIONS=False    
    OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
    ASSIGNMENT_UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads", "assignments"
    )#his creates a specific folder path on your computer/server. It tells the app,
    # "When a student uploads their homework, save it exactly in this folder."
