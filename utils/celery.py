from celery import Celery, Task
from celery.schedules import crontab

def make_celery(app):

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.import_name,
        broker=app.config.get(
            "CELERY_BROKER_URL",
            "redis://localhost:6379/1"
        ),
        backend=app.config.get(
            "CELERY_BACKEND_URL",
            "redis://localhost:6379/2"
        ),
        task_cls=FlaskTask,
       
        include=['utils.email_otp'] 
    )
    
 
    celery_app.conf.update(app.config)
    celery_app.conf.beat_schedule={
        "fee-reminder-job":{
            'task': 'utils.email_otp.generate_fee_notifications',
            "schedule":crontab(day_of_month=5, hour=9, minute=0)
        },
    }
    celery_app.conf.timezone = 'Asia/Kolkata'
    return celery_app


    
