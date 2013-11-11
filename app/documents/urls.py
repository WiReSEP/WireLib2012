#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from documents.views import DocumentList
from documents.views import DocumentDetailView
from documents.views import DocumentChangeView
from documents.views import SearchView


urlpatterns = patterns('documents.views',
                       url(r'^$',
                           'index',
                           name='documents.index'),
                       url(r'^list/$',
                           DocumentList.as_view(),
                           name='documents.list'),
                       url(r'^missed/$',
                           'index',
                           name='documents.list.missed'),
                       url(r'^view/(?P<pk>\w\d+)/$',
                           DocumentDetailView.as_view(),
                           name='documents.detail'),
                       url(r'^edit/(?P<pk>\w\d+)/$',
                           DocumentChangeView.as_view(),
                           name='documents.edit'),
                       url(r'^search/$',
                           SearchView.as_view(),
                           name='documents.search'),
                       url(r'^new/$',
                           'index',
                           name='documents.new'),
                       url(r'^export/$',
                           'index',
                           name='documents.export'),
                       )
