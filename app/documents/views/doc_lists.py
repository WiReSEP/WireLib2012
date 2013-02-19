#vim: set fileencoding=utf-8

from django.contrib.auth.decorators import login_required

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
                document_query = Document.objects.filter(
                                lib_views._get_searchset(i)).distinct()
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
                                            lib_views._get_searchset(i)).distinct()
                            not_active = False
                        else:
                            document_query = document_query.filter(
                                            lib_views._get_searchset(i)).distinct()

                #Falls ein logischer Ausdruck aktiv
                else:
                    #Wenn dieser Ausdruck "or" ist.
                    if next_action == "or":
                        #"or" wenn "not" aktiv
                        if not_active:
                            search_query = Document.objects.exclude(
                                            lib_views._get_searchset(i)).distinct()
                            document_query = document_query | search_query
                            not_active = False
                        #"or" wenn "not" nicht aktiv
                        else:
                            search_query = Document.objects.filter(
                                        lib_views._get_searchset(i)).distinct()
                            document_query = document_query | search_query
                        document_query = document_query.distinct()
                        next_action = "none"

                    if next_action == "and":
                        #"and" wenn "not" aktiv
                        if not_active:
                            document_query = document_query.exclude(
                                            lib_views._get_searchset(i)).distinct()
                            not_active = False
                        #"and" wenn "not" nicht aktiv
                        else:
                            document_query = document_query.filter(
                                            lib_views._get_searchset(i)).distinct()
                        next_action = "none"

        #Wenn das Ergebnis nur aus einem Dokument besteht, öffne die doc_detail
        if document_query.count()==1:
            return doc_detail(request, document_query[0].bib_no, searchtext)
        else:
            return _list(request, document_query,None, 0, searchtext)
        return _list(request, document_query)
    #Falls noch keine Suche gestartet wurde
    else:
        return doc_list(request)
#        dict_response = _get_dict_response(request)
#        context = Context(dict_response)
#        template = loader.get_template("search.html")
#        return HttpResponse(template.render(context))

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
        s_documents = Document.objects.filter(year__icontains = s_year)
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
            return _list(request, s_documents, None, 0, searchtext)
    #Laden der Suchseite, falls noch keine Suche gestartet worden ist.
    else:
        dict_response = _get_dict_response(request)
        dict_response['AVAILABLE'] = Document.AVAILABLE
        dict_response[ "LEND"] = Document.LEND
        dict_response["MISSING"] = Document.MISSING
        dict_response["ORDERED"] = Document.ORDERED
        dict_response["LOST"] = Document.LOST
        return render_to_response("search_pro.html", context_instance=Context(dict_response))

def doc_list(request):
    """ Übersicht über alle enthaltenen Dokumente
    """
    documents = Document.objects.all()
    return _list(request, documents, searchtext=[""])

@login_required
def doc_rent(request):
    """ Des Benutzers Ausleihliste
    Alle Dokumente die der Benutzer ausgeliehen hat und die Dokumente für die
    der Benutzer für andere Bürgt.
    """
    v_user = request.user
    documents = Document.objects.filter(docstatus__user_lend=v_user,
                                        docstatus__non_user_lend__isnull=True,
                                        docstatus__return_lend=False)
    documents_non_user = Document.objects.filter(
                                        docstatus__user_lend=v_user,
                                        docstatus__non_user_lend__isnull=False,
                                        docstatus__return_lend=False)
    return _list(request, documents, documents_non_user, 1)
