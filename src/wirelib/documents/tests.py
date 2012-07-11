"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test.client import Client
from django.utils import unittest

class SimpleTest(unittest.TestCase):
    def test_doc_details(self):
        c = Client()
        response = c.get('/doc_list/')
        self.assertEqual(response.status_code, 200)

#response = c.post('/login/', {'username': #'admin', 'password': 'sep2012'})
#response.status_code
    def test_sortlist(self):
        c = Client
        response = c.get('/doc_list/?&starts=g-i/')
        self.assertEqual(response.status_code, 200)   
    

