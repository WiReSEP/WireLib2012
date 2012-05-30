from django.db import models
from django.contrib.auth.models import User

class category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    
class publisher(models.Model):
    name = models.CharField(max_length=35, primary_key=True)
        
class document(models.Model):
    bibNo = models.CharField(max_length=15, primary_key=True)
    invNo = models.CharField(max_length=15)
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=17, null=True)
    category = models.ForeignKey(category)
    status = models.IntegerField()
    publisher = models.ForeignKey(publisher)
    pubDate = models.DateField()
    adress = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2);
    currency = models.CharField(max_length=3)
    dateOfPurchase = models.DateField(auto_now_add=True)
    ubDate = models.DateField(null=True)
    
class author(models.Model):
    documents = models.ManyToManyField(document)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=40)
    primary_key(name, surname)
    
class keywords(models.Model):
    document = models.ForeignKey(document)
    keyword = models.CharField(max_length=50)
    primary_key(document, keyword)
    
class doc_extra(models.Model):
    """
    Bietet die Möglichkeit für mehrere extra Felder für ein Dokument
    """
    docId = models.ForeignKey(document)
    bibField = models.CharField(max_length=40)
    content = models.CharField(max_length=200)
    primary_key(docId, bibField, content)

class nonUser(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=40)
    email = models.EmailField(unique=True)
    street = models.CharField(max_length=30)
    number = models.CharField(max_length=5)
    zipcode = models.CharField(max_length=5)
    city = models.CharField(max_length=58)

class lending(models.Model):
    docId = models.ForeignKey(document)
    dateLend = models.DateTimeField(auto_now_add=True)
    dateReturn = models.DateTimeField(null=True)
    dateTerm = models.DateTimeField(null=True)
    userLend = models.ForeignKey(User)
    nonUserLend = models.ForeignKey(non_user, null=True)

