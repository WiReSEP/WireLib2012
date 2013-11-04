#vim: set fileencoding=utf-8
from django.views.generic import ListView
from documents.forms import SimpleSearch
from documents.forms import search
from documents.lib.paginator import ShortPaginator
from documents.models import Document


class DocumentList(ListView):
    model = Document
    paginate_by = 10
    paginator_class = ShortPaginator
    get_forms = (SimpleSearch,
                 )

    def __init__(self, *args, **kwargs):
        super(DocumentList, self).__init__(*args, **kwargs)
        self.forms = {}

    def get(self, request):
        get_params = ""
        for p in request.GET.items():
            if p[0] == 'page':
                continue
            get_params += "%s;" % '='.join(p)
        else:
            self.get_params = get_params.strip(';')
        return super(DocumentList, self).get(request)

    def _class2method_str(self, cls):
        """ Return a method name that fits to a class name.
        YetAnotherClassName => yet_another_class_name """
        name = cls.__name__
        out = name[0].lower()  # don't put an underscore to first letter
        for c in name[1:]:
            if c.isupper():
                out += '_'
            out += c.lower()
        return out

    def _search_query(self, query):
        return search(query)

    def get_queryset(self):
        from django.db.models import Q
        filter_title = self.request.GET.get('filter_title')
        filter_authors = self.request.GET.get('filter_authors')
        search = self.request.GET.get('search', '')
        q_obj = self._search_query(search)
        if filter_title:
            q_obj = q_obj.filter(title__iregex='^[%s].*$' % filter_title)
        if filter_authors:
            q_obj = q_obj.filter(Q(authors__first_name__iregex='^[%s].*$'
                                   % filter_authors) |
                                 Q(authors__last_name__iregex='^[%s].*$'
                                   % filter_authors)
                                 )
        return q_obj

    def process_forms(self):
        for form in DocumentList.get_forms:
            f = form(self.request.GET or None)
            context_name = self._class2method_str(f.__class__)
            self.forms[context_name] = f
            if 'process_' + context_name in dir(self):
                eval('self.process_%s()' % context_name)

    def get_context_data(self, **kwargs):
        self.process_forms()
        context = super(DocumentList, self).get_context_data(**kwargs)
        context['forms'] = self.forms
        context['get_params'] = self.get_params
        return context

    def process_simple_search(self):
        self.paginate_by = (self.request.GET.get('documents_on_page') or 10)
