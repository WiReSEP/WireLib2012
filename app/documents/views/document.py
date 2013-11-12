#vim: set fileencoding=utf-8
from documents.models import Document
from documents.forms import DocumentForm
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView


class DocumentDetailView(DetailView):
    model = Document


class DocumentChangeView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/doc_modify.html'
