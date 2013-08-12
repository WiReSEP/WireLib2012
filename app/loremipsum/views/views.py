#vim: set fileencoding=utf-8
from django.shortcuts import render


def index(request):
    return render(request, 'loremipsum/base.html', None)
