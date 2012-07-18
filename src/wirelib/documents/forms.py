from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
from documents.models import EmailValidation, document, author, non_user,\
    user_profile, tel_user, tel_non_user
import mimetypes, urllib

if not settings.AUTH_PROFILE_MODULE: 
    raise SiteProfileNotAvailable
try:
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    Profile = models.get_model(app_label, model_name)
except (ImportError, ImproperlyConfigured): 
    raise SiteProfileNotAvailable


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
        
class ProfileForm(ModelForm): 
    class Meta: 
        model = user_profile
        exclude = ('user_id')

class TelForm(ModelForm): 
    class Meta: 
        model = tel_user
        exclude = ('user_id')

class TelNonUserForm(ModelForm):
    class Meta:
        model = tel_non_user
        exclude = ('non_user')

class UploadFileForm(forms.Form):
    file  = forms.FileField()

class DocForm(ModelForm):
    authors = forms.ModelMultipleChoiceField(
            queryset=author.objects.all().order_by('last_name'),
            label='Autoren')
    editors = forms.ModelMultipleChoiceField(
            queryset=author.objects.all().order_by('last_name'), 
            label='Editoren',
            required=False)
    class Meta:
        model = document
        exclude = ('date_of_purchase', 'ub_date', 'bib_date', 'last_edit_by')

class AuthorAddForm(ModelForm):
    class Meta:
        model = author

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() + u' (' + obj.username + u')'

class SelectUser(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(SelectUser, self).__init__(*args, **kwargs)
        self.fields['users'].queryset = User.objects.all().exclude(id=user.id)
        
    users = UserModelChoiceField(queryset=User.objects.all(), label="", empty_label="")
   

class NonUserForm(ModelForm):
    class Meta:
        model = non_user
