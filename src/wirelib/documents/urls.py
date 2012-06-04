from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('documents.views',
        url(r'^$', 'index'),
        url(r'^search$', 'search'),
        url(r'^search/pro$', 'search_pro'),
        url(r'^doc$', 'doc_list'),
        url(r'^doc/(?P<bib_no_id>\w\d+)$', 'doc_detail'),
        url(r'^doc/add$', 'doc_add'),
        url(r'^rent$', 'doc_rent'), # Ausleihliste
)

urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login$', 'login'),
        url(r'^logout$', 'logout'),
        
)
