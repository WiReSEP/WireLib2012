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

class DocumentAuthors(models.Model):
    document = models.ForeignKey(Document)
    author = models.ForeignKey(Author, verbose_name="Autor")
    editor = models.BooleanField(default=False)
    sort_value = models.IntegerField("Reihenfolge")
    _sort_field_name = "sort_value"

    class Meta:
        verbose_name = "Dokument Autoren"
        verbose_name_plural = "Dokument Autoren"
        unique_together = ('document', 'author')

    def __unicode__(self):
        return u'%s/%s' % (self.document, self.author)
