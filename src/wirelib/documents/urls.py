from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from documents.views import *

urlpatterns = patterns('documents.views',
        url(r'^$', 'index', name='index'), 
        url(r'^export/$', 'export'), 
        url(r'^export/allegro/$', 'allegro_export'),
        url(r'^export/bibtex/$', 'bibtex_export'), 
        url(r'^search/$', 'search'),
        url(r'^search_pro/$', 'search_pro'),
        url(r'^doc_list/$', 'doc_list'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/$', 'doc_detail'),
        url(r'^doc/add/$', 'doc_add'),
        url(r'^doc/import/$', 'doc_import'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/assign/$', 'doc_assign'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/edit/$', 'doc_add'),
        url(r'^account/rent/$', 'doc_rent'), # Ausleihliste
        url(r'^user/$', 'user'),
        url(r'^user/profile/$', 'profile'), 
        url(r'^user/settings/(?P<user_id>\d+)/$', 'profile_settings'),
        url(r'^profile/edit/personal/$', personal, name='profile_edit_personal'), 
        url(r'^user/profile/edit/personal/done/$', direct_to_template,
            {'template': 'profile/personal_done.html'}, name='profile_edit_personal_done'), 
        
        url(r'^profile/edit/tel/$', telpersonal, name='profile_edit_tel'),
        url(r'^profile/edit/name/$', 'profile_edit_name'), 
        url(r'^user/(?P<user_id>\d+)/$', 'profile'),
        url(r'^miss/$', 'docs_miss'),
)

###############PROFIL#############################

#Links zur Profilnavigation

# Links zum Passwortaendern
urlpatterns += patterns('', 
        url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset',
            {'template_name': 'account/password_reset.html', 
             'email_template_name': 'email/password_reset_email.txt'}),
        url(r'^accounts/password/change/$', 'django.contrib.auth.views.password_change',
            {'template_name': 'account/password_change.html'}),
        url(r'^accounts/password/change/done/$', 'django.contrib.auth.views.password_change_done',
            {'template_name': 'account/password_change_done.html'}),  
) 

#Links zum Emailaendern 
urlpatterns += patterns('', 
        url(r'^email/validation/$', email_validation), 
        url(r'^email/validation/processed/$', direct_to_template,  
            {'template': 'account/email_validation_processed.html'}),
        url(r'^email/validation/(?P<key>.{70})/$', email_validation_process, name='email_validation_process'),
        url(r'^email/validation/reset/$', email_validation_reset),
) 

###################################
        
urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login/$', 'login'),
        url(r'^logout/$', 'logout', {'next_page': '/'}),
)   
