#vim: set fileencoding=utf-8
from documents.models import NonUser
from django.views.generic import DetailView


class NonUserDetailView(DetailView):
    model = NonUser
    template_name = "documents/nonuser_detail.html"
