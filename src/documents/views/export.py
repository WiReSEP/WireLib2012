#vim: set fileencoding=utf-8
import os
import time
import hashlib
from os.path import normpath
from os.path import join
from django.conf import settings
from django.contrib.auth import decorators
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from documents.models import Document
from documents.lib.allegro import Allegro
from documents.lib.bibtex import Bibtex


class ExportView(TemplateView):
    template_name = 'documents/export.html'

    def get_context_data(self, **kwargs):
        context = super(ExportView, self).get_context_data(**kwargs)
        biblist = list()
        allegrolist = list()
        _basepath = normpath(settings.DOCUMENTS_SECDIR)
        _bibtexdir = normpath(settings.DOCUMENTS_BIBTEX)
        _allegrodir = normpath(settings.DOCUMENTS_ALLEGRO_FILES)
        filepath_bibtex = normpath(join(_basepath, _bibtexdir))
        filepath_allegro = normpath(join(_basepath, _allegrodir))
        for file in sorted(os.listdir(filepath_bibtex)):
            if str(file).lower().endswith('.bib'):
                _sec_path = join(_bibtexdir, file)
                sec_link = _gen_sec_link(_sec_path)
                biblist.append({'link': sec_link, 'desc': str(file)})
        for file in sorted(os.listdir(filepath_allegro)):
            if str(file).lower().endswith('.adt'):
                _sec_path = join(_allegrodir, file)
                sec_link = _gen_sec_link(_sec_path)
                allegrolist.append({'link': sec_link, 'desc': str(file)})
        biblist.reverse()
        context['biblist'] = biblist
        context['biblist_small'] = biblist[0:3]
        context['export_bib_state'] = Bibtex.get_state()

        allegrolist.reverse()
        context['allegrolist'] = allegrolist
        context['allegrolist_small'] = allegrolist[0:3]
        context['export_allegro_state'] = Allegro.get_state()
        return context

    @method_decorator(
        decorators.permission_required('documents.can_see_export', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ExportView, self).dispatch(*args, **kwargs)


def _gen_sec_link(path):
    """ Generate a formerly secure link, now its only a link.

    This method formerly generated a secure link to the BibTeX and Allegro
    export files. These file have been moved to /static/ in order to guarantee
    a fast drop of the dependency of lighttpd. Now essentially every webserver
    can be used to deploy WireLib.
    If in a random future secure links should be reimplemented the 'X-Sendfile'
    flag is probably a good starting point.
    """
    static = settings.STATIC_URL
    sec_path = settings.DOCUMENTS_SECDIR
    sec_dir = sec_path.rpartition('static/')[2]  # Everything left of static.
    file_path = join(static, sec_dir, path)
    return file_path


@decorators.permission_required('documents.can_export', raise_exception=True)
def export_allegro(request):
    if not Allegro.get_state():
        allegro_thread = Allegro()
        allegro_thread.start()
    return HttpResponseRedirect(reverse('documents.export'))


@decorators.permission_required('documents.can_export', raise_exception=True)
def export_bibtex(request):
    if not Bibtex.get_state():
        docs_to_export = Document.objects.filter(bib_date__isnull=True)
        _basepath = normpath(settings.DOCUMENTS_SECDIR)
        _bibtexdir = normpath(settings.DOCUMENTS_BIBTEX)
        _filepath_bibtex = normpath(join(_basepath, _bibtexdir))
        bibtex_thread = Bibtex().export_data(docs_to_export, _filepath_bibtex)
        bibtex_thread.start()
    return HttpResponseRedirect(reverse('documents.export'))
