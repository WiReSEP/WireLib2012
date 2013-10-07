# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from .document import Document


class DocExtra(models.Model):
    """
    Bietet die Möglichkeit für mehrere extra Felder für ein Dokument
    """
    doc_id = models.ForeignKey(Document)
    bib_field = models.CharField(max_length=40)
    content = models.CharField(max_length=200)

    class Meta:
        unique_together = ('doc_id', 'bib_field')
    # primary_key(docId, bibField)

    def __unicode__(self):
        return unicode(self.content)

    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter
        aktualisiert werden kann
        """
        # TODO nach Datenbankerstellung testen, ob user None sein muss
        self.doc_id.save(user)
        super(DocExtra, self).save(*args, **kwargs)
