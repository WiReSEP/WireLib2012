from __future__ import unicode_literals

from django.db import models


class Author(models.Model):
    first_name = models.CharField("vorname", max_length=30, null=True)
    last_name = models.CharField("nachname", max_length=30)

    class Meta:
        unique_together = ('first_name', 'last_name')
    # primary ('name', 'surname')
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"

    def __unicode__(self):
        return (self.first_name + ' ' + self.last_name)
