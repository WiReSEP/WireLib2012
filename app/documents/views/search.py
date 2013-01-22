def search(request):
  if "query" not in request.GET:
    return doc_list(request)
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
      if not request.method == "GET":
          dict_response = _get_dict_response(request)
          dict_response['AVAILABLE'] = Document.AVAILABLE
          dict_response['LEND'] = Document.LEND
          dict_response['MISSING'] = Document.MISSING
          dict_response['ORDERED'] = Document.ORDERED
          dict_response['LOST'] = Document.LOST
          context = Context(dict_response)
          return render_to_response("search_pro.html", context_instance=context)
