# vim: set fileencoding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from documents.models import author
from documents.models import category
from documents.models import document
from documents.models import document_authors
from documents.models import emails
from documents.models import keywords
from documents.models import need
from documents.models import need_groups
from documents.models import non_user
from documents.models import publisher
from documents.models import tel_non_user
from documents.models import tel_user
from documents.models import user_profile

"""
Definition der Adminseiten der Models.
Jede Klasse steht für ein Model, dass angezeigt werden soll
Alle 'inline' Klassen repräsentieren Models, die in anderen Seiten angezeigt
werden sollen.
'model' definiert von welchem Model alle Felder angzeigt werden. 'fields' zeigt
nur eine Auswahl an Attributen des Models an.
"""
#class keywords_admin(admin.ModelAdmin):
 #   fields = ['keyword','document']
 
 
 #TODO Massenfunktionen einfügen á la https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/
class keywords_inline(admin.StackedInline):
    model = keywords

class tel_user_inline(admin.StackedInline):
    model = tel_user
    fk_name = 'user'
    extra = 1

class need_inline(admin.StackedInline):
    model = need
    extra = 1

class need_groups_admin(admin.ModelAdmin):
    fields = ['name']
    inlines = [need_inline]

class category_admin(admin.ModelAdmin):
    fields = ['name', 'needs']

class publisher_admin(admin.ModelAdmin):
    fields = ['name']

class author_admin(admin.ModelAdmin):
    fields = ['first_name', 'last_name']

class document_authors_inline(admin.StackedInline):
    model = document_authors

class document_admin(admin.ModelAdmin):
    list_display = ('bib_no', 'inv_no', 'title', 
                    'publisher', 'ub_date', 'bib_date', 'last_updated', )
    #TODO Filter für Daten (Plural Datum) anpassen, sodass man nicht nach den 
    #entsprechenden Datum filtern kann und nicht mehr nur nach letzten Tag, Woche, Monat, Jahr
    list_filter = ('category', )
    ordering = ['bib_no'] 
    search_fields = ['bib_no', 'title', 'publisher__name' ,'isbn', 'inv_no', 'bibtex_id', ]
    fields = ['bib_no',  'inv_no', 'bibtex_id', 'lib_of_con_nr', 'title', 
              'isbn', 'category', 'last_updated', 'last_edit_by', 'publisher',
              'year', 'address', 'price', 'currency', 'date_of_purchase', 
              'ub_date', 'bib_date', 'comment']
    readonly_fields = ('last_edit_by', 'last_updated', 'date_of_purchase')
    inlines = [document_authors_inline, keywords_inline]
    
class tel_non_user_inline(admin.TabularInline):
    model = tel_non_user
    
class non_user_admin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email')
    inlines = [tel_non_user_inline,]

class user_profile_inline(admin.StackedInline):
    model = user_profile
    fk_name = 'user'
    max_num = 1

class CustomUserAdmin(UserAdmin):
    inlines = [user_profile_inline, tel_user_inline]
    
class emails_admin(admin.ModelAdmin):
    pass
    list_display = ('name', 'subject')
   # sollte man, nachdem alle Emails eingefügt worden, entkommentieren TODO
   # readonly_fields = ('name',) 
                                                        

#Registrierung aller anzuzeigenden Tabellen.
admin.site.register(publisher, publisher_admin)
admin.site.register(author, author_admin)
admin.site.register(category, category_admin)
admin.site.register(document, document_admin)
admin.site.register(need_groups, need_groups_admin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(non_user, non_user_admin)
admin.site.register(emails, emails_admin)
#admin.site.register(keywords, keywords_admin)
# TODO: evtl. wieder ein Statusfeld in document_admin einfügen
