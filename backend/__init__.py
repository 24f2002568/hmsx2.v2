from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery
import os

db     = SQLAlchemy()
jwt    = JWTManager()
mail   = Mail()
cache  = Cache()
celery = Celery(__name__)


def create_app():
    app = Flask(__name__)

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'hms-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///hms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY']                 = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES']       = 86400

    app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT']           = 587
    app.config['MAIL_USE_TLS']        = True
    app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'hms@hospital.com')

    app.config['CELERY_BROKER_URL']    = REDIS_URL
    app.config['CELERY_RESULT_BACKEND'] = REDIS_URL
    app.config['broker_url']           = REDIS_URL
    app.config['result_backend']       = REDIS_URL

    app.config['GCHAT_WEBHOOK_URL'] = os.environ.get('GCHAT_WEBHOOK_URL', '')

    # Use Redis cache if available, otherwise fall back to simple memory cache
    try:
        import redis as _r
        _r.from_url(REDIS_URL).ping()
        app.config['CACHE_TYPE']            = 'RedisCache'
        app.config['CACHE_REDIS_URL']       = REDIS_URL
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    except Exception:
        app.config['CACHE_TYPE']            = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://localhost:5000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5000",
    ]}}, supports_credentials=True)

    _init_celery(app)

    from .routes.auth         import auth_bp
    from .routes.admin        import admin_bp
    from .routes.doctor       import doctor_bp
    from .routes.patient      import patient_bp
    from .routes.appointments import appointments_bp
    from .routes.departments  import departments_bp
    from .routes.jobs         import jobs_bp

    app.register_blueprint(auth_bp,         url_prefix='/api/auth')
    app.register_blueprint(admin_bp,        url_prefix='/api/admin')
    app.register_blueprint(doctor_bp,       url_prefix='/api/doctor')
    app.register_blueprint(patient_bp,      url_prefix='/api/patient')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(departments_bp,  url_prefix='/api/departments')
    app.register_blueprint(jobs_bp,         url_prefix='/api/jobs')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'MEDIX HMS API running'})

    return app


def _init_celery(app):
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=True,
        beat_schedule={
            'daily-reminders-8am': {
                'task': 'backend.tasks.task_send_daily_reminders',
                'schedule': _crontab(hour=8, minute=0),
            },
            'monthly-doctor-reports': {
                'task': 'backend.tasks.task_send_monthly_reports',
                'schedule': _crontab(day_of_month=1, hour=6, minute=0),
            },
        },
    )

    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def _crontab(**kwargs):
    from celery.schedules import crontab
    return crontab(**kwargs)