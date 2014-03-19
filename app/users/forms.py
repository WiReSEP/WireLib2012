from django import forms
from users import models
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm


class UserEditForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email',
                  'street', 'number', 'zipcode', 'city',
                  )


class UserChangeForm(AuthUserChangeForm):
    class Meta:
        model = models.User


class UserCreationForm(AuthUserCreationForm):
    class Meta:
        model = models.User

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])
