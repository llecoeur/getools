#/bin/bash

cd /opt/getools
source bin/activate
cd getools
git pull
python manage.py migrate
python manage collectstatic --noinput
sudo systemctl restart gunicorn.socket
