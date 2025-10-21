# celery.py (in your project root, next to settings.py)
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photobiz.settings')

app = Celery('photobiz')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'retry-failed-previews-hourly': {
        'task': 'photos.tasks.retry_failed_previews',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-cache-daily': {
        'task': 'photos.tasks.cleanup_old_cache',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}

# Optional: Task routing for better resource management
# app.conf.task_routes = {
#     'photos.tasks.generate_photo_preview': {'queue': 'images'},
#     'photos.tasks.generate_batch_zip': {'queue': 'heavy'},
#     'photos.tasks.process_batch_upload': {'queue': 'orchestration'},
# }

# Performance optimizations
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Retry policy
    task_acks_late=True,  # Only ack after task completes
    task_reject_on_worker_lost=True,  # Requeue if worker dies
    
    # Result backend settings (if using)
    result_expires=3600,  # Results expire after 1 hour
    # result_backend_transport_options={
    #     'master_name': 'mymaster',  # If using Redis Sentinel
    # },
    
    # Worker settings
    worker_prefetch_multiplier=1,  # For long-running tasks
    worker_max_tasks_per_child=50,  # Prevent memory leaks
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')



# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photobiz.settings')

# app = Celery('photobiz')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()