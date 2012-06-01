# vim: set fileencoding=utf-8
from documents.models import document
from documents.models import user_profile
from documents.models import tel_user
from documents.models import category
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from documents.models import publisher
from documents.models import author

class tel_user_inline(admin.StackedInline):
    model = tel_user
    fk_name = 'user'
    extra = 1

class category_admin(admin.ModelAdmin):
    fields = ['name']

class publisher_admin(admin.ModelAdmin):
    fields = ['name']

class author_admin(admin.ModelAdmin):
    fields = ['first_name', 'last_name']

class document_admin(admin.ModelAdmin):
    fields = ['bib_no', 'inv_no', 'bibtex_id', 'lib_of_con_nr', 'title',
              'isbn', 'category', 'status', 'publisher',
              'address','year', 'price', 'currency', 'authors', 'comment']

class user_profile_inline(admin.StackedInline):
    model = user_profile
    fk_name = 'user'
    max_num = 1

class CustomUserAdmin(UserAdmin):
    inlines = [user_profile_inline, tel_user_inline]

admin.site.register(publisher, publisher_admin)
admin.site.register(author, author_admin)
admin.site.register(category, category_admin)
admin.site.register(document, document_admin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
