# vim: set fileencoding=utf-8
from django.contrib import admin
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
from documents.models import DocExtra

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
class KeywordsInline(admin.StackedInline):
    model = Keywords


class ExtrasInline(admin.StackedInline):
    model = DocExtra


class NeedInline(admin.StackedInline):
    model = Need
    extra = 1


class NeedGroupsAdmin(admin.ModelAdmin):
    fields = ['name', 'needs']


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'needs']


class PublisherAdmin(admin.ModelAdmin):
    fields = ['name']


class AuthorAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name']
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')


class DocumentAuthorsInline(admin.StackedInline):
    model = DocumentAuthors


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('bib_no', 'inv_no', 'title',
                    'publisher', 'ub_date', 'bib_date', 'last_updated',
                    'status',)
    #TODO Filter für Daten (Plural Datum) anpassen, sodass man nicht nach den
    #entsprechenden Datum filtern kann und nicht mehr nur nach letzten Tag, Woche, Monat, Jahr
    list_filter = ('category', 'status')
    ordering = ['status', 'bib_no']
    search_fields = ['bib_no', 'title', 'publisher__name', 'isbn', 'inv_no', 'bibtex_id', ]
    fields = ['bib_no',  'inv_no', 'bibtex_id', 'lib_of_con_nr', 'title',
              'status', 'isbn', 'category', 'last_updated', 'last_edit_by',
              'publisher', 'year', 'address', 'price', 'currency',
              'date_of_purchase', 'ub_date', 'bib_date', 'comment']
    readonly_fields = ('last_edit_by', 'last_updated', 'date_of_purchase')
    inlines = [DocumentAuthorsInline, KeywordsInline, ExtrasInline]


class NonUserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email')


class EmailsAdmin(admin.ModelAdmin):
    pass
    list_display = ('name', 'subject')
   # sollte man, nachdem alle Emails eingefügt worden, entkommentieren TODO
   # readonly_fields = ('name',)


#Registrierung aller anzuzeigenden Tabellen.
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(NeedGroups, NeedGroupsAdmin)
admin.site.register(NonUser, NonUserAdmin)
admin.site.register(Emails, EmailsAdmin)
#admin.site.register(keywords, keywords_admin)
# TODO: evtl. wieder ein Statusfeld in document_admin einfügen
