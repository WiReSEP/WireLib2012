""" These are the development settings. Create a new settings.py in this folder
and set your personal settings by your own needs.
"""

from settings.default import *

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3',
                # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'wirelib.db'
                # Or path to database file if using sqlite3.
                #'USER': '',
                # Not used with sqlite3.
                #'PASSWORD': '',
                # Not used with sqlite3.
                #'HOST': '',
                # Set to empty string for localhost. Not used with sqlite3.
                #'PORT': '',
                # Set to empty string for default. Not used with sqlite3.
                }
}

INSTALLED_APPS += ('django.contrib.webdesign', )

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'static_dev'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DOCUMENTS_SECDIR = normpath(join(DJANGO_ROOT, 'private'))
#DOCUMENTS_SECDIR = '/var/www/django/privat/'
DOCUMENTS_BIBTEX = 'bibtex/'
DOCUMENTS_ALLEGRO_FILES = 'allegro/'
DOCUMENTS_SENDER_MAIL = 'info@wirelib.sc.cs.tu-bs.de'

BIBTEX_DEBUG = False
