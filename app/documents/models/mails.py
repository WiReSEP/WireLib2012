class Emails(models.Model):
    name = models.CharField(max_length=30)
    subject = models.CharField("Betreff", max_length=50)
    text = models.TextField()

    class Meta:
        permissions = (("can_send_mails", "Can send Emails"),)
        verbose_name = "E-Mail"
        verbose_name_plural = "E-Mails"

    def __unicode__(self):
        return (self.name)
