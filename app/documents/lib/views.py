# vim: set fileencoding=utf-8
from django.db.models import Q
from django.conf import settings
import datetime
import time
import hashlib

def _get_searchset(searchvalue):
    return (Q(title__icontains = searchvalue) |
            Q(authors__first_name__icontains = searchvalue) |
            Q(authors__last_name__icontains = searchvalue) |
            Q(isbn__icontains = searchvalue) |
            Q(bib_no__icontains = searchvalue) |
            Q(publisher__name__icontains = searchvalue) |
            Q(keywords__keyword__icontains = searchvalue))

def _filter_names(documents, request):
    """Dem Benutzer wird ein reichhaltiges Angebot an Dokumenten angeboten und
    übersichtlich präsentiert. Er kann nach belieben zwischen Dokumenten mit
    beliebigem Anfangsbuchstaben wählen. Jedes Dokument muss selbstständig
    abgeholt werden, wir haften nicht für den Reiseweg!
    """
    sw = request.GET.get('starts', '')

    if sw == "special_sign":
        documents = documents.exclude(title__iregex='[A-Za-z]')
    elif sw == "all" or sw is None or sw == "":
        documents = documents.all()
    else :
        sw_reg = '[' + sw + ']'
        documents = documents.filter(title__iregex=sw)
    return documents

def _gen_sec_link(path):
    secret = settings.SECRET_KEY
    uri_prefix = '/dl/'
    hextime = '%08x' % time.time()
    token = hashlib.md5(secret + path + hextime).hexdigest()
    return '%s%s/%s%s' % (uri_prefix, token, hextime, path)

def _filter_history(doc):
    new_history = doc.DocStatus_set.order_by('-date')[0:10]
    return new_history

def _show_keywords(doc):
    keywords = doc.Keywords_set.order_by('-keyword').exclude(keyword__iexact="")
    return keywords

def _diff_authors(doc):
    authors = doc.DocumentAuthors_set.order_by('-author').exclude(editor=True)
    return authors

def _diff_editors(doc):
    editors = doc.DocumentAuthors_set
    editors = editors.order_by('-author').exclude(editor=False)
    return editors
