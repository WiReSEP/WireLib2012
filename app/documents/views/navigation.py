#vim: set fileencoding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

NAV_LIST = (('', reverse('index'), 'Home'),
            ('', reverse('documents.list'), 'Literaturverzeichnis'),
            )

MENU_TOP = ()
