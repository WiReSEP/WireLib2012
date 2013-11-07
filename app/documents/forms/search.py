#vim: set fileencoding=utf-8
from __future__ import unicode_literals
from django import forms
from django.db.models import Q
from django.forms.formsets import formset_factory
from documents.models import Document

SEARCH_CATEGORY_CHOICES = (('all', 'Alle Kategorien'),
                           ('title', 'Titel'),
                           ('author', 'Autor'),
                           ('editor', 'Editor'),
                           ('keywords', 'Schlüsselwort'),
                           ('year', 'Jahr'),
                           ('publisher', 'Herausgeber'),
                           ('bib_no', 'Bibliotheks-Nummer'),
                           ('isbn', 'ISBN'),
                           ('status', 'Buchstatus'),
                           )

SEARCH_CATEGORIES = {
    Document.objects: {'all': 'all',
                       'title': 'title',
                       'author': {'search': ('authors__last_name',
                                             'authors__first_name'),
                                  'filter': ({'authors__documentauthors__editor':
                                              False},
                                             )
                                  },
                       'editor': {'search': ('authors__last_name',
                                             'authors__first_name'),
                                  'filter': ({'authors__documentauthors__editor':
                                              True},
                                             )
                                  },
                       'keywords': 'keywords__keyword',
                       'year': 'year',
                       'publisher': 'publisher__name',
                       'bib_no': 'bib_no',
                       'isbn': 'isbn',
                       'status': 'status',
                       }
}
LOGIC_CHOICES = (('AND', 'und'),
                 ('NAND', 'und nicht'),
                 ('OR', 'oder'),
                 )
REGEX_DESCRIPTION_LINK = 'http://perldoc.perl.org/perlrequick.html'
REGEX_LABEL = '<a href="%s">Regex</a>' % REGEX_DESCRIPTION_LINK


class SearchForm(forms.Form):
    search = forms.CharField(label='', required=False, max_length=255)


class SearchProForm(forms.Form):
    bind = forms.ChoiceField(choices=LOGIC_CHOICES, label='Verknüpfung',
                             required=False)
    category = forms.ChoiceField(choices=SEARCH_CATEGORY_CHOICES,
                                 required=False, label='Suchfeld')
    searchtext = forms.CharField(label='Suchfilter', required=False)
    regex = forms.BooleanField(required=False, label=REGEX_LABEL)
    bind.widget.attrs['class'] = 'hidden span2'
    searchtext.widget.attrs['class'] = 'span5'
    regex.widget.attrs['class'] = 'span1'
    category.widget.attrs['class'] = 'span3'
    category.css = 'span4'

    class Media:
        js = ('js/dynamic-formset.js', )


SearchProExtendedForm = formset_factory(SearchProForm)


def normalise_extended_form(searchform):
    """Durch diese Methode werden die normale und die erweiterte Suche
    zueinander kompatibel. Suchstrings aus der erweiterten Suche werden in
    einem Format formatiert, welches von der normalen Suche interpretiert
    werden kann.
    """
    query = ''
    for form in searchform:
        cleaned_data = form.cleaned_data
        print cleaned_data
        try:
            bind = cleaned_data['bind']
            searchtext = cleaned_data['searchtext']
            regex = cleaned_data['regex']
            category = cleaned_data['category']
        except KeyError:
            searchtext = ''
            category = 'all'
            regex = False
        pattern = _create_searchpattern(searchtext, category, regex)
        if pattern:
            if query:
                query += ' %s ' % bind
            query += pattern
    return query


def _create_searchpattern(query, category, regex):
    if not query or query == '':
        return None
    pattern = category
    pattern += '~' if regex else '='
    pattern += query
    return pattern


def search(query):
    documents = Document.objects.all()
    for q in _get_search_list(query):
        documents = _filter_searchset(documents, **q)
    return documents


def _get_search_list(query):
    import re
    queries = []
    bindings = r'\s+(N?AND|OR)\s+'
    pattern = r'(?P<category>.*?)(?P<regex>\=|\~)(?P<query>.*)'
    if re.search(bindings, query) or re.match(pattern, query):
        # using regular bindings
        keywords = re.split(bindings, query)
        keywords.insert(0, 'AND')
        for i in range(1, len(keywords), 2):
            matching = re.match(pattern, keywords[i])
            if matching:
                q = matching.groupdict()
            else:
                q = {}
                q['category'] = 'all'
                q['regex'] = False
                q['query'] = keywords[i]
            q['bind'] = keywords[i - 1]
            queries.append(q)
    else:  # using AND with '\s+' as splitpattern
        keywords = re.split(r'\s+', query)
        for key in keywords:
            q = {}
            q['category'] = 'all'
            q['query'] = key
            q['regex'] = False
            q['bind'] = 'AND'
            queries.append(q)
    return queries


def _filter_searchset(searchset, category, query, regex, bind,
                      filter_target=Document.objects):
    if not query or query == '':
        return searchset
    new_searchset = _get_advanced_searchset(category, query, regex,
                                            filter_target)
    ids = new_searchset.values('pk')
    if not bind:
        return new_searchset
    if bind.lower() == 'and':
        searchset = searchset.filter(pk__in=ids)
    elif bind.lower() == 'nand':
        searchset = searchset.exclude(pk__in=ids)
    elif bind.lower() == 'or':
        searchset = searchset | new_searchset
    else:
        raise AttributeError('binding did not match')
    return searchset


def _get_advanced_searchset(category, query, regex,
                            filter_target=Document.objects):
    import types
    category = SEARCH_CATEGORIES[filter_target].get(category, None)
    searchset = filter_target.none()
    if not category:
        return searchset
    if isinstance(category, types.StringTypes):
        if not category == 'all':
            q = _get_q(category, query, regex)
            searchset = filter_target.filter(q)
        else:
            searchset = _iter_searchlist([c for c, n in SEARCH_CATEGORY_CHOICES],
                                         query, regex, filter_target)
    elif isinstance(category, (list, tuple)):
        searchset = _iter_searchlist(category, query, regex, filter_target)
    else:
        searchset = _complex_filter(category, query, regex, filter_target)
    return searchset


def _get_q(category, query, regex):
    if not regex or regex == '=':
        q = Q(**{'%s__icontains' % category: query})
    else:
        q = Q(**{'%s__iregex' % category: query})
    return q


def _complex_filter(category, query, regex, filter_target):
    searchset = filter_target.none()
    if isinstance(category, dict):
        search = category['search']
        filter = category.get('filter', None)
        exclude = category.get('exclude', None)
        if search and isinstance(search, basestring):
            q = _get_q(search, query, regex)
            searchset = filter_target.filter(q)
        elif isinstance(search, (list, tuple)):
            import operator
            qs = [_get_q(s, query, regex) for s in search]
            searchset = filter_target.filter(reduce(operator.or_, qs))
        for f in filter or []:
            q = Q(**f)
            searchset = searchset.filter(q)
        for f in exclude or []:
            q = Q(**f)
            searchset = searchset.exclude(q)
    return searchset


def _iter_searchlist(category_list, query, regex, filter_target):
    searchset = filter_target.none()
    for category in category_list:
        if category == 'all':
            continue
        searchset = searchset | _get_advanced_searchset(category, query, regex,
                                                        filter_target)
    return searchset
