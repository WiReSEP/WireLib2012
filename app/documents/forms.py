# vim: set fileencoding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.forms.models import modelformset_factory
from documents.models import Author
from documents.models import DocExtra
from documents.models import Document
from documents.models import DocumentAuthors
from documents.models import NonUser
from documents.models import Publisher
from documents.models import TelNonUser


class NameForm(ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class TelNonUserForm(ModelForm):

    class Meta:
        model = TelNonUser
        exclude = ('non_user')


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


class SelectUser(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(SelectUser, self).__init__(*args, **kwargs)
        self.fields['users'].queryset = User.objects.all().exclude(id=user.id)

    users = UserModelChoiceField(
        queryset=User.objects.all(), label="", empty_label="")


class NonUserForm(ModelForm):

    class Meta:
        model = NonUser


class SearchForm(forms.Form):
    query = forms.CharField(label="")
    regex = forms.BooleanField(required=False)


class SearchProBaseForm(forms.Form):
    CHOICES = (("title", "Titel"),
               ("authors__last_name", "Autor Nachname"),
               ("authors__first_name", "Autor Vorname"),
               ("editor", "Editor"),
               ("keword", u"Schlüsselwort"),
               ("year", "Jahr"),
               ("publisher", "Herausgeber"),
               ("bib_no", "Bibliotheks-Nummer"),
               ("isbn", "ISBN"),
               ("status", "Buchstatus"),
               )
    STATI = ((Document.AVAILABLE, "Vorhanden"),
             (Document.LEND, "Ausgeliehen"),
             (Document.ORDERED, "Bestellt"),
             (Document.MISSING, "Vermisst"),
             (Document.LOST, "Verloren"),
             )
    searchtext = forms.CharField(label="Suchtext", required=False)
    regex = forms.BooleanField(required=False,
                               label=u'<a href="http://perldoc.perl.org/perlrequick.html">Regex</a>')
    category = forms.ChoiceField(choices=CHOICES, required=False)

    class Media:
        js = ('js/dynamic-formset.js', 'js/jquery-1.9.1.min.js')


class SearchProForm(SearchProBaseForm):
    LOGIC_CHOICES = (
        ('and', 'und'),
        ('and not', 'und nicht'),
        ('or', 'oder'),)
    bind = forms.ChoiceField(choices=LOGIC_CHOICES, label=u"Verknüpfung")

SearchProExtendedForm = formset_factory(SearchProForm)
