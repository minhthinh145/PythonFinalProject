"""
Infrastructure Persistence App Configuration
"""
from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.persistence'
    verbose_name = 'Infrastructure Persistence'
