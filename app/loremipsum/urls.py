#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from loremipsum.views import *

urlpatterns = patterns('loremipsum.views',
                       url(r'^$', 'index'),
                       url(r'^docdetail$', 'detaildummy'),
                       url(r'^documents$', 'documents'),
                       url(r'^documents/search$', 'documents_search'),
                       url(r'^duplicates$', 'duplicates'),
                       url(r'^documents/new$', 'new_documents'),
                       url(r'^export$', 'export'),
                       url(r'^documents/K198442$', 'doc_detail'),
                       )
