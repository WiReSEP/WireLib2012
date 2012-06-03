from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('documents.views',
        url(r'^$', 'index'),
        url(r'^search$', 'search'),
        url(r'^search/pro$', 'search_pro'),
        url(r'^doc$', 'doc_list'),
#        url(r'^doc/(?P<bib_no_id>\d+)$', 'doc_detail'),
        url(r'doc/K006009$', 'doc_detail'),
        url(r'^doc/add$', 'doc_add'),
        url(r'^rent$', 'doc_rent'), # Ausleihliste
)
