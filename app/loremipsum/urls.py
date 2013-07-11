#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from loremipsum.views import *

urlpatterns = patterns('loremipsum.views',
                       url(r'^$', 'index'),
                       )
