#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('documents.views',
                       url(r'^$',
                           'index',
                           name='users.index'),
                       )
