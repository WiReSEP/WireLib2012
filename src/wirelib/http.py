# vim: set fileencoding=utf-8
""" Custom error handler. """
from __future__ import unicode_literals
from django import http
from django import template


class MessagedServerError(Exception):

    """ Raise Error 500 with a custom message.

    This error just needs to be raised and the Errormessage will be printed to
    the user.
    """


class ServerErrorHandlerMiddleware(object):

    """ Middleware that processes the MessagedServerError. """

    def process_exception(self, request, exception):
        """ Called in case of an exception. """
        if not isinstance(exception, MessagedServerError):
            return None
        t = template.loader.get_template('500.html')
        context = template.context.Context({'detail': "%s" % exception})
        return http.HttpResponseServerError(t.render(context))
