#vim: set fileencoding=utf-8

from django.template import RequestContext
from django.shortcuts import render_to_response


def index(request):
    context = RequestContext(request)
    return render_to_response("base.html", context_instance=context)
