#!/bin/bash

USE_MYSQL=y
DJANGO_VERSION=1.5
ENGINE=
USERNAME=
PASSWORD=
DATABASE=
WORKING_PATH=${0%/*}
SENDER_MAIL=


cd ${WORKING_PATH}
mkdir var
cd var
virtualenv -p python2 --system-site-packages virtualenv
. virtualenv/bin/activate
pip install django==${DJANGO_VERSION}
pip install flup
pip install gunicorn
django-admin.py startproject deploy
cd deploy
ln -s ../../app/documents documents
ln -s ../../app/users users

echo
echo
echo 'You need to edit the settings.py and the urls.py'
