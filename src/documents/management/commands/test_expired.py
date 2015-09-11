#vim: set fileencoding=utf-8
from django.core.management.base import BaseCommand, CommandError

import documents.lib.mails as mails

class Command(BaseCommand):
    help = "Sends mails to every lender of documents with expired lending date"
    args = "<max_days_lend>"

    def handle(self, *args, **options):
        if len(args)<1:
            raise CommandError('Argument needed: max_days_lend')
        print args
        max_days_lend = float(args[0])
        mails._document_expired_email(max_days_lend)
