from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

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
                       url(r'^$',
                           TemplateView.as_view(template_name='base.html'),
                           name='index'),
                       url(r'^admin/',
                           include(admin.site.urls)),
                       url(r'^lorem/',
                           include('loremipsum.urls')),
                       url(r'^documents/',
                           include('documents.urls')),
                       url(r'^users/',
                           include('users.urls')),
                       )
urlpatterns += staticfiles_urlpatterns()

#next lines are development only
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
