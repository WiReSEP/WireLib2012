# vim: set fileencoding=utf-8
from models import author
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from documents.models import document
import settings

def functions_test(self):
    """
    Um eine Funktion zu testen, die nur einen einfachen Text zurückgibt, 
    einfach die Funktion statt dem String einfüge und die Seite ~/funktionstest aufrufen.
    """
    response = HttpResponse("testfunktion hier einfügen")
    response["ContentType"] = "text/plain"
    return response

def index(request): 	
    """ Index der App.
    Bietet dem Benutzer nur eine Übersicht.
    TODO: Was sollte er auf dieser Seite noch sehen?
    """
    documents = document.objects.all().order_by("-title")
    return render_to_response("literatur.html", dict(documents=documents, user=request.user, settings=settings))

def search(request):
    """ Suche nach Dokumenten.
    Hier kann der Benutzer Dokumente suchen, finden und Überraschungseier
    finden.
    """
    return render_to_response("search.html")

def search_pro(request):
    """ Erweiterte Suche nach Dokumeten.
    Hier kann der Benutzer mit einer übersichtlichen Form nach Dokumenten
    suchen. Diese Suche soll auch dem Benutzer, der nicht mit Google umgehen
    kann die Möglichkeit geben ein Dokument spezifisch zu suchen und zu finden!
    """
    return render_to_response("search_pro.html")

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    Dem Benutzer wird ein reichhaltiges Angebot an Dokumenten angeboten und
    übersichtlich präsentiert. Er kann nach belieben zwischen Dokumenten die
    'A' beginnend oder Autoren mit 'Z' beginnend wählen.
    Jedes Dokument muss selbständig abgeholt werden, wir haften nicht für den
    Reiseweg!
    """
    return render_to_response("doc_list.html")

def doc_detail(request):
    """ Detailansicht zum Dokument

    """
    return render_to_response("doc_detail.html")

def doc_add(request):
    """ Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies kann auf folgende Arten geschehen:
        * Import durch Formeingabe
        * Import durch Upload einer BibTeX-Datei
    """
    return render_to_response("doc_add.html")

def doc_rent(request):
    """ Des Benutzers Ausleihliste
    Alle Dokumente die der Benutzer ausgeliehen hat und die Dokumente für die
    der Benutzer für andere Bürgt.
    """
    return render_to_response("doc_rent.html")

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
    
def unsere_suche (request):
    context = Context()
    if "suchanfrage_starten" in request.GET:
        suchtext = request.POST.get('suche','')
        response = HttpResponse(suchtext)
        response["ContentType"] = "text/plain"
        return response
    else:
        context = Context()
        template = loader.get_template("unsere_suche.html")
        return HttpResponse(template.render(context))
