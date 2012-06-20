# vim: set fileencoding=utf-8
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template import RequestContext 
from documents.models import document, lending, doc_extra
from documents.extras_bibtex import Bibtex
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.db.models import Q
import settings
import thread


headers = {'title':'asc', 
            'category':'asc',
            'authors':'asc',
            'year':'asc',
            'status':'asc',
            'isbn':'asc'
            
            }
            
def search(request):
    """ Suche nach Dokumenten.
    Hier kann der Benutzer Dokumente suchen, finden und Überraschungseier
    finden.
    """
    context = Context()
    if "query" in request.GET:
        suchtext = request.GET.get('query','')
        documents = document.objects.filter(title__icontains=suchtext)
        return __list(request, documents)
    else:
        v_user = request.user
        perms =  v_user.has_perm('add_author')
        context = Context({"user" : v_user, "perm" : perms})
        template = loader.get_template("search.html")
        return HttpResponse(template.render(context))

def search_pro(request):
    """ Erweiterte Suche nach Dokumeten.
    Hier kann der Benutzer mit einer übersichtlichen Form nach Dokumenten
    suchen. Diese Suche soll auch dem Benutzer, der nicht mit Google umgehen
    kann die Möglichkeit geben ein Dokument spezifisch zu suchen und zu finden!
    """
    if "title" in request.GET:
        s_author = request.GET.get('author','')
        s_title = request.GET.get('title','')
        s_year = request.GET.get('year','')
        s_publisher = request.GET.get('publisher','')
        s_bib_no = request.GET.get('bib_no','Test')
        s_isbn = request.GET.get('isbn','')
        s_keywords = request.GET.get('keywords','')
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
        return __list(request, s_documents)
    else:
        v_user = request.user
        perms =  v_user.has_perm('add_author')
        return render_to_response("search_pro.html",context_instance=Context({"user" :
                       v_user, "perm" : perms}))

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    """
    documents = document.objects.all()
    return __list(request, documents)
    
#def a_c(request):
 #   documents = document.objects.filter(
  #                      Q(title__istartswith='a') | 
   #                     Q(title__istartswith='b') | 
    #                    Q(title__istartswith='c'))
    #return __list(request, documents)

def doc_detail(request, bib_no_id):
    v_user = request.user
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.lending_set.latest("date_lend")
    except lending.DoesNotExist:
        lending_query = None
    if 'lend' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    if 'restitution' in request.POST and request.user.is_authenticated():
        document_query.restitution(v_user)
    if 'lost' in request.POST and request.user.is_authenticated():
        document_query.lost(v_user)
    if 'found' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    doc_extra_query = doc_extra.objects.filter(doc_id__bib_no__exact=bib_no_id)
    bibtex_string = Bibtex.export_doc(document_query)
    template = loader.get_template("doc_detail.html")
    perms =  v_user.has_perm('add_author')
    context = Context({"documents" : document_query,
                      "lending" : lending_query,
                      "doc_extra" : doc_extra_query,
                      "bi" : bibtex_string,
                      "user" : v_user,
                      "perm" : perms})
    response = HttpResponse(template.render(context))
    return response

def index(request): 
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("home.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

def profile(request): 
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("profile.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

def profile_settings(request): 
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("profile_settings.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))
                  


@login_required
def doc_add(request):
    """ Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies kann auf folgende Arten geschehen:
        * Import durch Formeingabe
        * Import durch Upload einer BibTeX-Datei
    """
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("doc_add.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def doc_rent(request):
    """ Des Benutzers Ausleihliste
    Alle Dokumente die der Benutzer ausgeliehen hat und die Dokumente für die
    der Benutzer für andere Bürgt.
    """
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("doc_rent.html",context_instance=Context({"user"
                              : v_user, "perm" : perms}))

@login_required
def export(request):
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("export.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def allegro_export(request):
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("allegro_export.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def bibtex_export(request):
    """ Seite um den Datenbankexport in BibTeX zu initiieren und für den
    Zugriff auf bisher exportierte BibTeX-Exporte.
    TODO: Zugriff nur auf Benutzer beschränken, die Dokumente hinzufügen
    dürfen.
    TODO: Dateien für entsprechende Benutzer publizieren.
    """
    if "bibtex_export" in request.POST:
        export_documents = document.objects.filter(
                bib_date__isnull=True,
                )
        thread.start_new_thread(Bibtex.export_docs,( export_documents, ) )

    v_user = request.user
    perms =  v_user.has_perm('add_author')
    return render_to_response("bibtex_export.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def user(request):
    lend_documents = document.objects.filter(
            lending__date_return__exact = None,
            lending__user_lend__exact = request.user,
            lending__non_user_lend__exact = None)
    return __list(request, lend_documents)

def __list(request, documents):
    documents = __filter_names(documents, request)
    sort = request.GET.get('sort')
    if sort is not None:
        documents = documents.order_by(sort)
        if headers[sort] == "des":
            documents = documents.reverse()
            headers[sort] = "asc"
    v_user = request.user
    perms =  v_user.has_perm('add_author')
    params_sort = __truncate_get(request, 'sort')
    params_starts = __truncate_get(request, 'starts', 'page')
    return render_to_response("doc_list.html", 
            dict(documents=documents,
                user=v_user, 
                settings=settings, 
                perm=perms,
                path_sort=params_sort, 
                path_starts=params_starts ),
            context_instance=RequestContext(request))

def __truncate_get(request, *var):
    params = request.GET.copy()
    test = False
    for arg in var:
        if arg in params:
            test = True
    if not test:
        return params.urlencode() # no need to truncate
    params_tmp = u""
    for key in params:
        if not key in var:
            params_tmp += key + u"=" + params[key] + u"&"
    params = QueryDict(params_tmp)
    return params.urlencode()

def __filter_names(documents, request):
    """ Dem Benutzer wird ein reichhaltiges Angebot an Dokumenten angeboten und
    übersichtlich präsentiert. Er kann nach belieben zwischen Dokumenten die
    'A' beginnend oder Autoren mit 'Z' beginnend wählen.
    Jedes Dokument muss selbständig abgeholt werden, wir haften nicht für den
    Reiseweg!
    """
    sw = request.GET.get('starts', '')
    if sw == "0-9":
        documents = documents.filter(
                         Q(title__istartswith='0') | 
                         Q(title__istartswith='1') | 
                         Q(title__istartswith='2') |
                         Q(title__istartswith='3') |
                         Q(title__istartswith='4') |
                         Q(title__istartswith='5') |
                         Q(title__istartswith='6') |
                         Q(title__istartswith='7') |
                         Q(title__istartswith='8') |
                         Q(title__istartswith='9')) 
    elif sw == "a-c":
        documents = documents.filter(
                         Q(title__istartswith='a') |
                         Q(title__istartswith='ä') |
                         Q(title__istartswith='b') | 
                         Q(title__istartswith='c'))
    elif sw == "d-f": 
        documents = documents.filter(
                         Q(title__istartswith='d') | 
                         Q(title__istartswith='e') | 
                         Q(title__istartswith='f'))
    elif sw == "g-i":
        documents = documents.filter(
                         Q(title__istartswith='g') | 
                         Q(title__istartswith='h') | 
                         Q(title__istartswith='i'))
    elif sw == "j-l":
        documents = documents.filter(
                         Q(title__istartswith='j') | 
                         Q(title__istartswith='k') | 
                         Q(title__istartswith='l'))
    elif sw == "m-o":
        documents = documents.filter(
                         Q(title__istartswith='m') | 
                         Q(title__istartswith='n') | 
                         Q(title__istartswith='o') |
                         Q(title__istartswith='ö'))
    elif sw == "p-s":
        documents = documents.filter(
                         Q(title__istartswith='p') | 
                         Q(title__istartswith='q') | 
                         Q(title__istartswith='r') |
                         Q(title__istartswith='s'))
    elif sw == "t-v":
        documents = documents.filter(
                         Q(title__istartswith='t') | 
                         Q(title__istartswith='u') |
                         Q(title__istartswith='ü') | 
                         Q(title__istartswith='v'))
    elif sw == "w-z":
        documents = documents.filter(
                         Q(title__istartswith='w') | 
                         Q(title__istartswith='x') | 
                         Q(title__istartswith='y') |
                         Q(title__istartswith='z'))
    elif sw == "all":
        documents = documents.all()                     
    return documents
