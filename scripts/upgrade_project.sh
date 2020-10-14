#/bin/bash

cd /opt/getools
source /bin/activate
cd getools
git pull
python manage.py migrate
sudo systemctl restart gunicorn.socket
