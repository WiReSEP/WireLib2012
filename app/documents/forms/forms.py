# vim: set fileencoding=utf-8
from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.forms.models import modelformset_factory
from documents.models import Author
from documents.models import DocExtra
from documents.models import Document
from documents.models import DocumentAuthors
from documents.models import NonUser
from documents.models import Publisher
from .search import SearchForm


FORM_LABEL = {'search': 'srch',
              'filter_authors': 'fa',
              'filter_documents': 'fd',
              'documents_on_page': 'dop',
              }


class SimpleSearch(SearchForm):
    """ This is the search form u.a. used in the documents overview of all documents. """
    TITLE_CHOICES = (('', 'Alle Titel'),
                     ('a-c', 'Titel mit A-C beginnend'),
                     ('d-f', 'Titel mit D-F beginnend'),
                     ('g-i', 'Titel mit G-I beginnend'),
                     ('j-l', 'Titel mit J-L beginnend'),
                     ('m-o', 'Titel mit M-O beginnend'),
                     ('p-r', 'Titel mit P-R beginnend'),
                     ('s-u', 'Titel mit S-U beginnend'),
                     ('v-z', 'Titel mit V-Z beginnend'),
                     ('^a-z', 'Titel mit Sonderzeichen'),
                     )
    AUTHOR_CHOICES = (('', 'Alle Authoren'),
                      ('a-c', 'Autoren mit A-C beginnend'),
                      ('d-f', 'Autoren mit D-F beginnend'),
                      ('g-i', 'Autoren mit G-I beginnend'),
                      ('j-l', 'Autoren mit J-L beginnend'),
                      ('m-o', 'Autoren mit M-O beginnend'),
                      ('p-r', 'Autoren mit P-R beginnend'),
                      ('s-u', 'Autoren mit S-U beginnend'),
                      ('v-z', 'Autoren mit V-Z beginnend'),
                      ('^a-z', 'Autoren mit Sonderzeichen'),
                      )
    PAGINATION_CHOICES = ((10, '10'),
                          (25, '25'),
                          (50, '50'),
                          (75, '75'),
                          (100, '100'),
                          )
    filter_title = forms.ChoiceField(choices=TITLE_CHOICES, required=False,
                                     label='')
    filter_authors = forms.ChoiceField(choices=AUTHOR_CHOICES, required=False,
                                       label='', )
    documents_on_page = forms.ChoiceField(choices=PAGINATION_CHOICES,
                                          required=False,
                                          label='Treffer pro Seite')
    filter_title.widget.attrs['onchange'] = 'this.form.submit()'
    filter_authors.widget.attrs['onchange'] = 'this.form.submit()'
    documents_on_page.widget.attrs['onchange'] = 'this.form.submit()'


class UploadFileForm(forms.Form):
    file = forms.FileField()


class DocumentAuthorForm(ModelForm):

    class Meta:
        model = DocumentAuthors

AuthorSelectForm = inlineformset_factory(Document, DocumentAuthors, extra=4,
                                         form=DocumentAuthorForm)

DocExtraForm = modelformset_factory(DocExtra, extra=4, can_delete=True,
                                    exclude=('doc_id',))


class DocForm(ModelForm):

    class Meta:
        model = Document
        fields = ('title', 'bib_no', 'inv_no', 'isbn', 'bibtex_id', 'category',
                  'publisher', 'year', 'address', 'price', 'currency', 'comment')
        exclude = ('date_of_purchase', 'ub_date', 'bib_date', 'last_edit_by',
                   'authors')


class AuthorAddForm(ModelForm):

    class Meta:
        model = Author


class PublisherAddForm(ModelForm):

    class Meta:
        model = Publisher


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.get_full_name() + u' (' + obj.username + u')'


class SelectUserForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(SelectUserForm, self).__init__(*args, **kwargs)
        self.fields['users'].queryset = get_user_model().objects.all().exclude(id=user.id)

    users = UserModelChoiceField(queryset=get_user_model().objects.all(),
                                 label="", empty_label="")


class NonUserForm(ModelForm):

    class Meta:
        model = NonUser
