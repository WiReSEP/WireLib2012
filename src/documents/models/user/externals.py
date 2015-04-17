# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
import inspect


class NonUser(models.Model):
    first_name = models.CharField("vorname", max_length=30)
    last_name = models.CharField("nachname", max_length=30)
    email = models.EmailField("e-mail", max_length=50, unique=True)
    street = models.CharField("straße", max_length=30, null=True, blank=True)
    number = models.CharField("nummer", max_length=5, null=True, blank=True)
    zipcode = models.CharField("postleitzahl", max_length=5,
                               null=True, blank=True)
    city = models.CharField("stadt", max_length=58, null=True, blank=True)
    phone_number = models.CharField("telefonnummer", max_length=60,
                                    null=True, blank=True)

    class Meta:
        app_label = 'documents'
        verbose_name = "Externer"
        verbose_name_plural = "Externe"

    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)

    @property
    def external(self):
        return True

    def get_absolute_url(self):
        return reverse('documents.external', args=(self.pk,))
