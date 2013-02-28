from django.template import Context
from django.shortcuts import render_to_response
from lib_views import _get_dict_response
from doc_lists import doc_list, _list
from documents.forms import SearchForm, SearchProBaseForm, SearchProExtendedForm
from django.db.models import Q
from documents.models import Document
from doc_detail import doc_detail
import lib_views

def search(request):
#  if not request.method == "GET":
#    return doc_list(request)
  documents = Document.objects.all()
  form = SearchForm(request.GET)
  if not form.is_valid():
    return doc_list(request)
  query = form.cleaned_data['query']
  regex = form.cleaned_data['regex']
  searchtext = [query[:],]
  searchset = lib_views._get_searchset(query, regex)
  documents = Document.objects.filter(searchset).distinct()
  if documents.count() == 1:
    return doc_detail(request, documents[0].bib_no, searchtext)
  return _list(request, documents, None, 0, searchtext)

def search_pro(request):
  search_base_form = SearchProBaseForm(request.POST or None, prefix='baseform')
  search_form = SearchProExtendedForm(request.POST or None, prefix='addform')

  if search_base_form.is_valid() and search_form.is_valid():
    cleaned_base_data = search_base_form.cleaned_data
    category = cleaned_base_data["category"]
    searchtext = cleaned_base_data["searchtext"]
    regex = cleaned_base_data["regex"]
    searchset = _get_advanced_searchset(category, searchtext, regex)
    for form in search_form:
      cleaned_data = form.cleaned_data
      category = cleaned_data["category"]
      searchtext = cleaned_data["searchtext"]
      regex = cleaned_data["regex"]
      bind = cleaned_data["bind"]
      searchset = _combine_querys(searchset, category, searchtext, regex, bind)
    if searchset.count() == 1:
      return doc_detail(request, searchset[0].bib_no)
    return _list(request, searchset)
  dict_response = _get_dict_response(request)
  dict_response['base_form'] = search_base_form
  dict_response['extended_form'] = search_form
  context = Context(dict_response)
  return render_to_response("search_pro.html", context_instance=context)

def _combine_querys(searchset, category, query, regex, bind):
  if not query or query == "":
      return searchset
  new_searchset = _get_advanced_searchset(category, query, regex)
  ids = new_searchset.values('bib_no')
  if bind == "and":
    searchset = searchset.filter(bib_no__in=ids)
  elif bind == "and not":
    searchset = searchset.exclude(bib_no__in=ids)
  elif bind == "or":
    searchset = searchset | new_searchset
  else:
    raise AttributeError("binding did not match")
  return searchset

def _get_advanced_searchset(category, query, regex):
  if not regex:
    q = Q(**{"%s__icontains" % category: query})
  else:
    q = Q(**{"%s__iregex" % category: query})
  searchset = Document.objects.filter(q)
  return searchset
