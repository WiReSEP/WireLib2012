#vim: set fileencoding=utf-8
from django.shortcuts import render


def index(request):
    return render(request, 'loremipsum/base.html', None)


def documents(request):
    return render(request, 'loremipsum/doc_list.html', None)


def documents_search(request):
    return render(request, 'loremipsum/search.html', None)


def new_documents(request):
    return render(request, 'loremipsum/doc_add_modify.html', None)


def duplicates(request):
    return render(request, 'loremipsum/duplicates.html', None)


def export(request):
    return render(request, 'loremipsum/export.html', None)


def doc_detail(request):
    return render(request, 'loremipsum/doc_detail.html', None)
