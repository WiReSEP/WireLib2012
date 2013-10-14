#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from documents.views import DocumentList


urlpatterns = patterns('documents.views',
                       url(r'^$', 'index',
                           name='documents.index'),
                       url(r'^list/$',
                           DocumentList.as_view(),
                           name='documents.list'),
                       url(r'^missed/$', 'index',
                           name='documents.list.missed'),
                       url(r'^view/(?P<pk>\w\d+)/$', 'index',
                           name='documents.detail'),
                       url(r'^edit/(?P<pk>\w\d+)/$', 'index',
                           name='documents.edit'),
                       url(r'^search/$', 'index',
                           name='documents.search'),
                       url(r'^new/$', 'index',
                           name='documents.new'),
                       url(r'^export/$', 'index',
                           name='documents.export'),
                       )
