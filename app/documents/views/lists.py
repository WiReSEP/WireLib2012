#vim: set fileencoding=utf-8
from django.views.generic import ListView
from documents.models import Document


class DocumentList(ListView):
    model = Document
    template_name = 'documents/doc_list.html'
