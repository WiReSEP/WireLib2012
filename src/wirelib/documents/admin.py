# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import user_profile
from django.contrib import admin
# from django.contrib.auth.models import User

# class user_admin(admin.ModelAdmin):
#    fields = ['username', 'password']

class document_admin(admin.ModelAdmin):
    fields = ['bib_no', 'inv_no', 'bibtex_id', 'lib_of_con_nr', 'title',
              'isbn', 'category', 'status', 'publisher',
              'address', 'price', 'currency','ub_date', 'comment']

class user_profile_admin(admin.ModelAdmin):
    fields = ['user', 'street', 'number', 'zipcode', 'city']

# admin.site.register(User,user_admin)
admin.site.register(document, document_admin)
admin.site.register(user_profile, user_profile_admin)
