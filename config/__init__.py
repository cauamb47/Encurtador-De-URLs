# Garante que o Celery seja carregado junto com o Django
from .celery import app as celery_app

__all__ = ("celery_app",)