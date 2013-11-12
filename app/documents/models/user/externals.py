# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from users.models import PhoneNumbers


class NonUser(models.Model):
    first_name = models.CharField("vorname", max_length=30)
    last_name = models.CharField("nachname", max_length=30)
    email = models.EmailField("e-mail", max_length=50)
    street = models.CharField("straße", max_length=30)
    number = models.CharField("nummer", max_length=5)
    zipcode = models.CharField("postleitzahl", max_length=5)
    city = models.CharField("stadt", max_length=58)
    phone_numbers = models.ManyToManyField(PhoneNumbers)

    class Meta:
        app_label = 'documents'
        verbose_name = "Externer"
        verbose_name_plural = "Externe"

    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)
