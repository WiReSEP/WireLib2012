#vim: set fileencoding=utf-8
from django.conf.urls import patterns, url
from users import views

urlpatterns = patterns('django.contrib.auth.views',
                       url(r'^login/$',
                           'login',
                           {'template_name': 'users/login.html'},
                           name='users.login'),
                       url(r'^logout/$',
                           'logout',
                           {'template_name': 'users/logout.html'},
                           name='users.logout'),
                       url(r'^password/change/$',
                           'password_change',
                           {'template_name': 'users/password_change.html'},
                           name='users.password.change'),
                       url(r'^password/change/done/$',
                           'password_change_done',
                           {'template_name': 'users/password_change_done.html'},
                           name='users.password.change.done'),
                       )

urlpatterns += patterns('users.views',
                        url(r'^edit/$',
                            views.UserEdit.as_view(),
                            name='users.edit'),
                        url(r'^(?P<username>[\w@.+-]{0,30})/$',
                            views.UserProfile.as_view(),
                            name='users.profile'),
                        )
