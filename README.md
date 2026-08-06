# EduAssist AI

EduAssist AI is a Flask-based backend system for coaching institutes that helps manage students, fees, attendance, assignments, quizzes, and notifications.

## Features

- Student Authentication (JWT)
- OTP Email Verification
- Attendance Management
- Fee Management
- Monthly Fee Reminder
- Web Notifications
- Assignment Management
- Quiz Management
- Owner Dashboard
- Teacher Dashboard
- Lead Management
- Redis + Celery Background Tasks

## Tech Stack

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- Redis
- Celery
- JWT

## Installation

```bash
git clone https://github.com/imtiyaz-dev432/eduassist-ai.git

cd eduassist-ai

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file.

```
DATABASE_URL=
JWT_SECRET_KEY=
REDIS_URL=
BREVO_API_KEY=
```

## Run Flask

```bash
flask run
```

## Run Celery Worker

```bash
celery -A app.celery worker --loglevel=info
```

## Run Celery Beat

```bash
celery -A app.celery beat --loglevel=info
```

## Folder Structure

```
routes/
models/
utils/
migrations/
```

## Future Improvements

- AI Chatbot
- Analytics Dashboard
- Payment Gateway
- Docker Deployment

## Author

Md Imtiyaz