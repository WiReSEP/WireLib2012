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
        url(r'^doc/(?P<user_id>\d+)$', 'doc_detail'),
        url(r'^doc/add$', 'doc_add'),
        url(r'^account/rent$', 'doc_rent'), # Ausleihliste
        url(r'^user$', 'user'),
        url(r'^user/profile$', 'profile'), 
        url(r'^user/profile/settings$', 'profile_settings'),
        url(r'^miss$', 'docs_miss'),
)



urlpatterns += patterns('', 
        url(r'^accounts/password_reset$', 'django.contrib.auth.views.password_reset',
            {'template_name': 'account/password_reset.html', 
             'email_template_name': 'email/password_reset_email.txt'}),
        url(r'^accounts/password/change$', 'django.contrib.auth.views.password_change',
            {'template_name': 'account/password_change.html'}),
        url(r'^accounts/password/change/done$', 'django.contrib.auth.views.password_change_done',
            {'template_name': 'account/password_change_done.html'}),  
) 

urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login$', 'login'),
        url(r'^logout$', 'logout'),
        
)   
