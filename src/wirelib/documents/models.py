# vim: set fileencoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models.signals import post_save
from exceptions import LendingError
from django.template import loader, Context 
from django.conf import settings
"""
class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb,self).__init__(*args, **kwargs)
        self.creates_table = False
"""

class category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
        #article
        #book
        #booklet
        #conference
        #''inbook (Teilstück von book)
        #''incollection (Teilstück von book)
        #''inproceedings (Teilstück von proceedings)
        #manual
        #mastersthesis
        #''misc ("beliebiger Eintrag": also wohl nicht in der DB)
        #phdthesis
        #proceedings
        #techreport
        #unpublished
    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __unicode__(self):
        return self.name

class category_need(models.Model):
    category = models.ForeignKey(category)
    need = models.CharField(max_length=30)

    def __unicode__(self):
        return self.category + u":" + self.need
    
class publisher(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    
    def __unicode__(self):
        return self.name


class author(models.Model):
    first_name = models.CharField("vorname",max_length=30, null=True)
    last_name = models.CharField("nachname",max_length=30)
    class Meta:
        unique_together = ('first_name', 'last_name')
    #primary ('name', 'surname')
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"
    
    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)

class document(models.Model):
    bib_no = models.CharField("Bibliotheksnummer", max_length=15, primary_key=True)
    inv_no = models.CharField("Inventar-Nummer", max_length=15, unique=True)
    bibtex_id = models.CharField("Bibtex-ID", max_length=120, unique=True)
    lib_of_con_nr = models.CharField("Library Of Congress No", max_length=20, blank=True, null=True) 
        #LibraryOfCongressN
    title = models.CharField("Titel",max_length=200)
    isbn = models.CharField("ISBN",max_length=17, blank=True, null=True)
    category = models.ForeignKey(category,verbose_name="Kategorie")
    last_updated = models.DateField("Letztes Update",auto_now=True)
    last_edit_by = models.ForeignKey(User,verbose_name="Zuletzt geändert von")
    publisher = models.ForeignKey(publisher, blank=True, null=True)
    year = models.IntegerField("Jahr",blank=True, null=True)
    address = models.CharField("Adresse",max_length=100, blank=True, null=True)
    price = models.DecimalField("Preis",max_digits=6, decimal_places=2, blank=True, null=True)
    currency = models.CharField("Währung",max_length=3, blank=True, null=True)
    date_of_purchase = models.DateField("Kaufdatum",auto_now_add=True)
    ub_date = models.DateField(blank=True, null=True) 
        #Datum des Allegro-Exports
    bib_date = models.DateField(blank=True, null=True) 
        #Datum des BibTeX-Exports
    comment = models.TextField("Kommentar",blank=True, null=True)
    authors = models.ManyToManyField(author,
            through='document_authors',verbose_name="Autoren")
    class Meta:
        permissions = (("can_see_price", "Can see price"),
                       ("can_see_locn", "Can see library of congress number"),
                       ("can_see_last_update_info", "Can see last update info"),
                       ("can_see_dop", "Can see date of purchase"),
                       ("can_see_export", "Can see dates of export"),)
        ordering = ['title']
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"
    
        

    AVAILABLE= 0  #vorhanden
    LEND = 1       #ausgeliehen
    ORDERED = 2    #bestellt
    MISSING = 3       #vermisst
    LOST = 4       #verloren
    
    def save(self, user=None, *args, **kwargs):
        """
        Methode zum Speichern des letzten Bearbeiters des Dokumentes
        """
        if user == None:
            user = User.objects.get(id=1)
        self.last_edit_by=user
        super(document, self).save(*args, **kwargs)
    
    def __status(self):
        """ 
        Ausgeben des aktuellen Status'
        """
        try:
            retVal = self.doc_status_set.latest('date').status
        except:
            retVal = 0
        return retVal
        
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.status = self.__status()

    def __unicode__(self):
        return self.title
    
    def set_status(self, 
                     editor, 
                     stat, 
                     terminate=None, 
                     user=None, 
                     non_user=None):
        """ 
        Methode zum Ändern des Status'
        Paramenter:
            editor - recent_user
            stat - status
            terminate - date_term_lend
            user - user_lend
            non_user - non_user_lend
        """
        try: # Wenn es was zum updaten gibt:
            old = self.doc_status_set.latest('date')
            # bei F5-Benutzung eines Buttons wurden zwei Einträge eingefügt und 
            # beide waren so gekennzeichnet, dass es keinen Nachfolgeeintrag gäbe
            if (old.status == stat \
                and old.recent_user == editor \
                and old.user_lend == user \
                and old.non_user_lend == non_user):
                pass
            else:
                old.return_lend=True
                old.save()
                l = doc_status(
                        recent_user = editor,
                        doc_id = self,
                        status = stat,
                        date_term_lend = terminate,
                        user_lend = user,
                        non_user_lend = non_user
                    )
                l.save()
        except:
            l = doc_status(
                        recent_user = editor,
                        doc_id = self,
                        status = stat,
                        date_term_lend = terminate,
                        user_lend = user,
                        non_user_lend = non_user
                    )
            l.save()

    def lend(self, user, editor=None, non_user=None, terminate=None):
        """ 
        Methode zum Ausleihen, Übertragen und beim Wiederfinden
        Parameter:
            user - user_lend (evtl recent_user)
            editor - recent_user
            non_user - non_user_lend
            terminate - date_term_lend
        """
        # fürs Übertragen
        if self.status == document.LEND:
            dstat = self.doc_status_set.latest('date')
            if dstat.user_lend == user and dstat.non_user_lend == non_user:
                return
        # zum Ausleihen oder Wiederfinden
        elif self.status == document.ORDERED:
            raise LendingError()
        if editor == None:
            editor = user
        self.set_status(editor, document.LEND, terminate, user, non_user)

    def unlend(self, user):
        """ 
        Methode zum zurückgeben 
        """
        self.set_status(user, document.AVAILABLE)

    def lost(self, user):
        """ 
        Methode zum "Verloren" setzen
        """
        self.set_status(user, document.LOST)
        
    def missing(self, user):
        """ 
        Methode für Vermisstmeldungen
        """
        self.set_status(user, document.MISSING)

    def get_editors(self):
        """
        Methode um alle Editoren anzuzeigen
        """
        auths = self.authors.filter(document_authors__editor=True)
        return auths

    def get_authors(self):
        """
        Methode um alle Autoren anzuzeigen
        """
        auths = self.authors.filter(document_authors__editor=False)
        return auths
    def add_author(self, author):
        """
        Methode um dem Dokument einen Autoren zuzuweisen
        """
        d = document_authors(document=self, author=author, editor=False)
        d.save()

    def add_editor(self, editor):
        """
        Methode um dem Dokument einen Autoren als Editor zuzuweisen
        """
        d = document_authors(document=self, author=editor, editor=True)
        d.save()

class document_authors(models.Model):
    document = models.ForeignKey(document)
    author = models.ForeignKey(author,verbose_name="autor")
    editor = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Dokument Autoren"
        verbose_name_plural = "Dokument Autoren"
        unique_together = ('document', 'author')

class keywords(models.Model):
    document = models.ForeignKey(document)
    keyword = models.CharField("Schlüsselwort",max_length=50)
    class Meta:
        unique_together = ('document', 'keyword')
    #primary_key(document, keyword)
        verbose_name = "Schlüsselwort"
        verbose_name_plural = "Schlüsselwörter"
        
    
    def __unicode__(self):
        return self.keyword
        
    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter 
        aktualisiert werden kann
        """
        #TODO nach Datenbankerstellung testen, ob user None sein muss
        self.document.save(user)
        super(keywords, self).save(*args, **kwargs)   

class doc_extra(models.Model):
    """
    Bietet die Möglichkeit für mehrere extra Felder für ein Dokument
    """
    doc_id = models.ForeignKey(document)
    bib_field = models.CharField(max_length=40)
    content = models.CharField(max_length=200)
    class Meta:
        unique_together = ('doc_id', 'bib_field')
    #primary_key(docId, bibField)
    
    def __unicode__(self):
        return unicode(self.content) 

    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter 
        aktualisiert werden kann
        """
        #TODO nach Datenbankerstellung testen, ob user None sein muss
        self.doc_id.save(user)
        super(doc_extra, self).save(*args, **kwargs)

class user_profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    street = models.CharField("Straße",max_length=30)
    number = models.CharField("Nummer",max_length=5)
    zipcode = models.CharField("Postleitzahl",max_length=5)
    city = models.CharField("Stadt",max_length=58)
    class Meta:
        permissions = (("can_see_admin", "Can see the adminpanel"),
                       ("can_import", "Can import"),
                       ("can_export", "Can export"),
                       ("can_see_others_groups", "Can see groupmembership of all users"),)
        verbose_name = "Benutzer Profil"
        verbose_name_plural = "Benutzer Profile"

    def __unicode__(self):
        return unicode(self.user)

    """
    Zugriff auf unsere Daten auch von außerhalb durch get_profile() möglich
    """
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile.objects.get_or_create(user=instance)
 
post_save.connect(create_user_profile, sender=User)

class tel_user(models.Model):
    user = models.ForeignKey(User)
    tel_type = models.CharField("Typ", max_length=20)
    tel_nr = models.CharField("Telefonnummer", max_length=20)
    # TODO eigene Telefonnummerklasse
    class Meta:
        unique_together = ('user', 'tel_nr')
        verbose_name = "Benutzer Tel. Nr."
        verbose_name_plural = "Benutzer Tel. Nr."

class non_user(models.Model):
    first_name = models.CharField("vorname",max_length=30)
    last_name = models.CharField("nachname",max_length=30)
    email = models.EmailField("e-mail",max_length=50)
    street = models.CharField("straße",max_length=30)
    number = models.CharField("nummer",max_length=5)
    zipcode = models.CharField("postleitzahl",max_length=5)
    city = models.CharField("stadt",max_length=58)

    class Meta:
        verbose_name = "Externer"
        verbose_name_plural = "Externe"
    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)

class tel_non_user(models.Model):

    non_user = models.ForeignKey(non_user, verbose_name="externer")
    tel_nr = models.CharField("tel Nr.",max_length=20)
    tel_type = models.CharField("tel Typ ( Privat,Büro,Mobil ... )",max_length=20)
    # TODO eigene Telefonnummerklasser
    class Meta:
        unique_together = ('non_user', 'tel_nr')
        verbose_name = "Externer Tel. Nr."
        verbose_name_plural = "Externer Tel. Nr."

class doc_status(models.Model):
    recent_user = models.ForeignKey(User, related_name='recent_user') 
        #auftraggebender User
    doc_id = models.ForeignKey(document) 
    status = models.IntegerField() 
        #in welchen Status wurde geändert?
    date = models.DateTimeField(auto_now_add=True) 
        #Datum an dem es geschah
    return_lend = models.BooleanField(default=False)
        # Aktueller Eintrag vorhanden
    date_term_lend = models.DateTimeField(blank=True, null=True) 
        #Ende der Rückgabefrist
    user_lend = models.ForeignKey(User, blank=True, null=True, related_name='user_lend') 
        #ausleihender User
    non_user_lend = models.ForeignKey(non_user, blank=True, null=True) 
        #ausleihender non_User
    class Meta:
        permissions = (("c_nlend", "Can lend documents"),
                       ("can_unlend", "Can unlend documents"),
                       ("can_miss", "Can miss documents"),
                       ("can_order", "Can order documents"),
                       ("can_lost", "Can lost documents"),
                       ("can_see_history", "Can see documenthistory"),)

class EmailValidationManager(models.Manager):
    """
    Email Validation Manager
    """
    def verify(self, key):
    #Methode zum Abgleichen der Keys 
    
        try:
            verify = self.get(key=key)
            if not verify.is_expired():
                verify.user.email = verify.email
                verify.user.save()
                verify.delete()
                return True
            else:
                verify.delete()
                return False
        except:
            return False

    def getuser(self, key):
    #Methode zum Anzeigen der user
        try:
            return self.get(key=key).user
        except:
            return False

    def add(self, user, email):
        """
        Methode zum Einfügen neuer Validerungsprozesse
        """
        while True:
            #Generierung eines zufälligen Passwortschlüssels
            key = User.objects.make_random_password(70)
            try:
                EmailValidation.objects.get(key=key)
            except EmailValidation.DoesNotExist:
                self.key = key
                break

        #Einbindung des Mailformulares für die E-Mail Verifizierung
        template_body = "email/validation.txt"
        #Einbindung des Betreffs 
        template_subject = "email/validation_subject.txt"
        site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
        body = loader.get_template(template_body).render(Context(locals()))
        subject = loader.get_template(template_subject).render(Context(locals())).strip()
        #Eigentliches Versenden der Mail
        send_mail(subject=subject, message=body, from_email=None, recipient_list=[email])
        user = User.objects.get(username=str(user))
        self.filter(user=user).delete()
        return self.create(user=user, key=key, email=email)


class EmailValidation(models.Model):

    user = models.ForeignKey(User, unique=True)
    email = models.EmailField(blank=True)
    key = models.CharField(max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = EmailValidationManager()
    
    def __unicode__(self): 
        return _("Emailverifikationsprozess für %(user)s") % { 'user': self.user }
    
    def is_expired(self):
        return (datetime.datetime.today() - self.created).days > 0

    def resend(self):
        """
        Senden der Verifierungsmail
        """
        template_body = "email/validation.txt"  
        template_subject = "email/validation_subject.txt"
        site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
        key = self.key
        body = loader.get_template(template_body).render(Context(locals()))
        subject = loader.get_template(template_subject).render(Context(locals())).strip()
        send_mail(subject=subject, message=body, fromcategories_email=None, recipient_list=[self.email])
        self.created = datetime.datetime.now()
        self.save()
        return True
        

class emails(models.Model):
    name = models.CharField(max_length=30)
    subject = models.CharField("Betreff", max_length=50)
    text = models.TextField()
    class Meta:
        permissions = (("can_send_mails", "Can send Emails"),)
        verbose_name = "E-Mail"
        verbose_name_plural = "E-Mails"
