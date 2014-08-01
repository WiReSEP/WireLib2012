#vim: set fileencoding=utf-8

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.http import urlencode
from django.views.generic.edit import FormView
from documents.forms import SearchProExtendedForm
from documents.forms import normalise_extended_form


class SearchView(FormView):
    template_name = 'documents/search.html'
    form_class = SearchProExtendedForm
    success_url = reverse_lazy('documents.list')

    def form_valid(self, form):
        query = normalise_extended_form(form)
        url = self.get_success_url()
        redirect_to = '%s?%s' % (url, urlencode({'search': query}))
        return HttpResponseRedirect(redirect_to)
