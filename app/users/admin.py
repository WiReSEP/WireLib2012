# vim: set fileencoding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import ugettext_lazy as _
from users.models import User
from users.models import PhoneNumbers
from users.forms import UserChangeForm
from users.forms import UserCreationForm


class PhoneNumbersAdmin(admin.ModelAdmin):
    model = PhoneNumbers


class UserAdmin(AuthUserAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email',
                                         'street', 'number', 'zipcode', 'city',
                                         'phone_numbers')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(PhoneNumbers, PhoneNumbersAdmin)
