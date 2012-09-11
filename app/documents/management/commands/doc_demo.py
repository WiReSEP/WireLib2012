#vim: set fileencoding=utf-8
from django.core.management.base import BaseCommand
#from optparse import make_option

from documents.extras_bibtex import UglyBibtex
import os

class Command(BaseCommand):
    help = "Hier kann der documents-App eine Demo-Session hinzugefügt werden"
    args = ""

    def handle(self, *args, **options):
        Command.__base_init()
        for file in os.listdir('olddb'):
            if file.__str__().endswith('.bib'):
                UglyBibtex('olddb/%s'%file).do_import()

    @staticmethod
    def __base_init():
        from documents import start_import
        start_import.importieren()
