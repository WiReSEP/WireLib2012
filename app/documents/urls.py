#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from documents.views import *

urlpatterns = patterns('documents.views',
                       url(r'^$', 'index', name='index'),
                       #lists
                       url(r'^doc/$', 'search', name='docs'),
                       url(r'^doc/missed/$', 'docs_miss', name='docs.missed'),
                       #search
                       url(r'^search/$', 'search_pro', name='search.pro'),
                       #docs
                       url(r'^doc/(?P<bib_no_id>\w\d+)/$', 'doc_detail',
                           name='doc'),
                       url(r'^doc/(?P<bib_no_id>\w\d+)/assign/$',
                           'doc_assign',
                           name='doc.assign'),
                       url(r'^doc/(?P<bib_no_id>\w\d+)/edit/$', 'doc_add',
                           name='doc.edit'),
                       #import
                       url(r'^doc/add/$', 'doc_add', name='doc.add'),
                       url(r'^doc/import/$', 'doc_import', name='doc.import'),
                       #export
                       url(r'^export/$', 'export', name='export'),
                       url(r'^export/allegro/$', 'allegro_export',
                           name='export.allegro'),
                       url(r'^export/bibtex/$', 'bibtex_export',
                           name='export.bibtex'),
                       )
