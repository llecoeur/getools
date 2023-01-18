celery --app=getools.celery:app purge -f
celery --app=getools.celery:app worker --loglevel=INFO -B
