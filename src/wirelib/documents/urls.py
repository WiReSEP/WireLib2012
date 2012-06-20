from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('documents.views',
        url(r'^$', 'index'), 
        url(r'^export$', 'export'), 
        url(r'^export/allegro$', 'allegro_export'),
        url(r'^export/bibtex$', 'bibtex_export'), 
        url(r'^search$', 'search'),
        url(r'^search/pro$', 'search_pro'),
        url(r'^doc_list$', 'doc_list'),
        url(r'^doc/(?P<bib_no_id>\w\d+)$', 'doc_detail'),
        url(r'^doc/add$', 'doc_add'),
        url(r'^rent$', 'doc_rent'), # Ausleihliste
        url(r'^user$', 'user'),
        url(r'^user/profile$', 'profile'), 
        url(r'^user/profile/settings$', 'profile_settings'),         
)

urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login$', 'login'),
        url(r'^logout$', 'logout'),
        url(r'^password_reset$', 'password_reset'), 
        url(r'^password_reset/done$', 'password_reset_done'), 
        
)   
