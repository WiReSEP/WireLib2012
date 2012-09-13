# vim: set fileencoding=utf-8
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template import RequestContext, Template 
from documents.models import document, doc_status, doc_extra, category,\
    EmailValidation, emails, user_profile, tel_user, \
    tel_non_user
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory
from documents.lib.bibtex import Bibtex
from documents.lib.allegro import Allegro
from documents.forms import EmailValidationForm, UploadFileForm, DocForm, \
    AuthorAddForm, SelectUser, NonUserForm, ProfileForm, \
    TelNonUserForm, NameForm, PublisherAddForm
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Q


import datetime
import os
import settings
import thread

# Für Filter von dict
from django import template
register = template.Library()

def get_dict_response(request):
    v_user = request.user
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    perms =  v_user.has_perm('documents.can_see_admin')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                             doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return {"user" : v_user, 
            "perm" : perms,
            "miss" : miss_query[0:10],
            "import_perm" : import_perm,
            "export_perm" : export_perm}


def search(request):
    """ Suche nach Dokumenten.
    Hier kann der Benutzer Dokumente suchen, finden und Überraschungseier
    finden.
    """
    #Wenn bereits eine Suche gestartet wurde
    if "query" in request.GET:
        #Eingabe des Users aus dem request auslesen
        searchtext = request.GET.get('query','')
        #Erstellen eines Sets aus allen Suchbegriffen.
        #Aufgrund des Verfahrens eine ODER-Suche
        #Aufspaltung des Suchbegriffs
        searchtext_split = searchtext.split(" ")
        #Verpackung in eine Liste für einheitliche Übergabe
        searchtext = [searchtext]
        #Initialisierung der für Schleife benötigten Variablen
        first_for = True
        next_action = "none"
        not_active = False
        for i in searchtext_split:
            #Falls erster Schleifendurchgang
            if first_for:
                first_for = False
                #Statt Filtern QuerySet erstellen
                document_query = document.objects.filter(
                        __get_searchset(i)).distinct()
            #Falls nicht erste Schleife
            else:
                #Wenn not nicht aktuell wirkend
                if not_active == False :
                    if i == "not":
                        not_active = True
                        continue
                
                #Wenn aktuell kein logischer Ausdruck aktiv
                if next_action == "none":
                    #Prüfe auf restliche Schlüsselwörter
                    if i == "and":
                        next_action = "and"
                    elif i == "or":
                        next_action = "or"
                    #Falls kein Schlüsselwort und keine logischer Ausdruck
                    #gemerkt führe normale "und"-Suche durch
                    else:
                        if not_active:
                            document_query = document_query.exclude(
                                    __get_searchset(i)).distinct()
                            not_active = False
                        else:
                            document_query = document_query.filter(
                                    __get_searchset(i)).distinct()

                #Falls ein logischer Ausdruck aktiv
                else:
                    #Wenn dieser Ausdruck "or" ist.
                    if next_action == "or":
                        #"or" wenn "not" aktiv
                        if not_active:
                            search_query = document.objects.exclude(
                                    __get_searchset(i)).distinct()
                            document_query = document_query | search_query
                            not_active = False
                        #"or" wenn "not" nicht aktiv
                        else:
                            search_query = document.objects.filter(
                                    __get_searchset(i)).distinct()
                            document_query = document_query | search_query
                        document_query = document_query.distinct()
                        next_action = "none"

                    if next_action == "and":
                        #"and" wenn "not" aktiv
                        if not_active:
                            document_query = document_query.exclude(
                                    __get_searchset(i)).distinct()
                            not_active = False
                        #"and" wenn "not" nicht aktiv
                        else:
                            document_query = document_query.filter(
                                    __get_searchset(i)).distinct()
                        next_action = "none"

        #Wenn das Ergebnis nur aus einem Dokument besteht, öffne die doc_detail
        if document_query.count()==1:
            return doc_detail(request, document_query[0].bib_no, searchtext)
        else:
            return __list(request, document_query,None, 0, searchtext)
        return __list(request, document_query)
    #Falls noch keine Suche gestartet wurde
    else:
        dict_response = get_dict_response(request)
        context = Context(dict_response)
        template = loader.get_template("search.html")
        return HttpResponse(template.render(context))

def __get_searchset(searchvalue):
    return (Q(title__icontains = searchvalue) |
            Q(authors__first_name__icontains = searchvalue) |
            Q(authors__last_name__icontains = searchvalue) |
            Q(isbn__icontains = searchvalue) |
            Q(bib_no__icontains = searchvalue) |
            Q(publisher__name__icontains = searchvalue) |
            Q(keywords__keyword__icontains = searchvalue))

def search_pro(request):
    """ Erweiterte Suche nach Dokumeten.
    Hier kann der Benutzer mit einer übersichtlichen Form nach Dokumenten
    suchen. Diese Suche soll auch dem Benutzer, der nicht mit Google umgehen
    kann die Möglichkeit geben ein Dokument spezifisch zu suchen und zu finden!
    """
    #Abfrage ob bereits eine Suche gestartet wurde
    if "title" in request.GET:
        #Auslesen der benötigten Variablen aus dem Request
        s_fn_author = request.GET.get('fn_author','')
        s_ln_author = request.GET.get('ln_author','nicht gefunden')
        s_fn_editor = request.GET.get('fn_editor','')
        s_ln_editor = request.GET.get('ln_editor','')
        s_title = request.GET.get('title','')
        s_year = request.GET.get('year','')
        s_publisher = request.GET.get('publisher','')
        s_bib_no = request.GET.get('bib_no','Test')
        s_isbn = request.GET.get('isbn','')
        s_keywords = request.GET.get('keywords','')
        s_doc_status = request.GET.get('doc_status','')
        #Verpackung in einer Liste zur einheitlichen Übergabe
        searchtext = [s_title, s_fn_author, s_ln_author, s_fn_editor,
                s_ln_editor, s_keywords, s_year, s_publisher, s_bib_no, s_isbn,
                s_doc_status]
        #Aufeinanderfolgendes Filtern nach Suchbegriffen
        #Aufgrund des Verfahrens eine UND-Suche
        s_documents = document.objects.filter(year__icontains = s_year)
        if s_title != "":
            title_query = s_title.split(" ")
            for i in title_query:
                s_documents = s_documents.filter(title__icontains = i)
        if s_fn_author != "":
            s_documents = s_documents.filter(authors__first_name__icontains =
                                             s_fn_author).filter(
                                             document_authors__editor=False)
        if s_ln_author != "":
            s_documents = s_documents.filter(authors__last_name__icontains =
                                             s_ln_author).filter(
                                             document_authors__editor=False)
        if s_fn_editor != "":
            s_documents = s_documents.filter(authors__first_name__icontains =
                                             s_fn_editor).filter(
                                             document_authors__editor=True)
        if s_ln_editor != "":
            s_documents = s_documents.filter(authors__last_name__icontains =
                                             s_ln_editor).filter(
                                             document_authors__editor=True)
        if s_publisher != "":
            s_documents = s_documents.filter(publisher__name__icontains = s_publisher)
        if s_bib_no != "":
            s_documents = s_documents.filter(bib_no__icontains = s_bib_no)
        if s_isbn != "":
            s_documents = s_documents.filter(isbn__icontains = s_isbn)
        if s_keywords != "":
            keyword_query = s_keywords.split(" ")
            for i in keyword_query:
                s_documents = s_documents.filter(keywords__keyword__icontains =
                                                i) 
        if s_doc_status !="":
            s_documents = s_documents.filter(doc_status__status =
                    s_doc_status,doc_status__return_lend = False) 
        s_documents = s_documents.distinct()
        #Wenn das Ergebnis nur aus einem Dokument besteht, öffne die doc_detail
        if s_documents.count()==1:
            return doc_detail(request, s_documents[0].bib_no, searchtext)
        else:
            return __list(request, s_documents, None, 0, searchtext)
    #Laden der Suchseite, falls noch keine Suche gestartet worden ist.
    else:
        dict_response = get_dict_response(request)
        dict_response['AVAILABLE'] = document.AVAILABLE
        dict_response[ "LEND"] = document.LEND
        dict_response["MISSING"] = document.MISSING
        dict_response["ORDERED"] = document.ORDERED
        dict_response["LOST"] = document.LOST
        return render_to_response("search_pro.html", context_instance=Context(dict_response))

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    """
    documents = document.objects.all()
    return __list(request, documents)

def doc_detail(request, bib_no_id, searchtext=""):
    """
    Gibt alle Informationen für die Dateilansicht eines Dokumentes zurück
    """
    v_user = request.user
    #ist das Dokument wirklich vorhanden, wenn ja wird es geladen
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    #selbst ausleihen, wenn Status vorhanden
    if 'lend' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    #zurückgeben
    if 'restitution' in request.POST and request.user.is_authenticated():
        document_query.unlend(v_user)
    #vermisst melden
    if 'missing' in request.POST and request.user.is_authenticated():
        document_query.missing(v_user)
       # thread.start_new_thread(
       #     __document_missing_email,  deaktiviert, um Spam vorzubeugen TODO
       #     (document_query, v_user)
       #     )
        
        
    #verloren melden
    if 'lost' in request.POST and request.user.is_authenticated():
        document_query.lost(v_user)
    #wiedergefunden melden
    if 'found' in request.POST and request.user.is_authenticated():
        document_query.lend(v_user)
    #aktualisieren des Datensatzes
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    #lädt den aktuellsten Statussatz - wenn keiner vorhanden: None
    try:
        lending_query = document_query.doc_status_set.latest('date')
    except doc_status.DoesNotExist:
        lending_query = None
    doc_extra_query = doc_extra.objects.filter(doc_id__bib_no__exact=bib_no_id)
    bibtex_string = Bibtex.export_doc(document_query)
    template = loader.get_template("doc_detail.html")
    #auslesen der für die doc_detail.html benötigten Rechte
    can_lend = v_user.has_perm('documents.can_lend')
    can_unlend = v_user.has_perm('documents.can_unlend')
    can_miss = v_user.has_perm('documents.can_miss')
    can_lost = v_user.has_perm('documents.can_lost')
    can_order = v_user.has_perm('documents.can_order')
    can_see_history = v_user.has_perm('documents.can_see_history')
    can_see_price = v_user.has_perm('documents.can_see_price')
    can_see_locn = v_user.has_perm('documents.can_see_locn')
    can_see_last_update = v_user.has_perm('documents.can_see_last_update_info')
    can_see_date_of_purchase = v_user.has_perm('documents.can_see_dop')
    can_see_export = v_user.has_perm('documents.can_see_export')
    change_document = v_user.has_perm('documents.change_document')
    history =__filter_history(document_query)
    keyword =__show_keywords(document_query)
    editoren =__diff_editors(document_query)
    autoren =__diff_authors(document_query)
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    #Finde heraus ob von einer Suche weitergeleitet wurde bzw. von welcher
    if len(searchtext) == 1:
        searchmode = 1
    elif len(searchtext) > 1:
        searchmode = 2
    else:
        searchmode = 0
    dict_response = get_dict_response(request)
    dict_response["documents"] = document_query
    dict_response["lending"] = lending_query
    dict_response["doc_extra"] = doc_extra_query
    dict_response["bibtex_string"] = bibtex_string
    dict_response["can_lend"] = can_lend
    dict_response["can_unlend"] = can_unlend
    dict_response["can_miss"] = can_miss
    dict_response["can_lost"] = can_lost
    dict_response["can_order"] = can_order
    dict_response["can_see_history"] = can_see_history
    dict_response["can_see_price"] = can_see_price
    dict_response["can_see_locn"] = can_see_locn
    dict_response["can_see_last_update"] = can_see_last_update
    dict_response["can_see_date_of_purchase"] = can_see_date_of_purchase
    dict_response["can_see_export"] = can_see_export
    dict_response["change_document"] = change_document
    dict_response["history"] = history
    dict_response["keyword"] = keyword
    dict_response["editoren"] = editoren
    dict_response["autoren"] = autoren
    dict_response["searchmode"] = searchmode
    dict_response["searchtext"] = searchtext
    context = Context(dict_response)

    response = HttpResponse(template.render(context))
    return response

def doc_assign(request, bib_no_id):
    v_user = request.user
    userform = SelectUser(v_user)
    nonuserform = NonUserForm()
    telnonuserform = TelNonUserForm()
    user_lend = ""
    try:
        document_query = document.objects.get(bib_no=bib_no_id)
    except document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.doc_status_set.latest('date')
    except doc_status.DoesNotExist:
        lending_query = None
    if 'assign' in request.POST and v_user.is_authenticated(): 
        userform = SelectUser(v_user, request.POST)
        if userform.is_valid():
            user_lend = userform.cleaned_data['users']
            if user_lend and not user_lend == "":
                document_query.lend(user=user_lend, editor=v_user)
                return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")
            
    elif 'assign-ex' in request.POST:
        nonuserform = NonUserForm(request.POST)
        telnonuserform = TelNonUserForm(request.POST)
        if nonuserform.is_valid() and telnonuserform.is_valid():
            non_user_lend = nonuserform.save()
            telnonuser, created = tel_non_user.objects.get_or_create(non_user=non_user_lend)
            telnonuserform = TelNonUserForm(request.POST, instance=telnonuser)
            telnonuserform.save()
            if non_user_lend and not non_user_lend == "":
                document_query.lend(user=v_user, non_user=non_user_lend)
                return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")

    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    template = loader.get_template("doc_assign.html")
    dict_response = get_dict_response(request)
    dict_response["documents"] = document_query
    dict_response["lending"] = lending_query
    dict_response["userform"] = userform
    dict_response["nonuserform"] = nonuserform
    dict_response["telnonuserform"] = telnonuserform
    context = Context(dict_response)
    response = HttpResponse(template.render(context))
    return response

def index(request): 
    context = Context(get_dict_response(request))
    return render_to_response("index.html",context_instance=context)

def docs_miss(request):
    """
    Vermisste Dokumente anzeigen
    """
    miss_query = document.objects.filter(doc_status__status = document.MISSING,        
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')  
    return __list(request, miss_query, form=2)
                              
@login_required

def profile(request, user_id):
    """View der Profilübersicht
    """

    v_user = request.user
    try:
        p_user = User.objects.get(id = user_id)
    except User.DoesNotExist :
        raise Http404
    see_groups = v_user.has_perm('documents.can_see_others_groups')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    dict_response = get_dict_response(request)
    if p_user.id == v_user.id :
        context = Context(dict_response)
        return render_to_response("profile.html", context_instance=context)
    else:
        dict_response["p_user"] = p_user
        dict_response["see_groups"] = see_groups
        context = Context(dict_response)
        return render_to_response("stranger_profile.html", context_instance=context)

@login_required
def profile_settings(request, user_id):
    """View der Accounteinstellung
    """ 
    c_user= User.objects.get(id = user_id)
    dict_response = get_dict_response(request)
    dict_response["c_user"] = c_user
    context = Context(dict_response)
    return render_to_response("profile_settings.html", context_instance=context)

@login_required
def personal(request):
    """Zum Editieren von Anschrift
    """
    profile, created = user_profile.objects.get_or_create(user_id=request.user)
    
    if request.method == "POST": 
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse("profile_edit_personal_done"))
    else:
        form = ProfileForm(instance=profile)
    
    template = "profile/personal.html"    
    data = { 'form': form, } 
    
    return render_to_response(template, data, context_instance=RequestContext(request))   

def telpersonal(request): 

    #tel, created = tel_user.objects.get_or_create(user=request.user)  
    
    if request.method == "POST": 
        telformset = modelformset_factory(tel_user, extra=3, max_num=3,\
                can_delete=True, exclude='user')
        formset = telformset(request.POST,\
                queryset=tel_user.objects.filter(user=request.user))
        if formset.is_valid():
            instances = formset.save(commit= False)
            for instance in instances:
                instance.user = request.user
                print instance
                instance.save()
            return HttpResponseRedirect(reverse("profile_edit_personal_done"))
    else: 
        telformset = modelformset_factory(tel_user, extra=3, max_num=3,\
                can_delete=True, exclude='user')
        formset = telformset(queryset=tel_user.objects.filter(user=request.user))
    template = "profile/tel.html"
    data = { 'formset': formset, }
    
    return render_to_response(template, data, context_instance=RequestContext(request)) 

def profile_edit_name(request):
    """
        Methode zum Ändern des eigenen Namens
    """
    v_user = request.user
    if request.method == "POST":
        form = NameForm(request.POST, instance=v_user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("profile_edit_personal_done"))
    else:
        form = NameForm(instance=v_user)
    template = "profile/name.html"
    data = { 'form' : form, }
    return render_to_response(template, data, 
                              context_instance=RequestContext(request))

def email_validation_process(request, key):

    if Emaireal-world or knuthlValidation.objects.verify(key=key): 
        successful = True
    else: 
        successful = False
    
    template = "account/email_validation_done.html"
    data = { 'successful': successful, }
    return render_to_response(template, data, context_instance=RequestContext(request))
     
               


def email_validation(request): 
    """
    Die Form für E-Mailaendern 
    """
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
def email_validation_reset(request): 
    
    try:
        resend = EmailValidation.objects.get(user=request.user).resend()
        response = "done"
    except EmailValidation.DoesNotExist: 
        response = "failed" 
    
    return HttpResponseRedirect(reverse("email_validation_reset_response", args=[response]))                   


def doc_import(request):
    """ BibTeX-Dateien importieren
    Hier kann der Benutzer mit den entsprechenden Rechten eine BibTeX-Datei
    hochladen und deren Inhalte der Datenbank hinzufügen.
    """
    success = True
    message = ""
    v_user = request.user
    if (not v_user.has_perm('documents.add_document') and not v_user.has_perm('documents.change_document') and not v_user.has_perm('documents.can_import')):
        raise PermissionDenied
    if len(request.FILES) > 0:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            date = datetime.datetime.today()
            filename = settings.DOCUMENTS_IMPORT_FILES + datetime.datetime.strftime(date, '%s') + '.bib'
            destination = open(filename, 'wb+')
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()
            Bibtex().do_import(filename)
            os.remove(filename)
            filesize = os.path.getsize(filename + '.err')
            if filesize == 0:
                message = 'Datei erfolgreich übernommen'
            else:
                errfile = open(filename + '.err', 'r')
                message = 'Datei konnte nicht vollständig übernommen werden \n\n '
                success = False
                for line in errfile:
                    message += line
                errfile.close()
            os.remove(filename + '.err')
    else :
        form = UploadFileForm()
    dict_response = get_dict_response(request)
    dict_response["form"] = form
    dict_response["message"] = message
    dict_response["success"] = success
    context = Context(dict_response)
    return render_to_response("file_import.html", context_instance=context)

@login_required
def doc_add(request, bib_no_id=None):
    """ Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies wird durch Formeingabe ermöglicht.
    """
    success = True
    v_user = request.user
    if (not v_user.has_perm('documents.add_document') and not v_user.has_perm('documents.change_document') and not v_user.has_perm('documents.can_import')):
        raise PermissionDenied
    #Web-Interface-Import
    if 'title' in request.POST:
        if bib_no_id is None:
            is_importform = True
            form_doc = DocForm(request.POST)
            extras_formset = modelformset_factory(doc_extra, extra=4,\
                can_delete=True, exclude='doc_id')
            form_extras = extras_formset(request.POST, queryset=doc_extra.objects.none())
            form_author = AuthorAddForm(request.POST)
            form_publisher = PublisherAddForm(request.POST)
        else :
            try :
                doc = document.objects.get(bib_no=bib_no_id)
            except document.DoesNotExist:
                raise Http404
            is_importform = False
            form_doc = DocForm(request.POST, instance=doc)
            extras_formset = modelformset_factory(doc_extra, extra=4,\
                can_delete=True, exclude='doc_id')
            form_extras = extras_formset(
                                    request.POST,
                                    queryset=doc_extra.objects.filter(doc_id=doc))
            form_author = AuthorAddForm(request.POST)
            form_publisher = PublisherAddForm(request.POST)
        success = False
        message = 'Fehler beim Import festgestellt: Daten sind im falschen Format'
        if u'sub_author' in request.POST and form_author.is_valid():
            form_author.save()
            message = 'Autor erfolgreich hinzugefügt'
            for item in form_doc.errors:
                form_doc.errors[item] = ''
            success = True
            form_author = AuthorAddForm()
        elif u'submit' in request.POST and request.POST[u'submit'] == u'Dokument speichern' and form_doc.is_valid():
            doc = form_doc.save(commit=False)
            doc.save()
            if form_extras.is_valid():
                instances = form_extras.save(commit=False)
                for instance in instances:
                    instance.doc_id=doc
                    instance.save()
                message = 'Daten erfolgreich übernommen'
            else :
                message = "Extra-Felder nicht valide"
            for editor in form_doc.cleaned_data['editors']:
                doc.add_editor(editor)
            for author in form_doc.cleaned_data['authors']:
                doc.add_author(author)
            doc.save()
            form_extras = extras_formset(
                                    queryset=doc_extra.objects.filter(doc_id=doc))
            if bib_no_id is None:
                form_doc = DocForm()
            else :
                return HttpResponseRedirect("/doc/%s/"%bib_no_id)
            form_author.errors['first_name'] = ''
            form_author.errors['last_name'] = ''
            success = True
        elif u'sub_publisher' in request.POST and form_publisher.is_valid():
            form_publisher.save()
            message = 'Publisher erfolgreich hinzugefügt'
            for item in form_publisher.errors:
                form_publisher.errors[item] = ''
            success = True
            form_publisher = PublisherAddForm()
            form_author.errors['first_name'] = ''
            form_author.errors['last_name'] = ''
            for item in form_doc.errors:
                form_doc.errors[item] = ''
    elif bib_no_id is None:
        is_importform = True
        message = ''
        form_doc = DocForm()
        extras_formset = modelformset_factory(doc_extra, extra=4,\
                can_delete=True, exclude='doc_id')
        form_extras = extras_formset(queryset=doc_extra.objects.none())
        form_author = AuthorAddForm()
        form_publisher = PublisherAddForm()
    else :
        message = ''
        try :
            doc = document.objects.get(bib_no=bib_no_id)
        except document.DoesNotExist:
            raise Http404
        is_importform = False
        form_doc = DocForm(instance=doc)
        extras_formset = modelformset_factory(doc_extra, extra=4,\
                can_delete=True, exclude='doc_id')
        form_extras = extras_formset(queryset=doc_extra.objects.filter(doc_id=doc))
        form_author = AuthorAddForm()
        form_publisher = PublisherAddForm()
# TODO
#    category_needs = category_need.objects.all()
    needs = dict()
#    for c in category_needs:
#        if (u""+c.category.name) not in needs:
#            needs[u"" + c.category.name] = []
#        needs[u"" + c.category.name].append(c.need)
    cat = category.objects.filter()
    dict_response = get_dict_response(request)
    dict_response["is_importform"] = is_importform
    dict_response["category"] = cat
    dict_response["form_doc"] = form_doc
    dict_response["form_extras"] = form_extras
    dict_response["form_author"] = form_author
    dict_response["form_publisher"] = form_publisher
    dict_response["message"] = message
    dict_response["success"] = success
    dict_response["category_needs"] = needs
    context = Context(dict_response)
    return render_to_response("doc_add.html", context_instance=context)

@login_required
def doc_rent(request):
    """ Des Benutzers Ausleihliste
    Alle Dokumente die der Benutzer ausgeliehen hat und die Dokumente für die
    der Benutzer für andere Bürgt.
    """
    v_user = request.user
    documents = document.objects.filter(doc_status__user_lend=v_user,
                                        doc_status__non_user_lend__isnull=True,
                                        doc_status__return_lend=False)
    documents_non_user = document.objects.filter(
                                        doc_status__user_lend=v_user,
                                        doc_status__non_user_lend__isnull=False,
                                        doc_status__return_lend=False)
    return __list(request, documents, documents_non_user, 1)

@login_required
def export(request):
    """Oberseite der Exporte. Die View lädt einfach das entsprechende Template
    unter Abfrage der für Navileiste benötigten Rechte
    """
    context = Context(get_dict_response(request))
    return render_to_response("export.html", context_instance=context)

@login_required
def allegro_export(request):
    """Seite um den Allegro-Export zu initiieren und für den Zugriff auf bisher
    erstellte Allegro Exporte.
    """
    hint = ''
    alg_exp = Allegro()
    if "allegro_export" in request.POST:
        alg_exp.start()
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."
    if alg_exp.isAlive():
        hint = "Derzeit läuft ein Export."
    elif not Allegro.docs_to_export:
        hint = "Keine Dokumente zum exportieren."
        Allegro.docs_to_export_lock.acquire()
        Allegro.docs_to_export = True
        Allegro.docs_to_export_lock.release()
    files = {}
    for file in os.listdir(settings.DOCUMENTS_SECDIR
            +settings.DOCUMENTS_ALLEGRO_FILES):
        if str(file).lower().endswith(".adt"):
            files[file] = __gen_sec_link(
                    "/"
                    +settings.DOCUMENTS_ALLEGRO_FILES
                    +file)

#    Snippet Code
    dict_response = get_dict_response(request)
    dict_response["files"] =files
    dict_response["hint"] = hint
    context = Context(dict_response)
    return render_to_response("allegro_export.html",
                              context_instance=context)

@login_required
def bibtex_export(request):
    """ Seite um den Datenbankexport in BibTeX zu initiieren und für den
    Zugriff auf bisher exportierte BibTeX-Exporte.
    TODO: Zugriff nur auf Benutzer beschränken, die Dokumente hinzufügen
    dürfen.
    """
    hint = ''
    if Bibtex.bibtex_lock.locked():
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."
    elif "bibtex_export" in request.POST:
        export_documents = document.objects.filter(
                bib_date__isnull=True,
                )
        Bibtex().export_data(
                export_documents,
                settings.DOCUMENTS_SECDIR+settings.DOCUMENTS_BIBTEX_FILES
                ).start()
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."

    files = {}
    for file in os.listdir(settings.DOCUMENTS_SECDIR
            +settings.DOCUMENTS_BIBTEX_FILES):
        if ".bib" in file:
            files[file] = __gen_sec_link(
                    "/"
                    +settings.DOCUMENTS_BIBTEX_FILES
                    +file
                    )

#    Snippet Code
    dict_response = get_dict_response(request)
    dict_response["files"] =files
    dict_response["hint"] = hint
    context = Context(dict_response)
    return render_to_response("bibtex_export.html", context_instance=context)

@login_required
def user(request):
    lend_documents = document.objects.filter(
            doc_status__return_lend__exact = False,
            doc_status__user_lend__exact = request.user,
            doc_status__non_user_lend__exact = None)
    return __list(request, lend_documents)

def __list(request, documents, documents_non_user=None, form=0, searchtext=""):
    """ Erzeugt eine Liste vom Typ "form".
        0 = Literaturverzeichnis oder Suchergebnis
        1 = Ausleihe
        2 = Vermisst
    """
    documents = __filter_names(documents, request)
    sort = request.GET.get('sort')
    path_sort = __truncate_get(request, 'sort') + u'&sort='
    params_sort = {}
    if form == 2:
        params_sort[u'Datum'] = path_sort
        if sort == u'date':
            params_sort[u'Datum'] += u'-'
        params_sort[u'Datum'] += u'date'

    params_sort[u'Dokumententitel'] = path_sort
    if sort == u'title':
        params_sort[u'Dokumententitel'] += u'-'
    params_sort[u'Dokumententitel'] += u'title'

    params_sort[u'Autoren'] = path_sort
    if u'authors' == sort:
        params_sort[u'Autoren'] += u'-'
    params_sort[u'Autoren'] += u'authors'

    params_sort[u'Veröffentlichung'] = path_sort
    if sort == u'year':
        params_sort[u'Veröffentlichung'] += u'-'
    params_sort[u'Veröffentlichung'] += u'year'


    if sort is not None:
        if sort == "date":
            documents = documents.order_by("-doc_status__date")
        elif sort == "-date":
            documents = documents.order_by("doc_status__date")
        else:
            documents = documents.order_by(sort)
    miss_query = None 
    # options für Filter-Dropdown
    startswith_filter = {
        'all': ['value=all', 'Alle'],
        '0-9': ['value=0-9', '0-9'],
        'a-c': ['value=a-c', 'A-C'],
        'd-f': ['value=d-f', 'D-F'],
        'g-i': ['value=g-i', 'G-I'],
        'j-k': ['value=j-k', 'J-K'],
        'm-o': ['value=m-o', 'M-O'],
        'p-s': ['value=p-s', 'P-S'],
        't-v': ['value=t-v', 'T-V'],
        'w-z': ['value=w-z', 'W-Z'],
        'special_sign': ['value=special_sign', 'Sonderzeichen'],
        }
    selected_filter = request.GET.get('starts', default='all')
    startswith_filter[selected_filter][0] += ' selected=selected'
    if form != 2:
        miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                             doc_status__return_lend = False)
        miss_query = miss_query.order_by('-doc_status__date')
    params_starts = __truncate_get(request, 'starts', 'page')
    dict_response = get_dict_response(request)
    dict_response["documents"] = documents
    dict_response["settings"] = settings
    dict_response["path_sort"] = params_sort
    dict_response["path_starts"] = params_starts
    dict_response["form"] = form
    dict_response["filter"] = startswith_filter
    if form == 1:
        return render_to_response(
                "doc_rent.html", 
                dict_response, 
                context_instance=RequestContext(request))
    if form == 2:
        return render_to_response(
                "missing.html",
                dict_response,
                context_instance=RequestContext(request))
    #Finde heraus ob von einer Suche weitergeleitet wurde bzw. von welcher
    if len(searchtext) == 1:
        searchmode = 1
    elif len(searchtext) > 1:
        searchmode = 2
    else:
        searchmode = 0
    dict_response["searchtext"] = searchtext
    dict_response["searchmode"] = searchmode
    return render_to_response(
            "doc_list_wrapper.html", 
            dict_response,
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
    
    if sw == "special_sign":
        documents = documents.exclude(
                         Q(title__iregex='[A-Za-z]'))
    elif sw == "0-9":
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

def __gen_sec_link(path):
    import time, hashlib
    secret = settings.SECRET_KEY
    uri_prefix = '/dl/'
    hextime = "%08x" % time.time()
    token = hashlib.md5(secret + path + hextime).hexdigest()
    return '%s%s/%s%s' % (uri_prefix, token, hextime, path)
    
def __filter_history(doc):
    new_history = doc.doc_status_set.order_by('-date')[0:10]
    return new_history
    
def __document_missing_email(document, user):
    email = emails.objects.get(name = "Vermisst Gemeldet")
    plaintext = Template(email.text)
    member = User.objects.values_list('email', flat=True)
   # member = ('zapdoshameyer@web.de', 'tim3out@arcor.de')
    c = Context({"document_name" : document.title,
                     "user_name" : user.first_name,
               })
    subject, from_email, to, bcc = ('[WiReLib] Vermisstmeldung', 
                                    'j.hameyer@tu-bs.de',
                                    'j.hameyer@tu-bs.de', #TODO
                                    member
                                    )
    text_content = plaintext.render(c)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to], bcc)
    msg.send()
    

def __document_expired_email(day_amount):
    current_day = datetime.date.today() 
    expired_docs = doc_status.objects.filter(
                  return_lend=False,
                  date_term_lend__exact=current_day + datetime.timedelta(day_amount))
                  
    
    #Vorbereiten der 2 Emails, öffnen der Verbindung                                           
    user_email = emails.objects.get(name = "Frist Erinnerungsemail(B)")
    nonuser_email = emails.object.get(name = "Frist Erinnerungsemail(E)")
    user_plaintext = Template(user_email.text)
    nonuser_plaintext = Template(nonuser_email.text)
    connection = mail.get_connection()
    connection.open()
    
    for entry in expired_docs:
       __send_expired_mail(
                           receiver=entry.user_lend.email,
                           subject=user_email.subject,
                           emailcontent=user_plaintext, 
                           connection=connection, 
                           user_name=entry.user_lend.username, 
                           document_name=entry.doc_id.title,
                           nonuser_firstname=entry.non_user_lend.firstname, 
                           nonuser_lastname=entry.non_user_lend.lastname
                          )
       __send_expired_mail(
                           receiver=entry.non_user_lend.email,
                           subject=nonuser_email.subject,
                           emailcontent=nonuser_plaintext,
                           connection=connection,
                           user_name=entry.user_lend.username, 
                           document_name=entry.doc_id.title,
                           nonuser_firstname=entry.non_user_lend.firstname, 
                           nonuser_lastname=entry.non_user_lend.lastname
                          )
    connection.close() 

def __send_expired_mail(receiver, subject, emailcontent, connection, **context):
    c = Context(context)
    text_content = emailcontent.render(c)                    
    finalemail = mail.EmailMessage(subject, 
                                   text_content, 
                                   'j.hameyer@tu-bs.de', #TODO
                                   [receiver], 
                                   connection=connection
                                   )       
    finalemail.send()             

def __show_keywords(doc):
    keywords = doc.keywords_set.order_by('-keyword').exclude(keyword__iexact="") 
    return keywords 
    
def __diff_authors(doc):
    autoren = doc.document_authors_set.order_by('-author').exclude(editor=True)       
    return autoren    

def __diff_editors(doc):
   editoren = doc.document_authors_set.order_by('-author').exclude(editor=False)       
   return editoren      

