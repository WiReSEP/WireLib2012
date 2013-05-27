#vim: set fileencoding=utf-8

import settings
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import QueryDict
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ValidationError
from lib_views import _get_dict_response
import lib_views as lib_views
from documents.models import Document
from documents.forms import SearchForm, SearchProBaseForm, SearchProExtendedForm

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
    return _list(request, documents, documents_non_user, Document.LEND)

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
    startswith_filter = (
        [u'value=all', 'Alle'],
        [u'value=0-9', '0-9'],
        [u'value=äa-c', 'A-C'],
        [u'value=d-f', 'D-F'],
        [u'value=g-i', 'G-I'],
        [u'value=j-k', 'J-K'],
        [u'value=öm-o', 'M-O'],
        [u'value=ßp-s', 'P-S'],
        [u'value=üt-v', 'T-V'],
        [u'value=w-z', 'W-Z'],
        [u'value=special_sign', 'Sonderzeichen'],
        )
    selected_filter = request.GET.get('starts', default='all')
    for start in startswith_filter:
        compare = 'value=' + selected_filter
        if start[0] == compare:
            start[0] += ' selected=selected'
    if form != 2:
        miss_query = Document.objects.filter(docstatus__status = Document.MISSING,
                                             docstatus__return_lend = False)
        miss_query = miss_query.order_by('-docstatus__date')
    params_starts = _truncate_get(request, 'starts', 'page')
    searchform = SearchForm(request.GET or None)
    paginator = Paginator(documents, 10)
    get_page = request.GET.get('page', '1')
    if re.match(r'\d+#$', get_page):
        get_page = get_page.rstrip("#")
    try:
        page = int(get_page)
    except ValueError:
        page = 1
    try:
        fp = paginator.page(page)
    except (EmptyPage, InvalidPage):
        fp = paginator.page(paginator.num_pages)

    search_pro_baseform = SearchProBaseForm(request.POST or None, 
            prefix='baseform')
    try:
        search_pro_form = SearchProExtendedForm(request.POST or None,
            prefix='addform')
    except ValidationError:
        search_pro_form = SearchProExtendedForm()

    num_pages = paginator.num_pages
    dict_response = _get_dict_response(request)
    dict_response["searchform"] = searchform
#    dict_response["documents"] = documents
    dict_response["documents"] = fp
    dict_response["active_page"] = page
    dict_response["max_page"] = num_pages
    dict_response["doc_num"] = len(documents)
    dict_response["settings"] = settings
    dict_response["path_sort"] = params_sort
    dict_response["path_starts"] = params_starts
    dict_response["form"] = form
    dict_response["filter"] = startswith_filter
    if len(documents) == 0:
        dict_response["doc_num_start"] = 0
    else:
        dict_response["doc_num_start"] = page * 10 - 9
    if page == num_pages:
        dict_response["doc_num_end"] = len(documents)
    else:
        dict_response["doc_num_end"] = page * 10
    if search_pro_baseform.is_valid() and search_pro_form.is_valid():
        dict_response["search_pro_baseform"] = search_pro_baseform
        dict_response["search_pro_form"] = search_pro_form
    page_buttons = []
    button_range = 4
    start = page - button_range
    i = start
    end = page + button_range
    if page == 1:
        button = _generate_pagination_link(1, active=True)
    else:
        button = _generate_pagination_link(1)
    page_buttons.append(button)
    if start > 2:
        button = "<li><span>...</span></li>"
        page_buttons.append(button)
    while i < end and (i < num_pages):
        if i > 1:
            if not i == page:
                button = _generate_pagination_link(i)
            else:
                button = _generate_pagination_link(i, active=True)
            page_buttons.append(button)
        i = i + 1
    if not num_pages == 1:
        if end < (num_pages - 1):
            button = "<li><span>...</span></li>"
            page_buttons.append(button)
        if page == num_pages:
            button = _generate_pagination_link(num_pages, active=True)
        else:
            button = _generate_pagination_link(num_pages)
        page_buttons.append(button)
    dict_response["page_buttons"] = page_buttons
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

def _generate_pagination_link(page_number, active=False, enabled=True):
    if enabled == False:
        button = """<li class="disabled">
                        <a href="javascript:void(0)">
                            %i
                        </a>
                    </li>""" % (page_number)
    elif active == True:
        button = """<li class="active">
                        <a href="javascript:void(0)">
                            %i
                        </a>
                    </li>""" % (page_number)
    else:
        button = """<li>
                        <a href="javascript:void(0)"
                           onclick="insertParam('page', %i, false);
                                $('form#query_form').submit();"
                        >
                            %i
                        </a>
                    </li>""" % (page_number, page_number)
    return button

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

