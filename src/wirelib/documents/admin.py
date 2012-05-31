# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import user_profile
from django.contrib import admin

admin.site.register(document, user_profile)
