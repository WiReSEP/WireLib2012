#vim: set fileencoding=utf-8

import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import QueryDict
from lib_views import _get_dict_response
import lib_views as lib_views
from documents.models import Document

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

def _list(request, documents, documents_non_user=None, form=0, searchtext=""):
    """ Erzeugt eine Liste vom Typ "form".
        0 = Literaturverzeichnis oder Suchergebnis
        1 = Ausleihe
        2 = Vermisst
    """
    documents = lib_views._filter_names(documents, request)
    sort = request.GET.get('sort')
    path_sort = _truncate_get(request, 'sort') + u'&sort='
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
            documents = documents.order_by("-docstatus__date")
        elif sort == "-date":
            documents = documents.order_by("docstatus__date")
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
        miss_query = Document.objects.filter(docstatus__status = Document.MISSING,
                                             docstatus__return_lend = False)
        miss_query = miss_query.order_by('-docstatus__date')
    params_starts = _truncate_get(request, 'starts', 'page')
    dict_response = _get_dict_response(request)
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

def _truncate_get(request, *var):
    """Entfernt GET-Parameter
    Diese Methode entfernt die angegebenen GET-Parameter und gibt die neu
    geformten Parameter als String zurück
    """
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
