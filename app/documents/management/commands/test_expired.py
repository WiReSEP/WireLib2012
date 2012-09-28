#vim: set fileencoding=utf-8
from django.core.management.base import BaseCommand

import documents.lib.mails as mails

class Command(BaseCommand):
    help = "Sends mails to every lender of documents with expired lending date"
    args = "<max_days_lend>"

    def handle(self, *args, **options):
        if not max_days_lend:
            raise CommandError('Argument needed: max_days_lend')
        mails._document_expired_email(max_days_lend)
