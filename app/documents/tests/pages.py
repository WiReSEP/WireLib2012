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

    def test_index(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_doclists(self):
        urls = ('/doc', 
                '/doc/missed'
                )
        for url in urls:
            print "checking",url
            response = self.c.get(url)
            self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.c.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_docs(self):
        pass


class private_pages(unittest.TestCase):
    """ Tests für alle Seiten aus der Sicht von angemelden Benutzern
    """

    pass
