# vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from documents.views import DocumentList
from documents.views import MissedDocumentList
from documents.views import LendDocumentList
from documents.views import NonUserLendDocumentList
from documents.views import DocumentDetailView
from documents.views import DocumentChangeView
from documents.views import DocumentCreateView
from documents.views import lend
from documents.views import unlend
from documents.views import missing
from documents.views import lost
from documents.views import SearchView
from documents.views import ExportView
from documents.views import export_allegro
from documents.views import export_bibtex
from documents.views import NonUserDetailView


urlpatterns = patterns('documents.views',
                       url(r'^$',
                           'index',
                           name='documents.index'),
                       url(r'^search/$',
                           SearchView.as_view(),
                           name='documents.search'),
                       url(r'^list/$',
                           DocumentList.as_view(),
                           name='documents.list'),
                       url(r'^list/missed/$',
                           MissedDocumentList.as_view(),
                           name='documents.list.missed'),
                       url(r'^list/lend/$',
                           LendDocumentList.as_view(),
                           name='documents.list.lend'),
                       url(r'^list/nonuserlend/(?P<nonuser>\d+)/$',
                           NonUserLendDocumentList.as_view(),
                           name='documents.list.nonuserlend'),
                       url(r'^view/(?P<pk>\w\d+)/$',
                           DocumentDetailView.as_view(),
                           name='documents.detail'),
                       url(r'^lend/(?P<pk>\w\d+)/$',
                           lend,
                           name='documents.lend'),
                       url(r'^missing/(?P<pk>\w\d+)/$',
                           missing,
                           name='documents.miss'),
                       url(r'^lost/(?P<pk>\w\d+)/$',
                           lost,
                           name='documents.lost'),
                       url(r'^unlend/(?P<pk>\w\d+)/$',
                           unlend,
                           name='documents.unlend'),
                       url(r'^edit/(?P<pk>\w\d+)/$',
                           DocumentChangeView.as_view(),
                           name='documents.edit'),
                       url(r'^new/$',
                           DocumentCreateView.as_view(),
                           name='documents.new'),
                       url(r'^export/$',
                           ExportView.as_view(),
                           name='documents.export'),
                       url(r'^export/allegro/$',
                           export_allegro,
                           name='documents.export.allegro'),
                       url(r'^export/bibtex/$',
                           export_bibtex,
                           name='documents.export.bibtex'),
                       url(r'^users/(?P<pk>\w+)/$',
                           NonUserDetailView.as_view(),
                           name='documents.external')
                       )
