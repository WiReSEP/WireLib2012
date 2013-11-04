#vim: set fileencoding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

NAV_LIST = ((reverse('index'), 'Home', None),
            (reverse('documents.list'), 'Literaturverzeichnis', None),
            (reverse('documents.search'), 'Erweiterte Suche', None),
            )

MENU_TOP = tuple()
