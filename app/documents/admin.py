# vim: set fileencoding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from documents.models import Author
from documents.models import Category
from documents.models import Document
from documents.models import DocumentAuthors
from documents.models import Emails
from documents.models import Keywords
from documents.models import Need
from documents.models import NeedGroups
from documents.models import NonUser
from documents.models import Publisher
from documents.models import TelNonUser
from documents.models import TelUser
from documents.models import UserProfile

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
    model = Keywords

class tel_user_inline(admin.StackedInline):
    model = TelUser
    fk_name = 'user'
    extra = 1

class need_inline(admin.StackedInline):
    model = Need
    extra = 1

class need_groups_admin(admin.ModelAdmin):
    fields = ['name', 'needs']

class category_admin(admin.ModelAdmin):
    fields = ['name', 'needs']

class publisher_admin(admin.ModelAdmin):
    fields = ['name']

class author_admin(admin.ModelAdmin):
    fields = ['first_name', 'last_name']
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')

class document_authors_inline(admin.StackedInline):
    model = DocumentAuthors

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
    model = TelNonUser
    
class non_user_admin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email')
    inlines = [tel_non_user_inline,]

class user_profile_inline(admin.StackedInline):
    model = UserProfile
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
admin.site.register(Publisher, publisher_admin)
admin.site.register(Author, author_admin)
admin.site.register(Category, category_admin)
admin.site.register(Document, document_admin)
admin.site.register(NeedGroups, need_groups_admin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(NonUser, non_user_admin)
admin.site.register(Emails, emails_admin)
#admin.site.register(keywords, keywords_admin)
# TODO: evtl. wieder ein Statusfeld in document_admin einfügen
