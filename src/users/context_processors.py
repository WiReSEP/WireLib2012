from django.core.urlresolvers import reverse


def user_context(request):
    return add_fullpath(request)


def add_fullpath(request):
    path = request.get_full_path()

    is_logoutpage = reverse('users.logout') in path
    return {'fullpath': path,
            'is_logoutpage': is_logoutpage,
            }
