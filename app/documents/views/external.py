#vim: set fileencoding=utf-8
from documents.models import NonUser
from django.contrib.auth import decorators
from django.utils.decorators import method_decorator
from django.views.generic import DetailView


class NonUserDetailView(DetailView):
    model = NonUser
    template_name = "documents/nonuser_detail.html"

    @method_decorator(decorators.permission_required('documents.can_unlend'))
    def dispatch(self, *args, **kwargs):
        return super(NonUserDetailView, self).dispatch(*args, **kwargs)
