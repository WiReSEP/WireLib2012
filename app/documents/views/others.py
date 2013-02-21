#vim: set fileencoding=utf-8
import os
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template import loader
from documents.lib.bibtex import Bibtex
from documents.lib.allegro import Allegro
# Dependencies for doc/add
from documents.models import Document
from documents.models import DocumentAuthors
from documents.models import DocExtra
from documents.models import Category
from documents.forms import DocForm
from documents.forms import AuthorSelectForm
from documents.forms import DocExtraForm
from documents.forms import AuthorAddForm
from documents.forms import PublisherAddForm

# Dependencies for doc/import
from documents.forms import UploadFileForm

# Dependencies for doc/<?>/assign
from documents.forms import SelectUser
from documents.forms import NonUserForm
from documents.forms import TelNonUserForm
from documents.models import DocStatus

# Dependencies for doc/missed
from documents.views.doc_lists import _list

from settings import *
from lib_views import _get_dict_response
from django.shortcuts import render_to_response

@login_required
def export(request):
    """Oberseite der Exporte. Die View lädt einfach das entsprechende Template
    unter Abfrage der für Navileiste benötigten Rechte
    """
    context = Context(_get_dict_response(request))
    return render_to_response("export.html", context_instance=context)

@login_required
def allegro_export(request):
    """Seite um den Allegro-Export zu initiieren und für den Zugriff auf
    bisher erstellte Allegro Exporte.
    """
    hint = ''
    alg_exp = Allegro()
    if "allegro_export" in request.POST:
        alg_exp.start()
        hint = "Der Export läuft. Bitte besuchen Sie uns in ein paar Minuten wieder."
        if alg_exp.isAlive():
            hint = "Derzeit läuft ein Export."
        elif not Allegro.docs_to_export:
            hint = "Keine Dokumente zum Exportieren."
            Allegro.docs_to_export_lock.acquire()
            Allegro.docs_to_export = True
            Allegro.docs_to_export_lock.release()
    files = {}
    for file in os.listdir(DOCUMENTS_SECDIR+"/"+DOCUMENTS_ALLEGRO_FILES):
        if str(file).lower().endswith(".adt"):
            files[file] = lib_views._gen_sec_link(
                    "/"
                    +DOCUMENTS_ALLEGRO_FILES
                    +file
                    )
    dict_response = _get_dict_response(request)
    dict_response["files"] = files
    dict_response["hint"] = hint
    context = Context(dict_response)
    return render_to_response("allegro_export.html", context_instance=context)

@login_required
def bibtex_export(request):
    """Seite um den Datenbankexport in BibTeX zu initiieren und für den Zugriff
    auf bisher exportierte BibTeX-Exporte.
    TODO: Zugriff nur auf Benutzer beschränken, die Dokumente hinzufügen
    dürfen.
    """
    hint = ''
    if Bibtex.bibtex_lock.locked():
        hint = "Der Export läuft. Bitte besuchen Sie uns in ein paar Minuten wieder."
    elif "bibtex_export" in request.POST:
        export_documents = Document.objects.filter(bib_date__isnull=True)
        Bibtex.export_data(
                export_documents,
                normpath(join(DOCUMENTS_SECDIR, DOCUMENTS_BIBTEX))
                ).start()
        hint = "Der Export läuft. Bitte besuchen Sie uns in ein paar Minuten wieder."

    files = {}
    for file in os.listdir(normpath(join(DOCUMENTS_SECDIR, DOCUMENTS_BIBTEX))):
        if str(file).lower().endswith(".bib"):
            files[file] = lib_views._gen_sec_link(
                    "/"
                    +DOCUMENTS_BIBTEX
                    +file
                    )
    dict_response = _get_dict_response(request)
    dict_response["files"] = files
    dict_response["hint"] = hint
    context = Context(dict_response)
    return render_to_response("bibtex_export.html", context_instance=context)

def doc_import(request):
    """BibTeX-Dateien importieren
    Hier kann der Benutzer mit den entsprechenden Rechten eine BibTeX-Datei
    hochladen und deren Inhalte der Datenbank hinzufügen.
    """
    success = True
    message = ""
    v_user = request.user
    if (not v_user.has_perm('documents.add_document') and not
            v_user.has_perm('documents.change_document') and not
            v_user.has_perm('documents.can_import')):
        raise PermissionDenied
    if len(request.FILES) > 0:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            date = datetime.datetime.today()
            filename = DOCUMENTS_IMPORT_FILES + \
                datetime.datetime.strftime(date, '%s') + '.bib'
            destination = open(filename, 'wb+')
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()
            Bibtex().do_import(filename)
            os.remove(filename)
            filesize = os.path.getsize(filename + '.err')
            if filesize == 0:
                message = 'Datei erfolgreich übernommen.'
            else:
                errfile = open(filename + '.err', 'r')
                message = "Datei konnte nicht vollständig übernommen werden \n\n "
                success = False
                for line in errfile:
                    message += line
                errfile.close()
            os.remove(filename + '.err')
    else:
        form = UploadFileForm()
    dict_response = _get_dict_response(request)
    dict_response["form"] = form
    dict_response["message"] = message
    dict_response["success"] = success
    context = Context(dict_response)
    return render_to_response("file_import.html", context_instance=context)

def doc_add(request, bib_no_id=None):
    """Ein Dokument hinzufügen
    Hier kann der Benutzer mit den entsprechenden Rechten ein Dokument der
    Datenbank hinzufügen. Dies wird durch Formeingabe ermöglicht.
    """
    success = True
    message = u''
    v_user = request.user
    if (not v_user.has_perm('documents.add_document') and not
            v_user.has_perm('documents.change_document') and not
            v_user.has_perm('documents.can_import')):
        raise PermissionDenied
    if bib_no_id is None:
        is_importform = True
        document = Document()
        query_authors = DocumentAuthors.objects.none()
        query_editors = DocumentAuthors.objects.none()
        query_extras = DocExtra.objects.none()
    else:
        is_importform = False
        try:
            document = Document.objects.get(bib_no=bib_no_id)
            query_authors = DocumentAuthors.objects.order_by('sort_value')
            query_editors = query_authors.filter(editor=True,
                    document=document)
            query_authors = query_authors.filter(editor=False,
                    document=document)
            query_extras = DocExtra.objects.filter(doc_id=document)
        except Document.DoesNotExist:
            raise Http404

    if request.method == 'POST':
        form_doc = DocForm(reuqest.POST, instance=document)
        form_authors = AuthorSelectForm(request.POST, instance=document)
        form_extras = DocExtraForm(request.POST, queryset=query_extras)
        form_author = AuthorAddForm(request.POST)
        form_publisher = PublisherAddForm(request.POST)

        if u'sub_author' in request.POST and form_author.is_valid():
            form_author.save()
            message = u'Autor erfolgreich hinzugefügt'
            lib_views._clean_errors(form_doc)
            lib_views._clean_errors(form_publisher)
            form_author = AuthorAddForm()
        elif u'sub_publisher' in request.POST and form_publisher.is_valid():
            form_publisher.save()
            message = u'Publisher erfolgreich hinzugefügt'
            lib_views._clean_errors(form_doc)
            lib_views._clean_errors(form_author)
            form_publisher = PublisherAddForm()
        elif u'submit' in request.POST and form_doc.is_valid():
            if form_authors.is_valid() and form_extras.is_valid():
                document = form_doc.save()
                lib_views._save_doc_form(form_authors, document)
                lib_views._save_doc_form(form_extras, document, True)
                document.save()
                if not bib_no_id is None and success:
                    return HttpResponseRedirect(reverse('doc', args=(bib_no_id,)))
                query_extras = DocExtra.objects.filter(doc_id=document)
                form_extras = DocExtraForm(queryset=query_extras)
                lib_views._clean_errors(form_author)
                lib_views._clean_errors(form_publisher)
            else:
                success = False
                message = u'Eingabe nicht vollständig korrekt'
        else:
            success = False
            message = u'Keine Valide Eingabe vorhanden'
    else:
        form_doc = DocForm(instance=document)
        form_authors = AuthorSelectForm(instance=document)
        form_extras = DocExtraForm(queryset=query_extras)
        form_author = AuthorAddForm()
        form_publisher = PublisherAddForm()

    #TODO
#   category_needs = category_need.objects.all()
    needs = dict()
#   for c in category_needs:
#       if (u""+c.category.name) not in needs:
#           needs[u""+c.category.name] = []
#       needs[u""+c.category.name].append(c.need)
    cat = Category.objects.filter()
    dict_response = _get_dict_response(request)
    dict_response["bib_no"] = bib_no_id
    dict_response["is_importform"] = is_importform
    dict_response["category"] = cat
    dict_response["form_doc"] = form_doc
    dict_response["form_authors"] = form_authors
    dict_response["form_extras"] = form_extras
    dict_response["form_author"] = form_author
    dict_response["form_publisher"] = form_publisher
    dict_response["message"] = message
    dict_response["success"] = success
    dict_response["category_needs"] = needs
    context = Context(dict_response)
    return render_to_response("doc_add.html", context_instance=context)

def doc_assign(request, bib_no_id):
    """Übertragen an andere Benutzer
    Diese Methode ermöglicht das Übertragen von selbst geliehenen Dokumenten an
    andere registrierte Benutzer.
    """
    v_user = request.user
    userform = SelectUser(v_user)
    nonuserform = NonUserForm()
    telnonuserform = TelNonUserForm()
    user_lend = ""
    try:
        document_query = Document.objects.get(bib_no=bib_no_id)
    except Document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.docstatus_set.latest('date')
    except DocStatus.DoesNotExist:
        lending_query = None
    if 'assign' in request.POST and v_user.is_authenticated():
        userform = SelectUser(v_user, request.POST)
        if userform.is_valid():
            user_lend = userform.cleaned_data["users"]
            if user_lend and not user_lend == "":
                document_query.lend(user=user_lend, editor=v_user)
                return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")
    elif 'assign-ex' in request.POST:
        nonuserform = NonUserForm(request.POST)
        telnonuserform = TelNonUserForm(request.POST)
        if nonuserform.is_valid() and telnonuserform.is_valid():
            non_user_lend = nonuserform.save()
            telnonuser, created = TelNonUser.objects.get_or_create(non_user=non_user_lend)
            telnonuserform = TelNonUserForm(request.POST, instance=telnonuser)
            telnonuserform.save()
            if non_user_lend and not non_user_lend == "":
                document_query.lend(user=v_user, non_user=non_user_lend)
                return HttpResponseRedirect("/doc/"+document_query.bib_no+"/")
    miss_query = Document.objects.filter(docstatus__status=Document.MISSING,
            docstatus__return_lend=False)
    miss_query = miss_query.order_by('-docstatus__date')
    template = loader.get_template("doc_assign.html")
    dict_response = _get_dict_response(request)
    dict_response["documents"] = document_query
    dict_response["lending"] = lending_query
    dict_response["userform"] = userform
    dict_response["nonuserform"] = nonuserform
    dict_response["telnonuserform"] = telnonuserform
    context = Context(dict_response)
    response = HttpResponse(template.render(context))
    return response

def docs_miss(request):
    """
    Vermisste Dokumente anzeigen
    """
    miss_query = Document.objects.filter(docstatus__status = Document.MISSING,        
                                         docstatus__return_lend = False)
    miss_query = miss_query.order_by('-docstatus__date')  
    return _list(request, miss_query, form=2)

def index(request): 
    """Rendert die Index-Seite.
    Really need a description?
    """
    context = Context(_get_dict_response(request))
    return render_to_response("index.html",context_instance=context)
