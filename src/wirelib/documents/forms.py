from django import forms
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
from documents.models import EmailValidation, document, author
import mimetypes, urllib


class EmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verifikation, ob Email wirklich existiert
        """
        email = self.cleaned_data.get("email")
        if not (User.objects.filter(email=email) or EmailValidation.objects.filter(email=email)):
            return email

        raise forms.ValidationError(_("Die Email existiert schon."))
        
class UploadFileForm(forms.Form):
    file  = forms.FileField()

class DocForm(ModelForm):
    authors = forms.ModelMultipleChoiceField(
            queryset=author.objects.all().order_by('last_name'),
            label='Autoren')
    editors = forms.ModelMultipleChoiceField(
            queryset=author.objects.all().order_by('last_name'), 
            label='Editoren')
    class Meta:
        model = document
        exclude = ('date_of_purchase', 'ub_date', 'bib_date', 'last_edit_by')

class AuthorAddForm(ModelForm):
    class Meta:
        model = author

class SelectUser(forms.Form):
    users = forms.ModelChoiceField(queryset=User.objects.all(), label="Nutzer \
    auf den uebertragen werden soll", empty_label="")
