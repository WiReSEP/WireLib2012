#!/bin/bash

USE_MYSQL=y
DJANGO_VERSION=1.3
ENGINE=
USERNAME=
PASSWORD=
DATABASE=
WORKING_PATH=${0%/*}


echo Welcome to the WireLib installation script
echo ==========================================
echo
echo
read -p "Do you wish to use MySQL as database?(Y/n):" USE_MYSQL
USE_MYSQL=${USE_MYSQL:-y}
if [ USE_MYSQL == 'y' ];then
  ENGINE=mysql
  echo "Using MySQL"
  while [[ -z USERNAME ]]; do
	read -p "Please enter the MySQL Username:" USERNAME
  done
  while [[ -z PASSWORD ]]; do
	read -p "Please enter the MySQL Username passwort:" PASSWORD
  done
  while [[ -z DATABASE ]]; do
	read -p "Please enter the MySQL Database:" DATABASE
  done
  read -p "Please enter the MySQL Host (default: localhost):" HOST
  HOST=${HOST-localhost}
  read -p "Please enter the MySQL Port (enter for default):" PORT
else
  ENGINE=sqlite3
  echo "Using sqlite3 instead"
  read -p "Please enter the path to the sqlite-file:" USERNAME
fi

mkdir -p ${WORKING_PATH}/private/allegro
mkdir -p ${WORKING_PATH}/private/bibtex

echo "from settings.default import *
DATABASES = {
    'default': {
	        'ENGINE': 'django.db.backends.${ENGINE}',
			# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
			# 'oracle'.
			        'NAME': '${NAME}'
					# Or path to database file if using sqlite3.
					#        'USER': '${USER}',
					# Not used with sqlite3.
					#        'PASSWORD': '${PASSWORD}',
					# Not used with sqlite3.
					#        'HOST': '${HOST}',
					# Set to empty string for localhost. Not used with sqlite3.
					#        'PORT': '${PORT}',
					# Set to empty string for default. Not used with sqlite3.
					    }
					  }

					  DEBUG = False

					  DOCUMENTS_SECDIR = normpath(join(DJANGO_ROOT, 'private'))
					  DOCUMENTS_SECDIR = '${WORKING_PATH}/private/'
					  DOCUMENTS_BIBTEX = 'bibtex/'
					  DOCUMENTS_ALLEGRO_FILES = 'allegro/'

					  BIBTEX_DEBUG = False
" >> ${WORKING_PATH}/settings/deploy.py
echo "from .default import *
from .deploy import *" >> ${WORKING_PATH}/settings/__init__.py

# Virtualenv
#

cd ${WORKING_PATH}
virtualenv -p python2 virtualenv
. virtualenv/bin/activate
pip install django==${DJANGO_VERSION}
pip install flup
