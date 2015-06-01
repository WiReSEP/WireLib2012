# vim: set fileencoding=utf-8
from django.contrib.auth import decorators
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from documents.forms import SimpleSearch
from documents.forms import search
from documents.lib.paginator import ShortPaginator
from documents.models import Document
from documents.models import NonUser


class DocumentList(ListView):

    """ Ordinary document list, as can be seen by every user. """

    model = Document
    paginate_by = 10
    paginator_class = ShortPaginator
    get_forms = (SimpleSearch,
                 )

    def __init__(self, *args, **kwargs):
        super(DocumentList, self).__init__(*args, **kwargs)
        self.forms = {}
        self.doc_start = 1
        self.doc_end = 10
        self.doc_count = 0

    def get(self, request, *args, **kwargs):
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

        YetAnotherClassName => yet_another_class_name
        """
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
            #fn_filter = Q(authors__first_name__iregex='^[%s].*$' % filter_authors)
            ln_filter = Q(authors__last_name__iregex='^[%s].*$' % filter_authors)
            #q_obj = q_obj.filter(fn_filter | ln_filter)
            q_obj = q_obj.filter(ln_filter)
        self.doc_count = q_obj.count()
        return q_obj

    def process_forms(self):
        for form in DocumentList.get_forms:
            f = form(self.request.GET or None)
            context_name = self._class2method_str(f.__class__)
            self.forms[context_name] = f
            if 'process_' + context_name in dir(self):
                eval('self.process_%s()' % context_name)

    def get_context_data(self, **kwargs):
        self.paginate_by = int(self.request.GET.get('documents_on_page') or 10)
        self.page = int(self.request.GET.get('page') or 1)
        self.doc_start = (self.page - 1) * self.paginate_by
        self.doc_end = self.doc_start + self.paginate_by
        self.doc_start += 1
        self.process_forms()
        context = super(DocumentList, self).get_context_data(**kwargs)
        context['forms'] = self.forms
        context['get_params'] = self.get_params
        if self.doc_count > self.doc_end:
            self.doc_end = self.doc_end
        else:
            self.doc_end = self.doc_count
        if self.doc_start > self.doc_end:
            self.doc_start = self.doc_end
        context['document_start'] = self.doc_start
        context['document_end'] = self.doc_end
        context['document_count'] = self.doc_count
        return context

    def process_simple_search(self):
        self.paginate_by = int(self.request.GET.get('documents_on_page') or 10)


class MissedDocumentList(DocumentList):

    """ List of missing documents. """

    def get_queryset(self):
        queryset = super(MissedDocumentList, self).get_queryset()
        queryset = queryset.filter(status=Document.MISSING)
        self.doc_count = queryset.count()
        return queryset

    @method_decorator(decorators.permission_required('documents.can_miss'))
    def dispatch(self, *args, **kwargs):
        return super(MissedDocumentList, self).dispatch(*args, **kwargs)


class LendDocumentList(DocumentList):

    """ List of documents lend by the logged in user. """

    username = None

    def get_queryset(self):
        queryset = super(LendDocumentList, self).get_queryset()
        queryset = queryset.filter(status=Document.LEND)
        user = self.request.user
        queryset = queryset.filter(docstatus__user_lend=user,
                                   docstatus__return_lend=False)
        self.doc_count = queryset.count()
        return queryset

    @method_decorator(decorators.permission_required('documents.can_lend'))
    def dispatch(self, *args, **kwargs):
        return super(LendDocumentList, self).dispatch(*args, **kwargs)


class NonUserLendDocumentList(DocumentList):

    """ List of documents lend by a NonUser. """

    def get_queryset(self):
        nonuser = NonUser.objects.get(pk=self.kwargs['nonuser'])
        queryset = super(NonUserLendDocumentList, self).get_queryset()
        queryset = queryset.filter(status=Document.LEND)
        queryset = queryset.filter(docstatus__non_user_lend=nonuser,
                                   docstatus__return_lend=False)
        self.doc_count = queryset.count()
        return queryset

    @method_decorator(decorators.permission_required('documents.can_lend'))
    def dispatch(self, *args, **kwargs):
        return super(NonUserLendDocumentList, self).dispatch(*args, **kwargs)
