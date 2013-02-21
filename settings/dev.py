""" These are the development settings. Create a new settings.py in this folder 
and set your personal settings by your own needs.
"""

from settings.default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wire',             
# Or path to database file if using sqlite3.
        'USER': 'wire',                      
# Not used with sqlite3.
        'PASSWORD': 'wireweb',                  
# Not used with sqlite3.
        'HOST': 'localhost',
# Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      
# Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DOCUMENTS_SECDIR = normpath(join(DJANGO_ROOT, 'private'))
#DOCUMENTS_SECDIR = '/var/www/django/privat/'
DOCUMENTS_BIBTEX = 'bibtex/'
DOCUMENTS_ALLEGRO_FILES = 'allegro/'

BIBTEX_DEBUG = False
