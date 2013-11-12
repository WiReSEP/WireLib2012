#vim: set fileencoding=utf-8
from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView
from documents.views import *

urlpatterns = patterns('documents.views',
        url(r'^$', 'index', name='index'),

#lists
#        url(r'^doc_list/$', 'doc_list', name='docs'),
#        url(r'^doc_list/$', 'search', name='docs'),
        url(r'^doc/$', 'search', name='docs'),
        #url(r'^account/rent/$', 'doc_rent', name='doc_rent'), # Ausleihliste
        url(r'^doc/missed/$', 'docs_miss', name='docs.missed'),

#search
#        url(r'^search/$', 'search', name='search'),
        url(r'^search/$', 'search_pro', name='search.pro'),

#docs
        url(r'^doc/(?P<bib_no_id>\w\d+)/$', 'doc_detail', name='doc'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/assign/$', 'doc_assign', name='doc.assign'),
        url(r'^doc/(?P<bib_no_id>\w\d+)/edit/$', 'doc_add', name='doc.edit'),

#import
        url(r'^doc/add/$', 'doc_add', name='doc.add'),
        url(r'^doc/import/$', 'doc_import', name='doc.import'),

#export
        url(r'^export/$', 'export', name='export'),
        url(r'^export/allegro/$', 'allegro_export', name='export.allegro'),
        url(r'^export/bibtex/$', 'bibtex_export', name='export.bibtex'),

#user
        #url(r'^user/$', 'user', name='user'),
        url(r'^user/$', 'profile', name='user'),
        url(r'^user/docs/$', 'doc_rent', name='doc.rent'),
#        url(r'^user/profile/$', 'profile', name='profile'),
        url(r'^user/settings/$', 'profile_settings', name='user.settings'),
        url(r'^user/settings/(?P<user_id>\d+)/$', 'profile_settings',
            name='user.settings.other'),
        url(r'^user/(?P<user_id>\d+)/$', 'profile', name='user.profile'),
#profile
        url(r'^profile/edit/personal/$', 'personal', name='user.edit.personal'),
        url(r'^profile/edit/phone/$', 'telpersonal', name='user.edit.phone'),
        url(r'^profile/edit/name/$', 'profile_edit_name', name='user.edit.name'),
        url(r'^profile/edit/personal/done/$',
            TemplateView.as_view(template_name='profile/personal_done.html'),
            name='profile.edit.personal.done'),

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
            name='user.edit.passwd'),
        url(r'^accounts/password/change/done/$', 'django.contrib.auth.views.password_change_done',
            {'template_name': 'account/password_change_done.html'}),
)

#Links zum Emailaendern
urlpatterns += patterns('',
        url(r'^email/validation/$', 'email_validation', name='user.edit.email'),
        url(r'^email/validation/processed/$',
            TemplateView.as_view(template_name='account/email_validation_processed.html')),
        url(r'^email/validation/(?P<key>.{70})/$', 'email_validation_process', name='email_validation_process'),
        url(r'^email/validation/reset/$', 'email_validation_reset'),
)

###################################

urlpatterns += patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', name='login'),
        url(r'^logout/$', 'logout', {'next_page': '/'}, name='logout'),
)
