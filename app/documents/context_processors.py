#vim: set fileencoding=utf-8
from documents.models import *
from django.core.urlresolvers import reverse


def wire(request):
    """ Modifying the context of the request to ensure the required variables
    are passed on to the templates
    """
    user = request.user
    import_perm = user.has_perm('documents.can_import')
    export_perm = user.has_perm('documents.can_export')
    perms = user.has_perm('documents.can_see_admin')
    query_miss = Document.objects.filter(docstatus__status=Document.MISSING,
                                         docstatus__return_lend=False)
    query_miss = query_miss.order_by('-docstatus__date')
    return {'user': user,
            'perm': perms,
            'miss': query_miss[0:10],
            'import_perm': import_perm,
            'export_perm': export_perm,
            'menu_top': _create_menu(request),
            'menu_left': _create_navlist(request),
            }


def _create_navlist(request):
    navlist = []
    nav_urls = []
    nav_urls.append((u'', reverse('documents.index'), u'Home'))

    for url in nav_urls:
        html = u'<li class="%s"><a href="%s">%s</a></li>' % url
        navlist.append({u'html': html,
                        })
    return navlist


def _create_menu(request):
    return []
