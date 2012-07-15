# vim: set fileencoding=utf-8
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template import RequestContext, Template 
from documents.models import document, doc_status, doc_extra, category,\
    EmailValidation, category_need, emails, user_profile, tel_user
from django.contrib.auth.models import User
from documents.extras_bibtex import Bibtex
from documents.extras_allegro import Allegro
from documents.forms import EmailValidationForm, UploadFileForm, DocForm, \
    AuthorAddForm, SelectUser, NonUserForm, ProfileForm, TelForm 
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q
import datetime
import os
import settings
import thread


def search(request):
    """ Suche nach Dokumenten.
    Hier kann der Benutzer Dokumente suchen, finden und Überraschungseier
    finden.
    """
    #Wenn bereits eine Suche gestartet wurde
    if "query" in request.GET:
        #Eingabe des Users aus dem request auslesen
        suchtext = request.GET.get('query','')
        #Erstellen eines Sets aus allen Suchbegriffen.
        #Aufgrund des Verfahrens eine ODER-Suche
        suchtext_gesplittet = suchtext.split(" ")
        first_for = True
        next_action = "none"
        not_active = False
        for i in suchtext_gesplittet:
            if first_for:
                first_for = False
                search_set = (
                    Q(title__icontains = i) |
                    Q(authors__last_name__icontains = i) |
                    Q(isbn__icontains = i) |
                    Q(bib_no__icontains = i) |
                    Q(publisher__name__icontains = i) |
                    Q(keywords__keyword__icontains = i))
                document_query = document.objects.filter(search_set).distinct()
            else:
                if not_active == False :
                    if i == "not":
                        not_active = True

                if next_action == "none":
                    if i == "and":
                        next_action = "and"
                    elif i == "or":
                        next_action = "or"
                    else:
                        search_set = (
                            Q(title__icontains = i) |
                            Q(authors__last_name__icontains = i) |
                            Q(isbn__icontains = i) |
                            Q(bib_no__icontains = i) |
                            Q(publisher__name__icontains = i) |
                            Q(keywords__keyword__icontains = i))
                        document_query = document_query.filter(search_set).distinct()

                else:
                    if next_action == "or":
                        if not_active:
                            search_set = (
                                Q(title__icontains = i) |
                                Q(authors__last_name__icontains = i) |
                                Q(isbn__icontains = i) |
                                Q(bib_no__icontains = i) |
                                Q(publisher__name__icontains = i) |
                                Q(keywords__keyword__icontains = i))
                            search_query = not document.objects.filter(search_set).distinct() & document.objects.all
                            document_query = document_query | search_query
                        else:
                            search_set = (
                                Q(title__icontains = i) |
                                Q(authors__last_name__icontains = i) |
                                Q(isbn__icontains = i) |
                                Q(bib_no__icontains = i) |
                                Q(publisher__name__icontains = i) |
                                Q(keywords__keyword__icontains = i))
                            search_query = document.objects.filter(search_set).distinct()
                            document_query = document_query | search_query
                        document_query = document_query.distinct()
                        next_action = "none"

                    if next_action == "and":
                        search_set = (
                            Q(title__icontains = i) |
                            Q(authors__last_name__icontains = i) |
                            Q(isbn__icontains = i) |
                            Q(bib_no__icontains = i) |
                            Q(publisher__name__icontains = i) |
                            Q(keywords__keyword__icontains = i))
                        document_query = document_query.filter(search_set).distinct()
                        next_action = "none"

        #Wenn das Ergebnis nur aus einem Dokument besteht, öffne die doc_detail
        if document_query.count()==1:
            return doc_detail(request, document_query[0].bib_no)
        else:
            return __list(request, document_query)
        return __list(request, document_query)
    #Falls noch keine Suche gestartet wurde
    else:
        v_user = request.user
        import_perm = v_user.has_perm('documents.can_import')
        export_perm = v_user.has_perm('documents.can_export')
        perms =  v_user.has_perm('documents.can_see_admin')
        context = Context({"user" : v_user, 
                           "perm" : perms,
                           "import_perm" : import_perm,
                           "export_perm" : export_perm})
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
        s_fn_author = request.GET.get('fn_author','')
        s_ln_author = request.GET.get('ln_author','')
        s_title = request.GET.get('title','')
        s_year = request.GET.get('year','')
        s_publisher = request.GET.get('publisher','')
        s_bib_no = request.GET.get('bib_no','Test')
        s_isbn = request.GET.get('isbn','')
        s_keywords = request.GET.get('keywords','')
        s_doc_status = request.GET.get('doc_status','')
        #Aufeinanderfolgendes Filtern nach Suchbegriffen
        #Aufgrund des Verfahrens eine UND-Suche
        s_documents = document.objects.filter(year__icontains = s_year)
        if s_title != "":
            title_query = s_title.split(" ")
            for i in title_query:
                s_documents = s_documents.filter(title__icontains = i)
        if s_fn_author != "":
            s_documents = s_documents.filter(authors__first_name__icontains =
                                             s_fn_author)
        if s_ln_author != "":
            s_documents = s_documents.filter(authors__last_name__icontains =
                                             s_ln_author)
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
        #Wenn das Ergebnis nur aus einem Dokument besteht, öffne die doc_detail
        if s_documents.count()==1:
            return doc_detail(request, s_documents[0].bib_no)
        else:
            return __list(request, s_documents)
    #Laden der Suchseite, falls noch keine Suche gestartet worden ist.
    else:
        v_user = request.user
        perms =  v_user.has_perm('documents.can_see_admin')
        import_perm = v_user.has_perm('documents.can_import')
        export_perm = v_user.has_perm('documents.can_export')
        miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                             doc_status__return_lend = False)
        miss_query = miss_query.order_by('-doc_status__date')
        return render_to_response("search_pro.html",
                                  context_instance=Context(
                                               {"user" : v_user, 
                                                "perm" : perms, 
                                                "import_perm" : import_perm,
                                                "export_perm" : export_perm, 
                                                "miss" : miss_query[0:10],
                                                "AVAILABLE" : document.AVAILABLE,
                                                "LEND" : document.LEND,
                                                "MISSING" : document.MISSING,
                                                "ORDERED" : document.ORDERED,
                                                "LOST" : document.LOST}))

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    """
    documents = document.objects.all()
    return __list(request, documents)

def doc_detail(request, bib_no_id):
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
        thread.start_new_thread(
            __document_missing_email,
            (document_query, v_user)
            )
        
        
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
    perms =  v_user.has_perm('documents.can_see_admin')
    can_lend = v_user.has_perm('documents.can_lend')
    can_unlend = v_user.has_perm('documents.can_unlend')
    can_miss = v_user.has_perm('documents.can_miss')
    can_lost = v_user.has_perm('documents.can_lost')
    can_order = v_user.has_perm('documents.can_order')
    can_see_history = v_user.has_perm('documents.can_see_history')
    can_see_price = v_user.has_perm('documents.can_see_price')
    can_see_locn = v_user.has_perm('documents.can_see_locn')
    can_see_last_update = v_user.has_perm('documents.can_see_last_update_info')
    can_see_date_of_purchase = v_user.has_perm('documents.can_see_date_of_purchase')
    can_see_export = v_user.has_perm('documents.can_see_export')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    change_document = v_user.has_perm('documents.change_document')
    history =__filter_history(document_query)
    keyword =__show_keywords(document_query)
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    
    context = Context({"documents" : document_query,
                      "lending" : lending_query,
                      "doc_extra" : doc_extra_query,
                      "bibtex_string" : bibtex_string,
                      "user" : v_user,
                      "perm" : perms,
                      "can_lend" : can_lend,
                      "can_unlend" : can_unlend,
                      "can_miss" : can_miss,
                      "can_lost" : can_lost,
                      "can_order" : can_order,
                      "can_see_history" : can_see_history,
                      "can_see_price" : can_see_price,
                      "can_see_locn" : can_see_locn,
                      "can_see_last_update" : can_see_last_update,
                      "can_see_date_of_purchase" : can_see_date_of_purchase,
                      "can_see_export" : can_see_export,
                      "export_perm" : export_perm,
                      "import_perm" : import_perm,
                      "change_document" : change_document,
                      "miss" : miss_query[0:10],
                      "history" : history ,
                      "keyword" : keyword })
    response = HttpResponse(template.render(context))
    return response

def doc_assign(request, bib_no_id):
    v_user = request.user
    userform = SelectUser(v_user)
    nonuserform = NonUserForm()
    user_lend = ""
    message = 'test'
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
            #print userform.fields['users']
                return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")
            
    elif 'assign-ex' in request.POST:
        nonuserform = NonUserForm(request.POST)
        if nonuserform.is_valid():
            nonuserform.save()
            # TODO :Buch soll auf Bürgen entliehen bleiben?
            # wo wird der Bürge gespeichert?
            # Anzeige wer entliehen hat
            return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")

    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    template = loader.get_template("doc_assign.html")
    context = Context({"documents" : document_query, 
                       "user" : v_user,
                       "lending" : lending_query, 
                       "userform": userform,
                       "nonuserform" : nonuserform,
                       "message" : message,
                       "perm" : perms, 
                       "import_perm" : import_perm,
                       "export_perm" : export_perm,
                       "miss" : miss_query[0:10]})
    response = HttpResponse(template.render(context))
    return response

def index(request): 
    v_user = request.user
    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return render_to_response("index.html",
                              context_instance=Context(
                                               {"user" : v_user, 
                                                "perm" : perms, 
                                                "import_perm" : import_perm,
                                                "export_perm" : export_perm,
                                                "miss" : miss_query[0:10]}))

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
        #TODO :Richtige Exception einbauen. User.DoesNotExist funktioniert
        #nicht.
    except "User existiert nicht":
        raise Http404
    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    see_groups = v_user.has_perm('documents.can_see_others_groups')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    if p_user.id == v_user.id :
        return render_to_response("profile.html",context_instance=Context({"user" :
                              v_user, "perm" : perms, "import_perm" : import_perm,
                              "export_perm" : export_perm, "miss" : miss_query[0:10]}))
    else:
        return render_to_response("stranger_profile.html",
                                  context_instance=Context({"user" :v_user, 
                                                            "p_user" : p_user,
                                                            "perm" : perms, 
                                                            "import_perm" : import_perm,
                                                            "export_perm" : export_perm, 
                                                            "see_groups" : see_groups,
                                                            "miss" : miss_query[0:10]}))

@login_required
def profile_settings(request, user_id):
    """View der Accounteinstellung
    """ 

    v_user = request.user
    c_user= User.objects.get(id = user_id)
    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return render_to_response("profile_settings.html",
                              context_instance=Context(
                                               {"user" : v_user,
                                                "c_user" : c_user,  
                                                "perm" : perms, 
                                                "import_perm" : import_perm,
                                                "export_perm" : export_perm, 
                                                "miss" : miss_query[0:10]}))
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

    tel, created = tel_user.objects.get_or_create(user=request.user)  
    
    if request.method == "POST": 
        form = TelForm(request.POST, instance=tel)
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse("profile_edit_personal_done"))
    else: 
        form = TelForm(instance=tel)
    template = "profile/tel.html"
    data = { 'form': form, }
    
    return render_to_response(template, data, context_instance=RequestContext(request)) 



def email_validation_process(request, key):

    if EmailValidation.objects.verify(key=key): 
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


@login_required
def doc_add(request, bib_no_id=None):
    """ Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies kann auf folgende Arten geschehen:
        * Import durch Formeingabe
        * Import durch Upload einer BibTeX-Datei
    """
    #TODO Rechtekontrolle
    success = True
    v_user = request.user
    #Datei-Import
    if len(request.FILES) > 0:
        form_doc = DocForm()
        form_author = AuthorAddForm()
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            date = datetime.datetime.today()
            filename = 'imports/' + datetime.datetime.strftime(date, '%s') + '.bib'
            destination = open(filename, 'wb+')
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()
            Bibtex.do_import(filename)
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
    #Web-Interface-Import
    elif 'title' in request.POST:
        if bib_no_id is None:
            form = UploadFileForm()
            form_doc = DocForm(request.POST)
            form_author = AuthorAddForm(request.POST)
        else:
            try:
                doc = document.objects.get(bib_no=bib_no_id)
            except document.DoesNotExist:
                raise Http404
            form = None
            form_doc = DocForm(request.POST, instance=doc)
            form_author = AuthorAddForm(request.POST)
        success = False
        message = 'Fehler beim Import festgestellt: Daten sind im falschen Format'
        if request.POST['submit'] == 'Autor hinzufügen' and form_author.is_valid():
            form_author.save()
            message = 'Autor erfolgreich hinzugefügt'
            success = True
            form_author = AuthorAddForm()
        elif request.POST['submit'] == 'Dokument speichern' and form_doc.is_valid():
            doc = form_doc.save(commit=False)
            doc.save()
            for editor in form_doc.cleaned_data['editors']:
                doc.add_editor(editor)
            for author in form_doc.cleaned_data['authors']:
                doc.add_author(author)
            doc.save()
            form_author.errors['first_name'] = ''
            form_author.errors['last_name'] = ''
            message = 'Daten erfolgreich übernommen'
            success = True
    elif bib_no_id is None:
        message = ''
        form_doc = DocForm()
        form_author = AuthorAddForm()
        form = UploadFileForm()
    else:
        message = ''
        try:
            doc = document.objects.get(bib_no=bib_no_id)
        except document.DoesNotExist:
            raise Http404
        form_doc = DocForm(instance=doc)
        form_author = AuthorAddForm()
        form = None
    category_needs = category_need.objects.all()
    needs = dict()
    for c in category_needs:
        if (u""+c.category.name) not in needs:
            needs[u"" + c.category.name] = []
        needs[u"" + c.category.name].append(c.need)
    perms = v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    cat = category.objects.filter()
    return render_to_response("doc_add.html",
                              context_instance=Context(
                                  {"user" : v_user, 
                                   "perm" : perms,
                                   "import_perm" : import_perm,
                                   "export_perm" : export_perm,
                                   "category" : cat,
                                   "form" : form,
                                   "form_doc" : form_doc,
                                   "form_author" : form_author,
                                   "message" : message,
                                   "success" : success,
                                   "miss" : miss_query[0:10],
                                   "category_needs" : needs}))

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
    #documents = document.objects.filter(
    #        doc_status__user_lend=v_user).filter(
    #        doc_status__non_user_lend__isnull=True).filter(
    #        doc_status__return_lend=False)
    documents_non_user = document.objects.filter(
                                        doc_status__user_lend=v_user,
                                        doc_status__non_user_lend__isnull=False,
                                        doc_status__return_lend=False)
    #documents_non_user = document.objects.filter(
    #        doc_status__user_lend=v_user).filter(
    #        doc_status__non_user_lend__isnull=False).filter(
    #        doc_status__return_lend=False)
    return __list(request, documents, documents_non_user, 1)

@login_required
def export(request):
    """Oberseite der Exporte. Die View lädt einfach das entsprechende Template
    unter Abfrage der für Navileiste benötigten Rechte
    """
    v_user = request.user
    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return render_to_response("export.html",
                              context_instance=Context(
                                        {"user" : v_user, 
                                         "perm" : perms, 
                                         "import_perm" : import_perm,
                                         "export_perm" : export_perm, 
                                         "miss" : miss_query[0:10]}))

@login_required
def allegro_export(request):
    """Seite um den Allegro-Export zu initiieren und für den Zugriff auf bisher
    erstellte Allegro Exporte.
    """
    hint = ''
    alg_exp = Allegro()
    if "allegro_export" in request.POST:
        alg_exp.start()
        alg_exp.join()
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."
    if alg_exp.isAlive():
        hint = "Derzeit läuft ein Export."
    elif not Allegro.docs_to_export:
        hint = "Keine Dokumente zum exportieren."
        Allegro.docs_to_export_lock.acquire()
        Allegro.docs_to_export = True
        Allegro.docs_to_export_lock.release()
    files = {}
    for file in os.listdir(settings.DOCUMENTS_ALLEGRO_FILES):
        if ".adt" in file:
            files[file] = __gen_sec_link("/"+file)

#    Rechte für Template
    v_user = request.user
#    Snippet Code
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    perms =  v_user.has_perm('documents.can_see_admin')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return render_to_response("allegro_export.html",
                              context_instance=Context(
                                    {"user" : v_user, 
                                     "perm" : perms, 
                                     "import_perm" : import_perm,
                                     "export_perm" : export_perm, 
                                     "miss" : miss_query[0:10],
                                     "files" :files,
                                     "hint" : hint,
                                     }))

@login_required
def bibtex_export(request):
    """ Seite um den Datenbankexport in BibTeX zu initiieren und für den
    Zugriff auf bisher exportierte BibTeX-Exporte.
    TODO: Zugriff nur auf Benutzer beschränken, die Dokumente hinzufügen
    dürfen.
    """
    hint = ''
    print "Es ist %s" % Bibtex.bibtex_lock.locked()
    if Bibtex.bibtex_lock.locked():
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."
        print hint
    elif "bibtex_export" in request.POST:
        export_documents = document.objects.filter(
                bib_date__isnull=True,
                )
        Bibtex().export_data(
                export_documents,
                settings.DOCUMENTS_BIBTEX_FILES
                ).start()
        hint = "Der Export läuft. Bitte besuchen sie uns in ein paar Minuten wieder."

    files = {}
    for file in os.listdir(settings.DOCUMENTS_BIBTEX_FILES):
        if ".bib" in file:
            files[file] = __gen_sec_link("/"+file)

#    Rechte für Template
    v_user = request.user
#    Snippet Code
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    perms =  v_user.has_perm('documents.can_see_admin')
    miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                         doc_status__return_lend = False)
    miss_query = miss_query.order_by('-doc_status__date')
    return render_to_response("bibtex_export.html",
                              context_instance=Context(
                                    {"user" : v_user, 
                                     "perm" : perms, 
                                     "import_perm" : import_perm,
                                     "export_perm" : export_perm, 
                                     "miss" : miss_query[0:10],
                                     "files" :files,
                                     "hint" : hint,
                                     }))

@login_required
def user(request):
    lend_documents = document.objects.filter(
            doc_status__return_lend__exact = False,
            doc_status__user_lend__exact = request.user,
            doc_status__non_user_lend__exact = None)
    return __list(request, lend_documents)

def __list(request, documents, documents_non_user=None, form=0):
    """ Erzeugt eine Liste vom Typ "form".
        0 = Literaturverzeichnis oder Suchergebnis
        1 = Ausleihe
        2 = Vermisst
    """
    v_user = request.user
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
    perms =  v_user.has_perm('documents.can_see_admin')
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    miss_query = None
    if form != 2:
        miss_query = document.objects.filter(doc_status__status = document.MISSING,
                                             doc_status__return_lend = False)
        miss_query = miss_query.order_by('-doc_status__date')
    params_starts = __truncate_get(request, 'starts', 'page')
    if form == 1:
        return render_to_response("doc_rent.html", 
                dict(documents = documents,
                    documents_non_user = documents_non_user,
                    user = v_user, 
                    settings = settings, 
                    perm = perms,
                    import_perm = import_perm,
                    export_perm = export_perm,
                    path_sort = params_sort, 
                    path_starts = params_starts,
                    form = form,
                    miss = miss_query[0:10]),
                context_instance=RequestContext(request))
    if form == 2:
        return render_to_response("missing.html",
                dict(documents = documents,
                     user = v_user,
                     settings = settings,
                     perm = perms,
                     import_perm = import_perm,
                     export_perm = export_perm,
                     path_sort = params_sort,
                     path_starts = params_starts,
                     form = form),
                 context_instance=RequestContext(request))
    return render_to_response("doc_list_wrapper.html", 
            dict(documents = documents,
                user = v_user, 
                settings = settings, 
                perm = perms,
                import_perm = import_perm,
                export_perm = export_perm,
                path_sort = params_sort, 
                path_starts = params_starts,
                form = form,
                miss = miss_query[0:10]),
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
    
    if sw == "Sonderzeichen":
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
    staffmember = User.objects.values_list('email', flat=True)
    #staffmember = ('zapdoshameyer@web.de', 'tim3out@arcor.de')
    c = Context({"document_name" : document.title,
                     "user_name" : user.first_name,
                     "user_email" : "" })
    subject, from_email, to, bcc = ('[WiReLib] Vermisstmeldung', 
                                    'j.hameyer@tu-bs.de',
                                    'j.hameyer@tu-bs.de', 
                                    staffmember
                                    )
    text_content = plaintext.render(c)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to], bcc)
    msg.send()
    
def __show_keywords(doc):
    keywords = doc.keywords_set.order_by('keyword')
    return keywords 
