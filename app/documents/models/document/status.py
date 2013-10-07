class DocStatus(models.Model):
        # auftraggebender User
    recent_user = models.ForeignKey(User, related_name='recent_user')
    doc_id = models.ForeignKey(Document)
        # in welchen Status wurde geändert?
    status = models.IntegerField(choices=Document.STATUS_CHOICES.items(),
                                 default=Document.AVAILABLE)
        # Datum an dem es geschah
    date = models.DateTimeField(auto_now_add=True)
        # False markiert den aktuellsten Eintrag für den Status eines
        # Dokumentes
    return_lend = models.BooleanField(default=False)
        # Ende der Rückgabefrist
    date_term_lend = models.DateTimeField(blank=True, null=True)
        # ausleihender User
    user_lend = models.ForeignKey(
        User, blank=True, null=True, related_name='user_lend')
        # ausleihender non_User
    non_user_lend = models.ForeignKey(NonUser, blank=True, null=True)

    class Meta:
        permissions = (("can_lend", "Can lend documents"),
                       ("can_unlend", "Can unlend documents"),
                       ("can_miss", "Can miss documents"),
                       ("can_order", "Can order documents"),
                       ("can_lost", "Can lost documents"),
                       ("can_see_history", "Can see documenthistory"),)
