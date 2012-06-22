# vim: set fileencoding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from exceptions import LendingError
from datetime import datetime
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

    def __unicode__(self):
        return self.name
    
class publisher(models.Model):
    name = models.CharField(max_length=35, primary_key=True)
    
    def __unicode__(self):
        return self.name


class author(models.Model):
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30)
    class Meta:
        unique_together = ('first_name', 'last_name')
    #primary ('name', 'surname')
    
    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)

class document(models.Model):
    bib_no = models.CharField(max_length=15, primary_key=True)
    inv_no = models.CharField(max_length=15, unique=True)
    bibtex_id = models.CharField(max_length=120, unique=True)
    lib_of_con_nr = models.CharField(max_length=20, null=True) 
        #LibraryOfCongressN
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=17, null=True)
    category = models.ForeignKey(category)
    last_updated = models.DateField(auto_now=True)
    last_edit_by = models.ForeignKey(User)
    publisher = models.ForeignKey(publisher, null=True)
    year = models.IntegerField(null=True)
    address = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    currency = models.CharField(max_length=3, null=True)
    date_of_purchase = models.DateField(auto_now_add=True)
    ub_date = models.DateField(null=True) 
        #Datum des Allegro-Exports
    bib_date = models.DateField(null=True) 
        #Datum des BibTeX-Exports
    comment = models.TextField(null=True)
    authors = models.ManyToManyField(author)

    stat_available = 0  #vorhanden
    stat_lend = 1       #ausgeliehen
    stat_ordered = 2    #bestellt
    stat_miss = 3       #vermisst
    stat_lost = 4       #verloren
    
    def save(self, user=None, *args, **kwargs):
        """
        Methode zum Speichern des letzten Bearbeiters des Dokumentes
        """
        #TODO nach Datenbankerstellung überprüfen, ob die if-Anweisung noch benötigt wird
        if user == None:
            user = User.get(username='admin')
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
    
    def __set_status(self, 
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
        self.doc_status_set.latest('date').update(return_lend=True)
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
        if self.status == stat_lend:
            dstat = self.doc_status_set.latest('date')
            if dstat.user_lend == user and dstats.non_user_lend == non_user:
                raise LendingError()
        # zum Ausleihen oder Wiederfinden
        elif self.status != stat_available and self.status != stat_miss :
            raise LendingError()
        if editor == None:
            editor = user
        self.__set_status(editor, stat_lend, terminate, user, non_user)

    def unlend(self, user):
        """ 
        Methode zum zurückgeben 
        """
        self.__set_status(user, stat_available)

    def lost(self, user):
        """ 
        Methode zum "Verloren" setzen
        """
        self.__set_status(user, stat_lost)
        
    def missing(self, user):
        """ 
        Methode für Vermisstmeldungen
        """
        self.__set_status(user, stat_miss)

class keywords(models.Model):
    document = models.ForeignKey(document)
    keyword = models.CharField(max_length=50)
    class Meta:
        unique_together = ('document', 'keyword')
    #primary_key(document, keyword)
    
    def __unicode__(self):
        return self.keyword
        
    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter 
        aktualisiert werden kann
        """
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
    
    def save(self, user=None, *args, **kwargs):
        """
        Methode, damit in der Tabelle 'document' der letzte Bearbeiter 
        aktualisiert werden kann
        """
        self.doc_id.save(user)
        super(doc_extra, self).save(*args, **kwargs)

class user_profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    street = models.CharField(max_length=30)
    number = models.CharField(max_length=5)
    zipcode = models.CharField(max_length=5)
    city = models.CharField(max_length=58)

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
    tel_nr = models.CharField(max_length=20)
    # TODO eigene Telefonnummerklasse
    class Meta:
        unique_together = ('user', 'tel_nr')

class non_user(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    street = models.CharField(max_length=30)
    number = models.CharField(max_length=5)
    zipcode = models.CharField(max_length=5)
    city = models.CharField(max_length=58)

    def __unicode__(self):
        return (self.last_name + ', ' + self.first_name)

class tel_non_user(models.Model):
    non_user = models.ForeignKey(non_user)
    tel_nr = models.CharField(max_length=20)
    # TODO eigene Telefonnummerklasser
    class Meta:
        unique_together = ('non_user', 'tel_nr')

class doc_status(models.Model):
    recent_user = models.ForeignKey(User, related_name='recent_user') 
        #auftraggebender User
    doc_id = models.ForeignKey(document) 
    status = models.IntegerField() 
        #in welchen Status wurde geändert?
    date = models.DateTimeField(auto_now_add=True) 
        #Datum an dem es geschah
    return_lend = models.BooleanField(default=False)
        #Datum der Rückgabe
    date_term_lend = models.DateTimeField(null=True) 
        #Ende der Rückgabefrist
    user_lend = models.ForeignKey(User, null=True, related_name='user_lend') 
        #ausleihender User
    non_user_lend = models.ForeignKey(non_user, null=True) 
        #ausleihender non_User

class emails(models.Model):
    text = models.TextField()
