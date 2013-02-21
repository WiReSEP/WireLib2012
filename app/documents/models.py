# vim: set fileencoding=utf-8
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.template import Context
from django.template import loader
from documents.lib.exceptions import LendingError


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
        
class Publisher(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publisher"


class Author(models.Model):
    first_name = models.CharField("vorname",max_length=30, null=True)
    last_name = models.CharField("nachname",max_length=30)
    class Meta:
        unique_together = ('first_name', 'last_name')
    #primary ('name', 'surname')
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"
    
    def __unicode__(self):
        return (self.first_name + ' ' + self.last_name)

class Document(models.Model):
    bib_no = models.CharField("Bibliotheks-Nr.", max_length=15, primary_key=True)
    inv_no = models.CharField("Inventar-Nr.", max_length=15, unique=True)
    bibtex_id = models.CharField("Bibtex-ID", max_length=120, unique=True)
    lib_of_con_nr = models.CharField("Library Of Congress No", max_length=60, blank=True, null=True) 
        #LibraryOfCongressN
    title = models.CharField("Titel",max_length=400)
    isbn = models.CharField("ISBN",max_length=17, blank=True, null=True)
    category = models.ForeignKey(Category,verbose_name="Kategorie")
    last_updated = models.DateField("Zuletzt geupdated", auto_now=True)
    last_edit_by = models.ForeignKey(User,verbose_name="Zuletzt geändert von")
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    year = models.IntegerField("Jahr",blank=True, null=True)
    address = models.CharField("Adresse",max_length=100, blank=True, null=True)
    price = models.DecimalField("Preis",max_digits=6, decimal_places=2, blank=True, null=True)
    currency = models.CharField("Währung",max_length=3, blank=True, null=True)
    date_of_purchase = models.DateField("Kaufdatum", auto_now_add=True)
    ub_date = models.DateField("UB-Export", blank=True, null=True) 
        #Datum des Allegro-Exports
    bib_date = models.DateField("BibTeX-Export", blank=True, null=True) 
        #Datum des BibTeX-Exports
    comment = models.TextField("Kommentar",blank=True, null=True)
    authors = models.ManyToManyField(Author,
            through='DocumentAuthors',verbose_name="Autoren")
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
    LEND = 1      #ausgeliehen
    ORDERED = 2   #bestellt
    MISSING = 3   #vermisst
    LOST = 4      #verloren
    
    def save(self, user=None, *args, **kwargs):
        """
        Methode zum Speichern des letzten Bearbeiters des Dokumentes
        """
        if user == None:
            user = User.objects.get(id=1)
        self.last_edit_by = user
        super(Document, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Methode zum Löschen nun überflüssiger Schriftsteller
        """
        for aut in (self.get_authors() or self.get_editors()):
            if len(aut.document_set.all())==1:
                aut.delete()
        if len(self.publisher.document_set.all())==1:
            self.publisher.delete()
        super(Document, self).delete(*args, **kwargs)
    
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
                l = DocStatus(
                        recent_user = editor,
                        doc_id = self,
                        status = stat,
                        date_term_lend = terminate,
                        user_lend = user,
                        non_user_lend = non_user
                    )
                l.save()
        except:
            l = DocStatus(
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
        if self.status == Document.LEND:
            dstat = self.doc_status_set.latest('date')
            if dstat.user_lend == user and dstat.non_user_lend == non_user:
                return
        # zum Ausleihen oder Wiederfinden
        elif self.status == Document.ORDERED:
            raise LendingError()
        if editor == None:
            editor = user
        self.set_status(editor, Document.LEND, terminate, user, non_user)

    def unlend(self, user):
        """ 
        Methode zum zurückgeben 
        """
        self.set_status(user, Document.AVAILABLE)

    def lost(self, user):
        """ 
        Methode zum "Verloren" setzen
        """
        self.set_status(user, Document.LOST)
        
    def missing(self, user):
        """ 
        Methode für Vermisstmeldungen
        """
        self.set_status(user, Document.MISSING)

    def _order_authors(self, auths):
        return auths.order_by("documentauthors__sort_value")

    def get_editors(self):
        """
        Methode um alle Editoren anzuzeigen
        """
        auths = self.authors.exclude(documentauthors__editor=False)
        return self._order_authors(auths)

    def get_authors(self):
        """
        Methode um alle Autoren anzuzeigen
        """
        auths = self.authors.exclude(documentauthors__editor=True)
        return self._order_authors(auths)

    def add_author(self, author):
        """
        Methode um dem Dokument einen Autoren zuzuweisen
        """
        self._add_author_or_editor(author, False)

    def add_editor(self, editor):
        """
        Methode um dem Dokument einen Autoren als Editor zuzuweisen
        """
        self._add_author_or_editor(editor, True)

    def _add_author_or_editor(self, obj, is_editor):
        from django.db.models import Max
        params = dict()
        connections = DocumentAuthors.objects.filter(document=self,editor=is_editor)
        max_val = connections.aggregate(Max('sort_value'))["sort_value__max"]
        if max_val is None:
            max_val = 0
        else :
            max_val = max_val + 1
        params["sort_value"] = max_val + 1
        d, dummy = DocumentAuthors.objects.get_or_create(document=self,
                author=obj, editor=is_editor, sort_value=max_val)
        d.save()

class DocumentAuthors(models.Model):
    document = models.ForeignKey(Document)
    author = models.ForeignKey(Author,verbose_name="Autor")
    editor = models.BooleanField(default=False)
    sort_value = models.IntegerField("Reihenfolge")
    _sort_field_name = "sort_value"
    class Meta:
        verbose_name = "Dokument Autoren"
        verbose_name_plural = "Dokument Autoren"
        unique_together = ('document', 'author')

    def __unicode__(self):
        return unicode({"Dokument": self.document, "Autor":self.author, "Editor": self.editor,
                "Position": self.sort_value})

class Keywords(models.Model):
    document = models.ForeignKey(Document)
    keyword = models.CharField("Schlüsselwort",max_length=200)
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
        super(Keywords, self).save(*args, **kwargs)   

class DocExtra(models.Model):
    """
    Bietet die Möglichkeit für mehrere extra Felder für ein Dokument
    """
    doc_id = models.ForeignKey(Document)
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
        super(DocExtra, self).save(*args, **kwargs)

class UserProfile(models.Model):
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
        UserProfile.objects.get_or_create(user=instance)
 
post_save.connect(create_user_profile, sender=User)

class TelUser(models.Model):
    user = models.ForeignKey(User)
    tel_type = models.CharField("Typ", max_length=20)
    tel_nr = models.CharField("Telefonnummer", max_length=20)
    # TODO eigene Telefonnummerklasse
    class Meta:
        unique_together = ('user', 'tel_nr')
        verbose_name = "Benutzer Tel. Nr."
        verbose_name_plural = "Benutzer Tel. Nr."

class NonUser(models.Model):
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

class TelNonUser(models.Model):

    non_user = models.ForeignKey(NonUser, verbose_name="externer")
    tel_type = models.CharField("tel Typ ( Privat,Büro,Mobil ... )",max_length=20)
    tel_nr = models.CharField("tel Nr.",max_length=20)
    # TODO eigene Telefonnummerklasser
    class Meta:
        unique_together = ('non_user', 'tel_nr')
        verbose_name = "Externer Tel. Nr."
        verbose_name_plural = "Externer Tel. Nr."

class DocStatus(models.Model):
    recent_user = models.ForeignKey(User, related_name='recent_user') 
        #auftraggebender User
    doc_id = models.ForeignKey(Document) 
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
    non_user_lend = models.ForeignKey(NonUser, blank=True, null=True) 
        #ausleihender non_User
    class Meta:
        permissions = (("can_lend", "Can lend documents"),
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
