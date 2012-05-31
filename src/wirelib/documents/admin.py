# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import user_profile
from django.contrib import admin

class document_admin(admin.ModelAdmin):
    fields = ['bib_no', 'category', 'publisher']

class user_profile_admin(admin.ModelAdmin):
    fields = ['user', 'street', 'number', 'zipcode', 'city']

admin.site.register(document, document_admin)
admin.site.register(user_profile, user_profile_admin)
