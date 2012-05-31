# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import user_profile
from documents.models import tel_user
from documents.models import category
from django.contrib import admin
from documents.models import publisher
from documents.models import author

class tel_user_inline(admin.StackedInline):
    model = tel_user
    extra = 1

class category_admin(admin.ModelAdmin):
    fields = ['name']

class publisher_admin(admin.ModelAdmin):
    fields = ['name']

class author_admin(admin.ModelAdmin):
    fields = ['documents', 'first_name', 'last_name']

class document_admin(admin.ModelAdmin):
    fields = ['bib_no', 'inv_no', 'bibtex_id', 'lib_of_con_nr', 'title',
              'isbn', 'category', 'status', 'publisher',
              'address','year', 'price', 'currency', 'authors', 'comment']

class user_profile_admin(admin.ModelAdmin):
    fields = ['user', 'street', 'number', 'zipcode', 'city']
    inlines = [tel_user_inline]

admin.site.register(publisher, publisher_admin)
admin.site.register(author, author_admin)
admin.site.register(category, category_admin)
admin.site.register(document, document_admin)
admin.site.register(user_profile, user_profile_admin)
