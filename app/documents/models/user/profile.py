class UserProfile(models.Model):
    """
    Zugriff auf unsere Daten auch von außerhalb durch get_profile() möglich
    """
    user = models.OneToOneField(User, primary_key=True)
    street = models.CharField("Straße", max_length=30)
    number = models.CharField("Nummer", max_length=5)
    zipcode = models.CharField("Postleitzahl", max_length=5)
    city = models.CharField("Stadt", max_length=58)

    class Meta:
        permissions = (("can_see_admin", "Can see the adminpanel"),
                       ("can_import", "Can import"),
                       ("can_export", "Can export"),
                       ("can_see_others_groups", "Can see groupmembership of all users"),)
        verbose_name = "Benutzer Profil"
        verbose_name_plural = "Benutzer Profile"

    def __unicode__(self):
        return unicode(self.user)

    class TelUser(models.Model):
    user = models.ForeignKey(User)
    tel_type = models.CharField("Typ", max_length=20)
    tel_nr = models.CharField("Telefonnummer", max_length=20)
    # TODO eigene Telefonnummerklasse

    class Meta:
        unique_together = ('user', 'tel_nr')
        verbose_name = "Benutzer Tel. Nr."
        verbose_name_plural = "Benutzer Tel. Nr."
