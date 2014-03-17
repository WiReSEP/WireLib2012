from django import forms
from users import models
from django.contrib.auth.forms import UserChangeForm as AuthUserChangeForm
from users.models import User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email',
                  'street', 'number', 'zipcode', 'city',
                  )


class UserChangeForm(AuthUserChangeForm):
    class Meta:
        model = User
