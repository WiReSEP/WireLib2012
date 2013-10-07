class Keywords(models.Model):
    document = models.ForeignKey(Document)
    keyword = models.CharField(u"Schlüsselwort", max_length=200)

    class Meta:
        unique_together = ('document', 'keyword')
    # primary_key(document, keyword)
        verbose_name = u"Schlüsselwort"
        verbose_name_plural = u"Schlüsselwörter"

    def __unicode__(self):
        return self.keyword

    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter
        aktualisiert werden kann
        """
        # TODO nach Datenbankerstellung testen, ob user None sein muss
        self.document.save(user)
        super(Keywords, self).save(*args, **kwargs)
