from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('documents.views',
        url(r'^$', 'main')
)
