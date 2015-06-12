from __future__ import unicode_literals

from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'documents'
        verbose_name = "Verlag"
        verbose_name_plural = "Verlage"
