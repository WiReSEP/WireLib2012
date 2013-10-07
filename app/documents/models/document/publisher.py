from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publisher"
