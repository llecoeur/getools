import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getools.settings')

app = Celery('getools')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    #Scheduler Name
    'valid_conges_14_jours': {
        # Task Name (Name Specified in Decorator)
        'task': 'valid_conges_14_jours',  
        # Schedule      
        'schedule': 3600.0,
    },
    'rappel_11_jours': {
        # Task Name (Name Specified in Decorator)
        'task': 'rappel_11_jours',  
        # Schedule      
        'schedule': 3600.0,
    },
    'delete_demande_conge_brouillon': {
        # Task Name (Name Specified in Decorator)
        'task': 'delete_demande_conge_brouillon',  
        # Schedule      
        'schedule': 3600.0,
    },
}