# vim: set fileencoding=utf-8
from django.db import models
from django.contrib.auth.models import User

class category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

class document(models.Model):
    bib_no = models.CharField(max_length=15, primary_key=True)
    title = models.CharField(max_length=100)
    isbn = models.CharField(max_length=17)
    category = models.ForeignKey(category)
    status = models.IntegerField()

class doc_extra(models.Model):
    """
    Bietet die Möglichkeit für mehrere extra Felder für ein Dokument
    """
    doc_id = models.ForeignKey(document)
    bib_field = models.CharField(max_length=40)
    content = models.CharField(max_length=200)

class author(models.Model):
    documents = models.ManyToManyField(document)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=40)

class non_user(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=40)

    email = models.EmailField(unique=True)
    

    street = models.CharField(max_length=30)
    number = models.CharField(max_length=5)

    zipcode = models.CharField(max_length=5)
    city = models.CharField(max_length=58)


class lending(models.Model):
    doc_id = models.ForeignKey(document)

    date_lend = models.DateTimeField(auto_now_add=True)
    date_return = models.DateTimeField(null=True)
    date_term = models.DateTimeField(null=True)

    user_lend = models.ForeignKey(User)
    nonuser_lend = models.ForeignKey(non_user, null=True)

