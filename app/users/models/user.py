#vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractUser as AuthUser
from django.contrib.auth.models import UserManager


class PhoneNumbers(models.Model):
    phone_type = models.CharField('Typ', max_length=20)
    phone_number = models.CharField('Telefonnummer', max_length=20, unique=True)

    class Meta:
        app_label = 'users'
        verbose_name = 'Benutzer Tel.-Nummer'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return u'%s: %s' % (self.phone_type, self.phone_number)


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

    def __unicode__(self):
        name = self.get_full_name()
        if not name:
            name = self.username
        return u'%s' % name

    def get_absolute_url(self):
        return reverse('users.profile', kwargs={'username': self.username})
