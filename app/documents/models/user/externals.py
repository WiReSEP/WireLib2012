# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models


class NonUser(models.Model):
    first_name = models.CharField("vorname", max_length=30)
    last_name = models.CharField("nachname", max_length=30)
    email = models.EmailField("e-mail", max_length=50)
    street = models.CharField("straße", max_length=30)
    number = models.CharField("nummer", max_length=5)
    zipcode = models.CharField("postleitzahl", max_length=5)
    city = models.CharField("stadt", max_length=58)

    class Meta:
        app_label = 'documents'
        verbose_name = "Externer"
        verbose_name_plural = "Externe"

    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)


class TelNonUser(models.Model):

    non_user = models.ForeignKey(NonUser, verbose_name="externer")
    tel_type = models.CharField(
        "tel Typ ( Privat,Büro,Mobil ... )", max_length=20)
    tel_nr = models.CharField("tel Nr.", max_length=20)
    # TODO eigene Telefonnummerklasser

    class Meta:
        app_label = 'documents'
        unique_together = ('non_user', 'tel_nr')
        verbose_name = "Externer Tel. Nr."
        verbose_name_plural = "Externer Tel. Nr."
