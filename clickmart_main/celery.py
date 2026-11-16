import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clickmart_main.settings')

app = Celery('clickmart_main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
