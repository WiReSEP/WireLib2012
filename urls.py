from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'wirelib.views.home', name='home'),
                       # url(r'^wirelib/', include('wirelib.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       #(r'^$', 'documents.views.index'),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^lorem/', include('loremipsum.urls')),
                       url(r'^documents/', include('documents.urls')),
                       )
urlpatterns += staticfiles_urlpatterns()
