class Need(models.Model):
    name = models.CharField(max_length=30, primary_key=True)

    class Meta:
        verbose_name = "Mussfeld"
        verbose_name_plural = "Mussfelder"

    def __unicode__(self):
        return self.name


class NeedGroups(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    needs = models.ManyToManyField(Need, verbose_name="Mussfelder")

    class Meta:
        verbose_name = "Mussfeldgruppe"
        verbose_name_plural = "Mussfeldgruppen"

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    needs = models.ManyToManyField(NeedGroups, verbose_name="Mussfelder")

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __unicode__(self):
        return self.name
