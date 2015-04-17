# vim: set fileencoding=utf-8

from django.utils import unittest

from django.test.client import Client

class public_pages(unittest.TestCase):
    """ Tests für alle Seiten aus der Sicht von Gästen.
    """

    def setUp(self):
        """ Initialisierung für die Tests
        """
        self.c = Client()

    def test_status_200(self):
        urls = ('/',
                '/doc',
                '/doc/missed',
                '/search',
                '/doc/K006001',
                '/doc/K006002',
                '/login',
                '/logout'
                )
        for url in urls:
            print "checking", url
            response = self.c.get(url)
            self.assertEqual(response.status_code, 200)

    def test_status_403(self):
        """ was ist /doc/K.../assign?
        """
        urls = ('/doc/add',
                '/doc/import',
                '/doc/K006001/edit',
                '/doc/K006002/edit',
                '/export',
                '/export/allegro',
                '/export/bibtex',
                '/user',
                '/user/docs',
                '/user/profile',
                '/user/profile/edit',
                '/user/settings',

                )
        for url in urls:
            print "checking", url
            response = self.c.get(url)
            self.assertEqual(response.status_code, 403)


class private_pages(unittest.TestCase):
    """ Tests für alle Seiten aus der Sicht von angemelden Benutzern
    """
    pass
