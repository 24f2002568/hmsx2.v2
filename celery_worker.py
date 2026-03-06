"""
celery_worker.py
────────────────
Celery worker entrypoint.

Usage:
    # Start worker (processes tasks)
    celery -A celery_worker.celery worker --loglevel=info

    # Start beat scheduler (fires scheduled tasks)
    celery -A celery_worker.celery beat --loglevel=info

    # Start both together (dev only — not recommended for production)
    celery -A celery_worker.celery worker --beat --loglevel=info

    # Monitor tasks in terminal
    celery -A celery_worker.celery flower      # needs: pip install flower
"""

from backend import create_app, celery

app = create_app()

# Push app context so tasks can use db, mail, cache etc.
app.app_context().push()
