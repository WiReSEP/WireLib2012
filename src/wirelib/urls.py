from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',
                           TemplateView.as_view(template_name='base.html'),
                           name='index'),
                       url(r'^admin/',
                           include(admin.site.urls)),
                       url(r'^documents/',
                           include('documents.urls')),
                       url(r'^users/',
                           include('users.urls')),
                       )
