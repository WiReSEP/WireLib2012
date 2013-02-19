#vim: set fileencoding=utf-8
def doc_detail(request, bib_no_id, searchtext=""):
    """
    Gibt alle Informationen für doe Detailansicht eines Dokumentes zurück
    """
    v_user = request.user
    try:
        document_query = Document.objects.get(bib_no=bib_no_id)
    except Document.DoesNotExist:
        raise Http404
    if 'lend' in request.POST and v_user.is_authenticated(): #selbst ausleihen
        document_query.lend(v_user)
    if 'restitution'in request.POST and v_user.is_authenticated(): #zurückgeben
        document_query.unlend(v_user)
    if 'missing' in request.POST and v_user.is_authenticated(): #vermisst melden
        document_query.missing(v_user)
        thread.start_new_thread(
                __document_missing_email,
                (document_query, v_user)
                )
    if 'lost' in request.POST and v_user.is_authenticated(): #verloren melden
        document_query.lost(v_user)
    if 'found' in request.POST and v_user.is_authenticated(): #wiedergefunden
        document_query.lend(v_user)
    #aktualisieren des Datensatzes
    try:
        document_query = Document.objects.get(bib_no=bib_no_id)
    except Document.DoesNotExist:
        raise Http404
    try:
        lending_query = document_query.docstatus__set.latest('date')
    except DocStatus.DoesNotExist:
        lending_query = None
    doc_extra_query = DocExtra.objects.filter(doc_id__bib_no__exact=bib_no_id)
    bibtex_string = Bibtex.export_doc(document_query)
#auslesen der Rechte
    can_lend = v_user.has_perm('documents.can_lend')
    can_unlend = v_user.has_perm('documents.can_unlend')
    can_miss = v_user.has_perm('documents.can_miss')
    can_lost = v_user.has_perm('documents.can_lost')
    can_order = v_user.has_perm('documents.can_order')
    can_see_history = v_user = v_user.has_perm('documents.can_see_history')
    can_see_price = v_user.has_perm('documents.can_see_price')
    can_see_locn = v_user.has_perm('documents.can_see_locn')
    can_see_last_update = v_user.has_perm('documents.can_see_last_update_info')
    can_see_date_of_purchase = v_user.has_perm('documents.can_see_dop')
    can_see_export = v_user.has_perm('documents.can_see_export')
    change_document = v_user.has_perm('documents.change_document')
    history = lib_views._filter_history(document_query)
    keyword = lib_views._show_keywords(document_query)
    editors = document_query.get_editors()
    authors = document_query.get_authors()
    miss_query = Document.objects.filter(docstatus__status=Document.MISSING,
            docstatus__return_lend=False)
    miss_query = miss_query.order_by('-docstatus__date')
    if len(searchtext) == 1:
        searchmode = 1
    elif len(searchtext) > 1:
        searchmode = 2
    else:
        searchmode = 0
    dict_response = _get_dict_response(request)
    dict_response["bib_no"]
    dict_response["documents"] = document_query
    dict_response["lending"] = lending_query
    dict_response["doc_extra"] = doc_extra_query
    dict_response["bibtex_string"] = bibtex_string
    dict_response["can_lend"] = can_lend
    dict_response["can_unlend"] = can_unlend
    dict_response["can_miss"] = can_miss
    dict_response["can_lost"] = can_lost
    dict_response["can_order"] = can_order
    dict_response["can_see_history"] = can_see_history
    dict_response["can_see_price"] = can_see_price
    dict_response["can_see_locn"] = can_see_locn
    dict_response["can_see_last_update"] = can_see_last_update
    dict_response["can_see_date_of_purchase"] = can_see_date_of_purchase
    dict_response["can_see_export"] = can_see_export
    dict_response["change_document"] = change_document
    dict_response["history"] = history
    dict_response["keyword"] = keyword
    dict_response["editors"] = editors
    dict_response["authors"] = authors
    dict_response["searchmode"] = searchmode
    dict_response["searchtext"] = searchtext
    context = Context(dict_response)

    response = HttpResponse(template.render(context))
    return response
