import os

from celery import Celery

# Diz ao Celery qual é o settings do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
# Lê as configurações que começam com CELERY_ no settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()