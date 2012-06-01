# vim: set fileencoding=utf-8
from models import author
from django.http import HttpResponse
from django.template import Context, loader

def functions_test(self):
    """
    Um eine Funktion zu testen, die nur einen einfachen Text zurückgibt, 
    einfach die Funktion statt dem String einfüge und die Seite ~/funktionstest aufrufen.
    """
    response = HttpResponse("testfunktion hier einfügen")
    response["ContentType"] = "text/plain"
    return response

def authorbooks (request, s_author):
    author_query = author.objects.filter(surname__icontains=s_author)
    book_titles=[]
    for document in author_query.objects.all():
        book_titles.append(document.title)
    response = HttpResponse("/n".join(book_titles))
    response["Content-Type"] = "text/plain"
    return response

def templatebeispiel (request, s_author):
    author_query = author.objects.filter(surname__icontains=s_author)
    template = loader.get_template("Beispielbuchausgabe.html")
    context = Context({"authoren" : author_query.objects.all()})
    return HttpResponse(template.render(context))
