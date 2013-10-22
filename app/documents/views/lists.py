#vim: set fileencoding=utf-8
from django.views.generic import ListView
from documents.models import Document
from documents.lib.paginator import ShortPaginator


class DocumentList(ListView):
    model = Document
    paginate_by = 10
    paginator_class = ShortPaginator
