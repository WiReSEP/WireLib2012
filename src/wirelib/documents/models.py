# vim: set fileencoding=utf-8
from django.db import models
from django.contrib.auth.models import User

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
    
class publisher(models.Model):
    name = models.CharField(max_length=35, primary_key=True)
        
class document(models.Model):
    bib_no = models.CharField(max_length=15, primary_key=True)
    inv_no = models.CharField(max_length=15, unique=True)
    bibtex_id = models.CharField(max_length=120, unique=True)
    lib_of_con_nr = models.CharField(max_length=20) #LibraryOfCongressN
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=17, null=True)
    category = models.ForeignKey(category)
    status = models.IntegerField()
        #(0) vorhanden
        #(1) ausgeliehen
        #(2) bestellt
        #(3) vermisst
        #(4) verloren
    last_updated = models.DateField(auto_now=True) 
    publisher = models.ForeignKey(publisher)
    year = models.IntegerField()
    address = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3)
    date_of_purchase = models.DateField(auto_now_add=True)
    ub_date = models.DateField(null=True)
    comment = models.TextField(null=True)

    
class author(models.Model):
    documents = models.ManyToManyField(document)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    class Meta:
        unique_together = ('first_name', 'last_name')
    #primary ('name', 'surname')
    
class keywords(models.Model):
    document = models.ForeignKey(document)
    keyword = models.CharField(max_length=50)
    class Meta:
        unique_together = ('document', 'keyword')
    #primary_key(document, keyword)
    
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
    
class tel_user(models.Model):
    user = models.ForeignKey(user_profile)
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
    class Meta:
        unique_together = ('last_name', 'first_name')

class tel_non_user(models.Model):
    non_user = models.ForeignKey(non_user)
    tel_nr = models.CharField(max_length=20)
        #todo
    class Meta:
        unique_together = ('non_user', 'tel_nr')

class lending(models.Model):
    doc_id = models.ForeignKey(document)
    date_lend = models.DateTimeField(auto_now_add=True)
    date_return = models.DateTimeField(null=True)
    date_term = models.DateTimeField(null=True)
    user_lend = models.ForeignKey(User)
    non_user_lend = models.ForeignKey(non_user, null=True)

