#vim: set fileencoding=utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response

def detaildummy(request):
    context = RequestContext(request)
    return render_to_response('loremipsum/doc_detail.html', 
                              context_instance=context)
