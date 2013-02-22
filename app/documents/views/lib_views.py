# vim: set fileencoding=utf-8
from django.db.models import Q
from django.conf import settings
import datetime
import time
import hashlib
from documents.models import Document

def _get_dict_response(request):
    """ Dict-response default erstellen
    Gibt ein Python-Dict zurück mit Werten, die in jedem Template benötigt
    werden. Eigene Werte für Templates werden in den jeweiligen Methoden
    eingefügt.
    """
    v_user = request.user
    import_perm = v_user.has_perm('documents.can_import')
    export_perm = v_user.has_perm('documents.can_export')
    perms = v_user.has_perm('documents.can_see_admin')
    miss_query = Document.objects.filter(docstatus__status=Document.MISSING,
            docstatus__return_lend=False)
    miss_query = miss_query.order_by('-docstatus__date')
    return {"user": v_user,
            "perm": perms,
            "miss": miss_query[0:10],
            "import_perm": import_perm,
            "export_perm": export_perm}

def _get_searchset(searchvalue, regex=False):
    if not regex:
        return (Q(title__icontains=searchvalue) |
                Q(authors__first_name__icontains=searchvalue) |
                Q(authors__last_name__icontains=searchvalue) |
                Q(isbn__icontains=searchvalue) |
                Q(bib_no__icontains=searchvalue) |
                Q(publisher__name__icontains=searchvalue) |
                Q(keywords__keyword__icontains=searchvalue))
    return (Q(title__iregex=searchvalue) |
            Q(authors__first_name__iregex=searchvalue) |
            Q(authors__last_name__iregex=searchvalue) |
            Q(isbn__iregex=searchvalue) |
            Q(bib_no__iregex=searchvalue) |
            Q(publisher__name__iregex=searchvalue) |
            Q(keywords__keyword__iregex=searchvalue))


def _filter_names(documents, request):
    """Dem Benutzer wird ein reichhaltiges Angebot an Dokumenten angeboten und
    übersichtlich präsentiert. Er kann nach belieben zwischen Dokumenten mit
    beliebigem Anfangsbuchstaben wählen. Jedes Dokument muss selbstständig
    abgeholt werden, wir haften nicht für den Reiseweg!
    """
    sw = request.GET.get('starts', 'all')
    if sw == "special_sign":
        documents = documents.exclude(title__iregex='^[A-Za-z]')
    elif sw == "all" or sw is None or sw == "":
        documents = documents.all()
    else :
        sw_reg = '^[' + sw + ']'
        documents = documents.filter(title__iregex=sw_reg)
    return documents

def _gen_sec_link(path):
    secret = settings.SECRET_KEY
    uri_prefix = '/dl/'
    hextime = '%08x' % time.time()
    token = hashlib.md5(secret + path + hextime).hexdigest()
    return '%s%s/%s%s' % (uri_prefix, token, hextime, path)

def _filter_history(doc):
    new_history = doc.docstatus_set.order_by('-date')[0:10]
    return new_history

def _show_keywords(doc):
    keywords = doc.keywords_set.order_by('-keyword').exclude(keyword__iexact="")
    return keywords

def _clean_errors(form):
    for item in form.errors:
        form.errors[item] = ''

def _save_doc_form(form, document, doc_id=False):
    instances = form.save(commit=False)
    for instance in instances:
        if doc_id:
            instance.doc_id = document
        else :
            instance.document = document
            print 'changing', instance, document, instance.document
        instance.save()
