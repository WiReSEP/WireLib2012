#vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser as AuthUser
from django.contrib.auth.models import UserManager


class PhoneNumbers(models.Model):
    phone_type = models.CharField('Typ', max_length=20)
    pnone_number = models.CharField('Telefonnummer', max_length=20, unique=True)

    class Meta:
        app_label = 'users'
        verbose_name = 'Benutzer Tel.-Nummer'
        verbose_name_plural = verbose_name


class User(AuthUser):
    street = models.CharField("Straße", max_length=30)
    number = models.CharField("Hausnummer", max_length=5)
    zipcode = models.CharField("Postleitzahl", max_length=10)
    city = models.CharField("Stadt", max_length=58)
    phone_numbers = models.ManyToManyField(PhoneNumbers)

    objects = UserManager()

    class Meta:
        app_label = 'users'
        permissions = (('can_see_admin', 'Can see the adminpanel'),)
