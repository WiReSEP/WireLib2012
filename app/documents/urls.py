from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from documents.views import *

urlpatterns = patterns('documents.views',
        url(r'^$', 'index', name='index'), 

#lists
        url(r'^doc_list/$', 'doc_list', name='docs'),
        #url(r'^account/rent/$', 'doc_rent', name='doc_rent'), # Ausleihliste
        url(r'^miss/$', 'docs_miss', name='docs_missed'),

#search
        url(r'^search/$', 'search', name='search'),
        url(r'^search_pro/$', 'search_pro', name='search_pro'),

#docs
        url(r'^doc/(?P<bib_no_id>\w\d+)/$', 'doc_detail', name='doc'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/assign/$', 'doc_assign', name='doc_assign'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/edit/$', 'doc_add', name='doc_edit'),

#import
        url(r'^doc/add/$', 'doc_add', name='doc_add'),
        url(r'^doc/import/$', 'doc_import', name='doc_import'),

#export
        url(r'^export/$', 'export', name='export'), 
        url(r'^export/allegro/$', 'allegro_export', name='export_allegro'),
        url(r'^export/bibtex/$', 'bibtex_export', name='export_bibtex'), 

#user
        #url(r'^user/$', 'user', name='user'),
        url(r'^user/$', 'profile', name='user'), 
        url(r'^user/docs/$', 'doc_rent', name='doc_rent'),
        url(r'^user/profile/$', 'profile', name='profile'), 
        url(r'^user/settings/$', 'profile_settings', name='profile_settings'),
        url(r'^user/settings/(?P<user_id>\d+)/$', 'profile_settings',
            name='profile_settings_other'),
        url(r'^user/(?P<user_id>\d+)/$', 'profile', name='user_profile'),
        url(r'^user/profile/edit/personal/done/$', direct_to_template,
            {'template': 'profile/personal_done.html'}, name='profile_edit_personal_done'), 

#profile
        url(r'^profile/edit/personal/$', personal, name='profile_edit_personal'), 
        url(r'^profile/edit/tel/$', telpersonal, name='profile_edit_tel'),
        url(r'^profile/edit/name/$', 'profile_edit_name', name='edit_name'), 
)

###############PROFIL#############################

#Links zur Profilnavigation

# Links zum Passwortaendern
urlpatterns += patterns('', 
        url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset',
            {'template_name': 'account/password_reset.html', 
             'email_template_name': 'email/password_reset_email.txt'}),
        url(r'^accounts/password/change/$', 'django.contrib.auth.views.password_change',
            {'template_name': 'account/password_change.html'},
            name='profile_edit_passwd'),
        url(r'^accounts/password/change/done/$', 'django.contrib.auth.views.password_change_done',
            {'template_name': 'account/password_change_done.html'}),  
) 

#Links zum Emailaendern 
urlpatterns += patterns('', 
        url(r'^email/validation/$', email_validation, name='profile_edit_mail'), 
        url(r'^email/validation/processed/$', direct_to_template,  
            {'template': 'account/email_validation_processed.html'}),
        url(r'^email/validation/(?P<key>.{70})/$', email_validation_process, name='email_validation_process'),
        url(r'^email/validation/reset/$', email_validation_reset),
) 

###################################
        
urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', name='login'),
        url(r'^logout/$', 'logout', {'next_page': '/'}, name='logout'),
)   
