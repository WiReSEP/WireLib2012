#vim: set fileencoding=utf-8
from django.contrib.auth import decorators
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from documents.forms import DocumentForm
from documents.forms import NonUserForm
from documents.forms import SelectUserForm
from documents.forms import UploadFileForm
from documents.lib.bibtex import Bibtex
from documents.models import Document


class DocumentDetailView(DetailView):
    model = Document

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        context['userform'] = SelectUserForm(self.request.user)
        context['externalform'] = NonUserForm()
        return context


class DocumentChangeView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/doc_modify.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentChangeView, self).get_context_data(**kwargs)
        context['modify'] = True
        return context

    @method_decorator(
        decorators.permission_required('documents.change_document', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DocumentChangeView, self).dispatch(*args, **kwargs)


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/doc_add.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentCreateView, self).get_context_data(**kwargs)
        context['upload_form'] = UploadFileForm()
        context['modify'] = False
        return context

    def post(self, request, *args, **kwargs):
        if request.FILES:
            file_form = UploadFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                with request.FILES['file'] as bib_file:
                    Bibtex().do_import(bib_file)
        return super(DocumentCreateView, self).post(request, *args, **kwargs)

    @method_decorator(
        decorators.permission_required('documents.add_document', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(DocumentCreateView, self).dispatch(*args, **kwargs)


@decorators.permission_required('documents.can_lend', raise_exception=True)
def lend(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        raise Http404
    user = request.user
    editor = None
    non_user = None
    if request.method == 'POST':
        userform = SelectUserForm(request.user, request.POST)
        externalform = NonUserForm(request.POST)
        if externalform.is_valid():
            non_user = externalform.save()
        if userform.is_valid():
            editor = user
            user = userform.cleaned_data['users']
    document.lend(user, editor, non_user)
    return HttpResponseRedirect(reverse('documents.detail', kwargs={'pk': pk}))


@decorators.permission_required('documents.can_miss', raise_exception=True)
def missing(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        raise Http404
    document.missing(request.user)
    return HttpResponseRedirect(reverse('documents.detail', kwargs={'pk': pk}))


@decorators.permission_required('documents.can_unlend', raise_exception=True)
def unlend(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        raise Http404
    document.unlend(request.user)
    return HttpResponseRedirect(reverse('documents.detail', kwargs={'pk': pk}))


@decorators.permission_required('documents.can_lost', raise_exception=True)
def lost(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        raise Http404
    document.lost(request.user)
    return HttpResponseRedirect(reverse('documents.detail', kwargs={'pk': pk}))
