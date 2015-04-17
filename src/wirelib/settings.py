# coding=utf-8

""" Einstellungen von Wirelib.

Diese Datei wurde durch Django 1.5 erzeugt und unter Django 1.6 getested.
"""

from __future__ import unicode_literals
from __future__ import print_function

from django.conf import global_settings
try:
    import configparser
except:  # PY2 Fallback
    import ConfigParser as configparser
import os


def abs_join(*args):
    """ Join path arguments and build absolute path. """
    return os.path.abspath(os.path.join(*args))


def allowed_hosts_config():
    try:
        allowed_hosts = config.get('global', 'allowed_hosts', 'localhost')
        allowed_hosts = map(string.strip, allowed_hosts.split(','))
    except:
        allowed_hosts = ['localhost', ]
    return allowed_hosts


def debug_config():
    try:
        debug = config.get('global', 'debug', 'false')
    except:
        debug = 'false'
    return debug.lower() == 'true'


def database_config():
    """ Read configuration from cfg file. """
    cfg = None
    # Configuration errors are handled by django, because of this every not
    # given option will be set to the empty string.
    if config.get('database', 'type', '') == 'sqlite3':
        db_path = config.get('database', 'name', '')
        db_path = os.path.abspath(db_path)
        cfg = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    elif config.get('database', 'type', '') == 'mysql':
        cfg = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config.get('database', 'name', ''),
            'USER': config.get('database', 'user', ''),
            'PASSWORD': config.get('database', 'password', ''),
            'HOST': config.get('database', 'host', ''),
            'PORT': config.get('database', 'port', ''),
        }
    else:
        print('Datenbank konfiguration konnte nicht geladen werden.')
    return cfg


def get_or_create_secret_key():
    """ Get configured secret key for django. """
    try:
        secret_key = config.get('global', 'secret_key')
    except (KeyError,
            configparser.NoSectionError,
            configparser.NoOptionError):
        from django.utils.crypto import get_random_string
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!(){}/\-_+*'

        if not config.has_section('global'):
            config.add_section('global')
        config.set('global', 'secret_key', get_random_string(50, chars))

        secret_key = config.get('global', 'secret_key')
        write_config('Secret key geschrieben')
    return secret_key


def write_config(msg):
    """ Schreibt die Konfigurationsdatei gemäß der Einstellung CONFIG_FILE. """
    with open(CONFIG_FILE, 'w') as config_fp:
        config.write(config_fp)
        print(msg)


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = abs_join(PROJECT_DIR, '..', 'etc', 'wirelib.cfg')


config = configparser.SafeConfigParser()
if not config.read(CONFIG_FILE):
    write_config('Configurationsdatei erzeugt')

DEBUG = debug_config()
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': database_config(),
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = allowed_hosts_config()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    abs_join(PROJECT_DIR, '..', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = get_or_create_secret_key()

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wirelib.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wirelib.apache.wsgi.application'

TEMPLATE_DIRS = (
    abs_join(PROJECT_DIR, '..', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'documents',
    'users',
    'django.contrib.admin',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        "documents.context_processors.wire",
        "users.context_processors.user_context",
)

# Export settings
DOCUMENTS_ALLEGRO_FILES = 'allegro'
DOCUMENTS_BIBTEX = 'bibtex'

# If the setting DOCUMENTS_SECDIR is changed, the function
# `documents.views.export._get_sec_link` needs to be changed, too.
# To ensure the exports are running as expected this settings should always set
# to an absolute path pointing to the export directory.
# The BibTeX and Allegro exports are done in a subfolder of this setting based
# on the name stored in the settings above.
DOCUMENTS_SECDIR = abs_join(PROJECT_DIR, '..', 'static', 'exports')

# Generiere Export Ordner, wenn nicht bereits vorhanden
try:
    os.mkdir(DOCUMENTS_SECDIR)
    os.mkdir(os.path.join(DOCUMENTS_SECDIR, DOCUMENTS_ALLEGRO_FILES))
    os.mkdir(os.path.join(DOCUMENTS_SECDIR, DOCUMENTS_BIBTEX))
except:
    pass

# User model überschreiben
AUTH_USER_MODEL = 'users.User'

# misc
BIBTEX_DEBUG = False
DOCUMENTS_SENDER_MAIL = '${SENDER_MAIL}'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'
LOGOUT_URL = '/users/logout/'
