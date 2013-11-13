from django import forms
from users import models


class UserEditForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email',
                  'street', 'number', 'zipcode', 'city',
                  )
