#vim: set fileencoding=utf-8
from django.shortcuts import render
from django.views.generic.detail import DetailView

from django.contrib.auth.models import User


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

class UserProfileView(DetailView):
    model = User
    template_name = 'loremipsum/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['profile'] = self.object
        return context
