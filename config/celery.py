import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery = Celery('common-goods')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()