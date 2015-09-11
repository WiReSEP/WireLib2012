# vim: set fileencoding=utf-8

from django.test import SimpleTestCase #TestCase

from django.test.client import Client

import logging

class public_pages(SimpleTestCase):
    """ Tests für alle Seiten aus der Sicht von Gästen.
    """

    def log(self, msg):
        logging.info(msg)
        
    def setUp(self):
        """ Initialisierung für die Tests
        """
        self.c = Client()

    def test_status_200(self):
        """Public URLs should return HTTP code 200.
        """
        urls = (
            '/',
            '/documents/',
            #'/doc/missed',
            '/documents/search/',
            #'/doc/K006001',
            #'/doc/K006002',
            '/users/login/',
            '/users/logout/',
        )
        for url in urls:
            self.log("checking: " + str(url))
            response = self.c.get(url)
            self.assertEqual(response.status_code, 200)

    def test_status_403(self):
        """URLs available after login should return HTTP code 403.
        """
        # was ist /doc/K.../assign?
        urls = (
            '/documents/new/',
            #'/doc/add',
            #'/doc/import',
            #'/doc/K006001/edit',
            #'/doc/K006002/edit',
            #'/export',
            #'/export/allegro',
            #'/export/bibtex',
            #'/user',
            #'/user/docs',
            #'/user/profile',
            #'/user/profile/edit',
            #'/user/settings',
        )
        for url in urls:
            self.log("checking: " + str(url))
            response = self.c.get(url)
            self.assertEqual(response.status_code, 403)


class private_pages(SimpleTestCase):
    """ Tests für alle Seiten aus der Sicht von angemelden Benutzern
    """
    pass
