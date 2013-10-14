#vim: set fileencoding=utf-8
from documents.models import Document
from django.views.generic import DetailView


class DocumentDetailView(DetailView):
    model = Document
