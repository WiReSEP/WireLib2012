# vim: set fileencoding=utf-8
from models import *
from django.http import HttpResponse
from django.template import Context, loader

def authorbooks (request, author):
    author_query = author.objects.filter(surname__icontains=s_author)
    book_titles=[]
    for document in author_query.objects.all():
        book_titles.append(document.title)
    response = HttpResponse("/n".join(book_titles))
    response["Content-Type"] = "text/plain"
    return response

def templatebeispiel (request, author):
    author_query = author.objects.filter(surname__icontains=s_author)
    template = loader.get_template("Beispielbuchausgabe.html")
    context = Context({"authoren" : author_query.objects.all()})
    return HttpResponse(template.render(context))
