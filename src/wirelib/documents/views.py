# vim: set fileencoding=utf-8
from models import author
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from documents.models import document, lending, doc_extra
from documents.extras_bibtex import Bibtex
import settings


headers = {'title':'asc', 
            'category':'asc',
            'authors':'asc',
            'year':'asc',
            'status':'asc',
            'isbn':'asc'
            
            }
def literatur(request):
    sort = request.GET.get('sort')
    documents = document.objects.all()
    
    if sort is not None:
        documents = documents.order_by(sort)
        if headers[sort] == "des":
            documents = documents.reverse()
            headers[sort] = "asc"
    
    return render_to_response("literatur.html", dict(documents=documents, user=request.user, settings=settings))
            
            
"""       
def index(request): 	
    Index der App.
    Bietet dem Benutzer nur eine Übersicht.
    TODO: Was sollte er auf dieser Seite noch sehen?

    documents = document.objects.all().order_by("-title")
    return render_to_response("literatur.html", dict(documents=documents,       user=request.user, settings=settings))"""

def search(request):
    """ Suche nach Dokumenten.
    Hier kann der Benutzer Dokumente suchen, finden und Überraschungseier
    finden.
    """
    context = Context()
    if "suchanfrage_starten" in request.GET:
        suchtext = request.POST.get('suche','')
        document_query = document.objects.filter(title__icontains=suchtext)
        template = loader.get_template("suchergebnis.html")
        context = Context({"documents" : document_query})
        response = HttpResponse(template.render(context))
        #response["ContentType"] = "text/plain"
        return response
    else:
        context = Context()
        template = loader.get_template("search.html")
        return HttpResponse(template.render(context))

def search_pro(request):
    """ Erweiterte Suche nach Dokumeten.
    Hier kann der Benutzer mit einer übersichtlichen Form nach Dokumenten
    suchen. Diese Suche soll auch dem Benutzer, der nicht mit Google umgehen
    kann die Möglichkeit geben ein Dokument spezifisch zu suchen und zu finden!
    """
    if "pro_search_result" in request.GET:
        s_author = request.POST.get('author','')
        s_title = request.POST.get('title','')
        s_year = request.POST.get('year','')
        s_publisher = request.POST.get('publisher','')
        s_bib_no = request.POST.get('bib_no','Test')
        s_isbn = request.POST.get('isbn','')
        s_keywords = request.POST.get('keywords','')
        s_documents = document.objects.filter(title__icontains = s_title)
        if s_author != "":
            s_documents = s_documents.filter(authors__last_name__icontains =
                                             s_author)
        if s_year != "":
            s_documents = s_documents.filter(year__icontains = s_year)
        if s_publisher != "":
            s_documents = s_documents.filter(publisher__name__icontains = s_publisher)
        if s_bib_no != "":
            s_documents = s_documents.filter(bib_no__icontains = s_bib_no)
        if s_isbn != "":
            s_documents = s_documents.filter(isbn__icontains = s_isbn)
        if s_keywords != "":
            s_documents = s_documents.filter(keywords__keyword__icontains = s_keywords) 
        template = loader.get_template("suchergebnis.html")
        context = Context({"documents" : s_documents})
        response = HttpResponse(template.render(context))
        return response
    else:
        return render_to_response("search_pro.html")

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    Dem Benutzer wird ein reichhaltiges Angebot an Dokumenten angeboten und
    übersichtlich präsentiert. Er kann nach belieben zwischen Dokumenten die
    'A' beginnend oder Autoren mit 'Z' beginnend wählen.
    Jedes Dokument muss selbständig abgeholt werden, wir haften nicht für den
    Reiseweg!
    """
    sort = request.GET.get('sort')
    documents = document.objects.all()
    if sort is not None:
        documents = documents.order_by(sort)
        if headers[sort] == "des":
            documents = documents.reverse()
            headers[sort] = "asc"
    
    return render_to_response("doc_list.html", dict(documents=documents, user=request.user, settings=settings))
        
   

def doc_detail(request, bib_no_id):
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.lending_set.latest("date_lend")
    except lending.DoesNotExist:
        lending_query = None
    doc_extra_query = doc_extra.objects.filter(doc_id__bib_no__icontains=bib_no_id)
    bibtex_string = Bibtex.export_doc(document_query)
    template = loader.get_template("doc_detail.html")
    context = Context({"documents" : document_query,
                      "lending" : lending_query,
                      "doc_extra" : doc_extra_query,
                      "bi" : bibtex_string})
    response = HttpResponse(template.render(context))
    return response

def index(request): 
    return render_to_response("home.html")

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
        document_query = document.objects.filter(title__icontains=suchtext)
        template = loader.get_template("suchergebnis.html")
        context = Context({"documents" : document_query})
        response = HttpResponse(template.render(context))
        #response["ContentType"] = "text/plain"
        return response
    else:
        context = Context()
        template = loader.get_template("unsere_suche.html")
        return HttpResponse(template.render(context))
