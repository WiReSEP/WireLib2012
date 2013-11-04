#vim: set fileencoding=utf-8
import models


def wire(request):
    """ Modifying the context of the request to ensure the required variables
    are passed on to the templates
    """
    user = request.user
    query_miss = models.Document.objects.filter(docstatus__status=models.Document.MISSING,
                                                docstatus__return_lend=False)
    query_miss = query_miss.order_by('-docstatus__date')
    return {'user': user,
            'miss': query_miss[0:10],
            'menu_top': _create_menu(request),
            'menu_left': _create_navlist(request),
            }


def _create_navlist(request):
    from documents.views.navigation import NAV_LIST
    navlist = []

    for entry in NAV_LIST:
        if entry[2] and not request.user.has_perm(entry[2]):
            continue
        active_entry = ''
        css = ''
        if active_entry == entry[0]:
            css = 'active'
        url = (css, entry[0], entry[1])
        html = u'<li class="%s"><a href="%s">%s</a></li>' % url
        navlist.append({u'html': html,
                        })
    return navlist


def _create_menu(request):
    from documents.views.navigation import MENU_TOP
    menulist = []

    for entry in MENU_TOP:
        if entry[2] and not request.user.has_perm(entry[2]):
            continue
        css = ''
        url = (css, entry[0], entry[1])
        html = u'<li class="%s"><a href="%s">%s</a></li>' % url
        menulist.append({u'html': html,
                         })
    return menulist
