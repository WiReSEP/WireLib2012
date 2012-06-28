# vim: set fileencoding=utf-8
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template import RequestContext 
from documents.models import document, doc_status, doc_extra, category, EmailValidation
from documents.extras_doc_funcs import insert_doc
from documents.extras_bibtex import Bibtex, UglyBibtex
from documents.forms import EmailValidationForm, UploadFileForm
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.db.models import Q
import datetime
import os
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
        perms =  v_user.has_perm('cs_admin')
        context = Context({"user" : v_user, "perm" : perms})
        template = loader.get_template("search.html")
        return HttpResponse(template.render(context))

def search_pro(request):
    """ Erweiterte Suche nach Dokumeten.
    Hier kann der Benutzer mit einer übersichtlichen Form nach Dokumenten
    suchen. Diese Suche soll auch dem Benutzer, der nicht mit Google umgehen
    kann die Möglichkeit geben ein Dokument spezifisch zu suchen und zu finden!
    """
    #Abfrage ob bereits eine Suche gestartet wurde
    if "title" in request.GET:
        #Auslesen der benötigten Variablen aus dem Request
        s_author = request.GET.get('author','')
        s_title = request.GET.get('title','')
        s_year = request.GET.get('year','')
        s_publisher = request.GET.get('publisher','')
        s_bib_no = request.GET.get('bib_no','Test')
        s_isbn = request.GET.get('isbn','')
        s_keywords = request.GET.get('keywords','')
        #Aufeinanderfolgendes Filtern nach Suchbegriffen
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
        #Laden der Suchseite, falls noch keine Suche gestartet worden ist.
        v_user = request.user
        perms =  v_user.has_perm('cs_admin')
        return render_to_response("search_pro.html",context_instance=Context({"user" :
                       v_user, "perm" : perms}))

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    """
    documents = document.objects.all()
    return __list(request, documents)

def doc_detail(request, bib_no_id):
    v_user = request.user
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.doc_status_set.latest("date")
    except doc_status.DoesNotExist:
        lending_query = None
    #selbst ausleihen, wenn Status vorhanden
    if 'lend' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    #zurückgeben
    if 'restitution' in request.POST and request.user.is_authenticated():
        document_query.unlend(v_user)
    #vermisst melden
    if 'lost' in request.POST and request.user.is_authenticated():
        document_query.lost(v_user)
    #wiedergefunden melden
    if 'found' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    doc_extra_query = doc_extra.objects.filter(doc_id__bib_no__exact=bib_no_id)
    bibtex_string = Bibtex.export_doc(document_query)
    template = loader.get_template("doc_detail.html")
    #auslesen der für die doc_detail.html benötigten Rechte
    perms =  v_user.has_perm('cs_admin')
    c_lm = v_user.has_perm('c_lend_miss')
    c_lo = v_user.has_perm('c_lost_order')
    cs_history = v_user.has_perm('cs_history')
    c_transfer = v_user.has_perm('c_transfer')
    cs_price = v_user.has_perm('cs_price')
    cs_locn = v_user.has_perm('cs_locn')
    cs_lui = v_user.has_perm('cs_last_update_info')
    cs_dop = v_user.has_perm('cs_dop')
    cs_export = v_user.has_perm('cs_export')

    context = Context({"documents" : document_query,
                      "lending" : lending_query,
                      "doc_extra" : doc_extra_query,
                      "bi" : bibtex_string,
                      "user" : v_user,
                      "perm" : perms,
                      "c_lo" : c_lo,
                      "cs_history" : cs_history,
                      "c_transfer" : c_transfer,
                      "cs_price" : cs_price,
                      "cs_locn" : cs_locn,
                      "cs_lui" : cs_lui,
                      "cs_dop" : cs_dop,
                      "cs_export" : cs_export,
                      "c_lm" : c_lm})
    response = HttpResponse(template.render(context))
    return response

def index(request): 
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("index.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))
@login_required
def profile(request): 
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("profile.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))
@login_required
def profile_settings(request): 
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("profile_settings.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))
                              
def email_validation(request): 
    
    if request.method == 'POST': 
        form = EmailValidationForm(request.POST)
        if form.is_valid(): 
            EmailValidation.objects.add(user=request.user, email=form.cleaned_data.get('email'))
            return HttpResponseRedirect('%sprocessed/' % request.path_info)
    else: 
        form = EmailValidationForm()
    
    template = "account/email_validation.html"
    data = { 'form': form, }
    return render_to_response(template, data, context_instance=RequestContext(request))
                  


@login_required
def doc_add(request):
    """ Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies kann auf folgende Arten geschehen:
        * Import durch Formeingabe
        * Import durch Upload einer BibTeX-Datei
    """
    #TODO Rechtekontrolle
    v_user = request.user
    if len(request.FILES) > 0:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            date = datetime.datetime.today()
            filename = 'imports/' + datetime.datetime.strftime(date, '%s') + '.bib'
            destination = open(filename, 'wb+')
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()
            UglyBibtex(filename).do_import()
            os.remove(filename)
            filesize = os.path.getsize(filename + '.err')
            if filesize == 0:
                message = 'Datei erfolgreich übernommen'
            else:
                errfile = open(filename + '.err', 'r')
                message = 'Datei konnte nicht vollständig übernommen werden <br /> /n <br /> /n'
                for line in errfile:
                    message += line + '<br /> /n'
                errfile.close()
            os.remove(filename + '.err')
    elif 'title' in request.POST:
        insert = {}
        insert[u"title"] = request.POST.get('title','')
        insert[u"bib_no"] = request.POST.get('bib_no','').upper()
        insert[u"inv_no"] = request.POST.get('inv_no','')
        insert[u"category"] = request.POST.get('category','')
        insert[u"publisher"] = request.POST.get('publisher','')
        insert[u"year"] = request.POST.get('year','')
        insert[u"address"] = request.POST.get('address','')
        insert[u"comment"] = request.POST.get('comment','')
        insert[u"currency"] = request.POST.get('currency','')
        insert[u"lib_of_con_nr"] = request.POST.get('lib_of_con_nr','')
        insert[u"isbn"] = request.POST.get('isbn','')
        
        firstnames = request.POST.getlist('author_first_name')
        lastnames = request.POST.getlist('author_last_name')
        authors = []
        bibtex = u""
        for a in range(0,len(firstnames)-1):
            if not lastnames[a] == '':
                authors.append(lastnames[a] + u", " + firstnames[a])
                bibtex += lastnames[a]
        bibtex += insert[u"inv_no"]
        insert[u"bibtex_id"] = bibtex
        insert[u"author"] = authors
        
        key = []
        keyword = request.POST.getlist('keyword')
        for k in range(0,len(keyword)-1):
            if not keyword[k] == '':
                key.append(keyword[k])
        insert[u"keywords"] = key
        
        extras = {}
        names = request.POST.getlist('doc_extra_name')
        content = request.POST.getlist('doc_extra_content')
        for i in range(0, len(names)-1):
            if not names == '':
                extras[names[i]] = content[i]
        insert[u"extras"] = extras
        
        insert_doc(insert, v_user)
        message = 'Daten erfolgreich übernommen'
        #documents.extras_doc_funcs.insert_doc(insert,v_user) 
    else:
        message = ''
    form = UploadFileForm()
    perms = v_user.has_perm('cs_admin')
    cat = category.objects.filter()
    return render_to_response("doc_add.html",
                              context_instance=Context(
                                  {"user" : v_user, 
                                   "perm" : perms, 
                                   "category" : cat,
                                   "form" : form,
                                   "message" : message}))

@login_required
def doc_rent(request):
    """ Des Benutzers Ausleihliste
    Alle Dokumente die der Benutzer ausgeliehen hat und die Dokumente für die
    der Benutzer für andere Bürgt.
    """
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("doc_rent.html",context_instance=Context({"user"
                              : v_user, "perm" : perms}))

@login_required
def export(request):
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("export.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def allegro_export(request):
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
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
    perms =  v_user.has_perm('cs_admin')
    return render_to_response("bibtex_export.html",context_instance=Context({"user" :
                              v_user, "perm" : perms}))

@login_required
def user(request):
    lend_documents = document.objects.filter(
            doc_status__return_lend__exact = False,
            doc_status__user_lend__exact = request.user,
            doc_status__non_user_lend__exact = None)
    return __list(request, lend_documents)

def __list(request, documents, form=0):
    """ Erzeugt eine Liste vom Typ "form".
        0 = Literaturverzeichnis oder Suchergebnis
        1 = Ausleihe
    """
    documents = __filter_names(documents, request)
    sort = request.GET.get('sort')
    if sort is not None:
        documents = documents.order_by(sort)
        if headers[sort] == "des":
            documents = documents.reverse()
            headers[sort] = "asc"
    v_user = request.user
    perms =  v_user.has_perm('cs_admin')
    params_sort = __truncate_get(request, 'sort')
    params_starts = __truncate_get(request, 'starts', 'page')
    return render_to_response("doc_list.html", 
            dict(documents = documents,
                user = v_user, 
                settings = settings, 
                perm = perms,
                path_sort = params_sort, 
                path_starts = params_starts,
                form = form),
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


