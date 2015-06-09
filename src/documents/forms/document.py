#vim: set fileencoding=utf-8
from django import forms
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from documents.models import Author
from documents.models import Document
from documents.models import DocumentAuthors
from documents.models import Publisher
from documents.models import Keywords
from documents.models import DocExtra


def _get_js_list(data_target, field):
    objects = "["
    for value in data_target.objects.values_list(field, flat=True):
        if not value:
            continue
        import json
        val = json.dumps(value)
        if objects == "[":
            objects += '%s' % val
        else:
            objects += ',%s' % val
    objects += "]"
    return objects


def _get_publisher_list():
    return _get_js_list(Publisher, 'name')


def _get_author_list():
    return _get_js_list(Author, 'full_name')


class AuthorSelectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuthorSelectForm, self).__init__(*args, **kwargs)
        self.fields['editor'].widget.attrs = {'class': 'onoffswitch-checkbox',
                                              'data-on-text': 'Editor',
                                              'data-off-text': 'Autor'}
        self.fields['sort_value'].widget = forms.HiddenInput()

    author = forms.CharField(widget=forms.TextInput(
        attrs={'data-provide': 'typeahead', 'autocomplete': 'off',
               'data-source': _get_author_list(), 'placeholder': 'Autor'}))

    def clean_author(self):
        author_name = self.cleaned_data['author']
        author, created = Author.objects.get_or_create(full_name=author_name)
        return author

    class Meta:
        model = DocumentAuthors
        fields = ['author', 'editor', 'sort_value']


class KeywordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(KeywordForm, self).__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs.update({'placeholder': 'Schlüsselwort'})

    class Meta:
        model = Keywords
        fields = ['keyword', ]


class ExtraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExtraForm, self).__init__(*args, **kwargs)
        self.fields['bib_field'].widget.attrs.update({'placeholder': 'Feldname'})
        self.fields['content'].widget.attrs.update({'placeholder': 'Feldinhalt'})

    class Meta:
        model = DocExtra
        fields = ['bib_field', 'content']


class CustomAuthorInlineFormSet(BaseInlineFormSet):
    def save(self, commit=True):
        for i, form in enumerate(self, 1):
            if form and form.cleaned_data:
                form.cleaned_data['sort_value'] = i
                form.sort_value = i
        return super(CustomAuthorInlineFormSet, self).save(commit)

AuthorInlineFormset = inlineformset_factory(Document, DocumentAuthors,
                                            form=AuthorSelectForm, 
                                            formset=CustomAuthorInlineFormSet)

KeywordInlineFormset = inlineformset_factory(Document, Keywords,
                                             form=KeywordForm)

ExtraInlineFormset = inlineformset_factory(Document, DocExtra, form=ExtraForm)


class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if not kwargs['initial']:
            kwargs['initial'] = {}
        kwargs['initial'].update({'currency': 'EUR', 'category': 'book'})
        super(DocumentForm, self).__init__(*args, **kwargs)

        for key, field in self.fields.items():
            field.widget.attrs.update({'placeholder': key})
        self.fields['title'].widget.attrs.update({'id': 'importTitle',
                                                  'size': '120'})
        self.fields['address'].widget.attrs.update({'id': 'importAddress',
                                                    'size': '80'})
        self.fields['bib_no'].widget.attrs.update({'id': 'importBibNo'})
        self.fields['inv_no'].widget.attrs.update({'id': 'importInvNo'})
        self.fields['isbn'].widget.attrs.update({'id': 'importISBN',
                                                 'placeholder': 'ISBN'})
        self.fields['year'].widget.attrs.update({'id': 'importYear'})
        self.fields['category'].widget.attrs.update({'id': 'importBibTeXCategory'})
        self.fields['bibtex_id'].widget.attrs.update({'id': 'importBibTeXID'})
        self.fields['price'].widget.attrs.update({'id': 'importPrice'})
        self.fields['currency'].widget.attrs.update({'id': 'importCurrency'})
        #self.fields['currency'].initial = 'EUR'
        self.fields['lib_of_con_nr'].widget.attrs.update({'id': 'importLOCN',
                                                          'placeholder': 'Library Of Congress No'})
        self.fields['comment'].widget.attrs.update({'id': 'importComment',
                                                    'cols': 80,
                                                    'placeholder': 'Kommentar'})
        self.author_form = AuthorInlineFormset(data=self.data or None,
                                               instance=self.instance or None,
                                               prefix='authors')
        self.keyword_form = KeywordInlineFormset(data=self.data or None,
                                                 instance=self.instance or None,
                                                 prefix='keywords')
        self.extra_form = ExtraInlineFormset(data=self.data or None,
                                             instance=self.instance or None,
                                             prefix='extras')

    publisher = forms.CharField(widget=forms.TextInput(
        attrs={'data-provide': 'typeahead', 'autocomplete': 'off',
               'data-source': _get_publisher_list(), 'id': 'importPublisher', 'size': '80'}))

    def clean_publisher(self):
        publisher_name = self.cleaned_data['publisher']
        publisher, created = Publisher.objects.get_or_create(name=publisher_name)
        return publisher

    def is_valid(self):
        valid = super(DocumentForm, self).is_valid()
        if not self.extra_form.is_valid():
            valid = False
        if not self.keyword_form.is_valid():
            valid = False
        if not self.author_form.is_valid():
            valid = False
        return valid

    def save(self, commit=True):
        self.extra_form.save()
        self.keyword_form.save()
        retval=super(DocumentForm, self).save(commit)
        self.author_form.save()
        return retval

    class Meta:
        model = Document
        fields = ['title', 'publisher', 'address', 'bib_no',
                  'inv_no', 'isbn', 'year', 'category', 'bibtex_id', 'price',
                  'currency', 'lib_of_con_nr', 'comment']

    class Media:
        css = {
            'all': ('css/bootstrap-switch.css',),
        }
        js = ('js/bootstrap-switch.js', 'js/dynamic-formset.js',
              'js/jquery-ui.js')
