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
    first_name = models.CharField(max_length=30)
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
    #TODO Referenz einbauen
    #status = models.IntegerField()
        #(0) vorhanden
        #(1) ausgeliehen
        #(2) bestellt
        #(3) vermisst
        #(4) verloren
    last_updated = models.DateField(auto_now=True)
    # TODO recent_user = models.ForeignKey(User)
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

    def __unicode__(self):
        return self.title

    def lend(self, user, non_user=None, terminate=None):
        if self.status != 0 and self.status != 3 :
            raise LendingError()
        self.status = 1
        l = lending(
                doc_id=self,
                date_term = terminate,
                user_lend = user,
                non_user_lend = non_user,
        )
        l.save()
        self.save()

    def restitution(self, user):
        self.status = 0
        l = lending.objects.get(
            doc_id = self,
            date_return = None,
            user_lend = user,
        )
        l.date_return = datetime.now()
        l.save()
        self.save()

    def lost(self, user):
        self.status = 3
        l = lending.objects.get(
            doc_id = self,
            date_return = None,
            user_lend = user,
        )
        l.date_return = datetime.now()
        l.save()
        self.save()

class keywords(models.Model):
    document = models.ForeignKey(document)
    keyword = models.CharField(max_length=50)
    class Meta:
        unique_together = ('document', 'keyword')
    #primary_key(document, keyword)
    
    def __unicode__(self):
        return self.keyword

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
    #todo
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
        #todo
    class Meta:
        unique_together = ('non_user', 'tel_nr')

class doc_status(models.Model):
    recent_user = models.ForeignKey(User) 
        #auftraggebender User
    doc_id = models.ForeignKey(document) 
    status = models.IntegerField() 
        #in welchen Status wurde geändert?
    date = models.DateTimeField(auto_now_add=True) 
        #Datum an dem es geschah
    date_term_lend = models.DateTimeField(null=True) 
        #Ende der Rückgabefrist
    user_lend = models.ForeignKey(User, null=True) 
        #ausleihender User
    non_user_lend = models.ForeignKey(non_user, null=True) 
        #ausleihender non_User

class emails(models.Model):
    text = models.TextField()

# TODO: Check für migration
