#vim: set fileencoding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

# Die Menu Listen setzten sich aus drei Komponenten zusammen:
#  1. URL für das Linkziel
#  2. Text für den Link
#  3. Liste von Zugriffsrechten, die notwendig sind damit der Link angezeigt
#     wird. Ein Nutzer muss jedes der Zugriffsrechte besitzen, damit der Link
#     angezeigt wird.
#
# ACHTUNG: Das Verwenden von Zugriffsrechten hier schützt nicht vor
# unberechtigtem Zugriff. Sollen gewisse Rechte für den Zugriff auf die Seite
# notwendig sein, müssen diese im View selbst eingerichtet werden.

NAV_LIST = ((reverse('index'), 'Home', None),
            (reverse('documents.list'), 'Literaturverzeichnis', None),
            (reverse('documents.search'), 'Erweiterte Suche', None),
            (reverse('documents.new'), 'neue Dokumente', ('documents.add_document',)),
            (reverse('documents.export'), 'Export', ('documents.can_export',)),
            )

MENU_TOP = tuple()
