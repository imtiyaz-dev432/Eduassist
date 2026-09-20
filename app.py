from flask import Flask,jsonify,request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from dbms.db import db
from utils.rate import limiter
from utils.extensions import redis_client
from flask_migrate import Migrate
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST,Histogram

#models
from models.user import User
from models.institute import Institution
from models.course import Course
from models.batch import Batch
from models.student import Student
from models.fee import Fee
from models.payment import Payment
from models.attendance import Attendance
from models.fee_reminder import FeeReminder
from models.assignment import Assignment
from models.assignment_submission import AssignmentSubmission
from models.quize import Quiz
from models.quiz_question import QuizQuestion
from models.faq import Faq
from models.leads import Lead
from models.chat import ChatHistory
from models.quizsubmission import QuizSubmission
from models.quiz_submission_answer import QuizSubmissionAnswer
from models.teacher import Teacher
#route
from routes.owner.auth import auth_bp
from routes.owner.otp import otp_bp
from routes.owner.institution import institute_bp
from routes.owner.academic.course import course_bp
from routes.owner.academic.batch import batch_bp
from routes.teacher.academics.student import teacher_student_bp
from routes.owner.finance.fee import fee_bp
from routes.owner.finance.payment import payment_bp
from routes.teacher.operations.attendance import attendance_bp
from routes.owner.finance.fee_reminder import fee_reminder_bp
from routes.teacher.assessments.assignment import assignment_for_student_bp
from routes.teacher.assessments.assignment_check_ import teacher_see_student_bp
from routes.teacher.assessments.quize import quiz_bp
from routes.teacher.assessments.quiz_question import quiz_question_bp
from routes.student.student_auth import student_auth_bp
from routes.student.dashboard import student_dashboard_bp
from routes.student.finance.fee import student_fee_bp
from routes.student.finance.payment  import student_payment_bp
from routes.student.operation.attendance import student_attendance_bp
from routes.student.assessments.assignment_view_submission import assignment_submission_view_bp
from routes.student.assessments.quiz import student_quiz_bp
from routes.student.assessments.quiz_question import student_quiz_question_bp
from routes.student.assessments.quiz_submission import student_quiz_submission_bp
from routes.teacher.assessments.quiz_submission import teacher_quiz_view_bp
from routes.owner.crm.faq import faq_bp
from routes.owner.crm.leads import lead_bp
from routes.owner.crm.chat_history import chat_history_bp
from routes.ai.admission_bot import admission_bot_bp
from routes.student.assessments.assignment_view_submission import assignment_submission_view_bp
from routes.student.assessments.assignment_submission import student_assignment_submission_bp
from routes.student.assessments.assignment_view import student_assignment_bp
from routes.student.assessments.student_assignment_result import student_result_bp
from routes.owner.teacher_add import teacher_add_bp
from routes.teacher.teacher_login import teacher_login_bp
from routes.teacher.dashboard import teacher_dashboard_bp
from routes.owner.dashboard import owner_dashboard_bp
from utils.celery import make_celery
from routes.student.notification import notif_bp
from routes.teacher.teacher_student import teacher_batch_student_bp

app=Flask(__name__)
app.config.from_object(Config)
celery=make_celery(app)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return '', 200
db.init_app(app)
migrate=Migrate(app,db)
jwt=JWTManager(app)
limiter.init_app(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header,jwt_payload):
   jti=jwt_payload['jti']
   return redis_client.exists(f"blocklist:{jti}")
@jwt.revoked_token_loader
def revoked_token_loader(jwt_header,jwt_payload):
      return ({
        "description":"user has been logged out",
        "error":"token-revoked"
      },401)

#register blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(institute_bp)
app.register_blueprint(course_bp)
app.register_blueprint(batch_bp)
app.register_blueprint(teacher_student_bp)
app.register_blueprint(fee_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(fee_reminder_bp)
app.register_blueprint(assignment_for_student_bp)
app.register_blueprint(teacher_see_student_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(quiz_question_bp)
app.register_blueprint(student_auth_bp)
app.register_blueprint(assignment_submission_view_bp)
app.register_blueprint(student_result_bp)
app.register_blueprint(student_assignment_submission_bp)
app.register_blueprint(student_assignment_bp)
app.register_blueprint(student_dashboard_bp)
app.register_blueprint(student_fee_bp)
app.register_blueprint(student_payment_bp)
app.register_blueprint(student_attendance_bp)

app.register_blueprint(student_quiz_bp)
app.register_blueprint(student_quiz_question_bp)
app.register_blueprint(student_quiz_submission_bp)
app.register_blueprint(teacher_quiz_view_bp)
app.register_blueprint(faq_bp)
app.register_blueprint(lead_bp)
app.register_blueprint(chat_history_bp)
app.register_blueprint(admission_bot_bp)
app.register_blueprint(teacher_add_bp)
app.register_blueprint(teacher_login_bp)
app.register_blueprint(teacher_dashboard_bp)
app.register_blueprint(owner_dashboard_bp)
app.register_blueprint(notif_bp)
app.register_blueprint(teacher_batch_student_bp)
REQUEST_COUNT = Counter(
    "flask_requests_total",
    "Total number of Flask requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "flask_request_duration_seconds",
    "Flask request latency in seconds",
    ["method", "endpoint", "status"]
)

# @app.before_request
# def count_request():
#         if request.path != "/metrics":
#             REQUEST_COUNT.inc()
@app.before_request
def start_timer():
    if request.path != "/metrics":
        request._start_time = time.perf_counter()



@app.after_request
def record_request_metrics(response):
    if request.path != "/metrics":
        endpoint = request.endpoint or "unknown"

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        duration = time.perf_counter() - request._start_time

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).observe(duration)

    return response    
@app.route("/metrics")
@limiter.exempt
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
@app.before_request
def log_request_info():
    print(f"Incoming Request -> URL: {request.path}, Method: {request.method}", flush=True)
@app.route("/",methods=["GET"])
@limiter.exempt
def home():
    return jsonify({
        "message":"eduassist ai is running successfully"
    }),200
if __name__ == "__main__":
    app.run(debug=True)

# While instrumenting Flask with Prometheus, I initially 
# encountered HTTP 429 on the /metrics endpoint because the global
#  rate limiter was also applied to Prometheus scrape requests.
#   I excluded the monitoring endpoint from rate limiting so that
#    observability traffic would not interfere with application monitoring


# sum(rate(flask_requests_total[5m]))
# means:
# Sabhi matching Flask time-series ki requests/sec ko add karke total requests/sec batao
