# vim: set fileencoding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractUser as AuthUser
from django.contrib.auth.models import UserManager
import subprocess


class User(AuthUser):
    afs_user = models.BooleanField("TU Benutzer (GITZ)", default=False)
    street = models.CharField("Straße", max_length=30, blank=True)
    number = models.CharField("Hausnummer", max_length=5, blank=True)
    zipcode = models.CharField("Postleitzahl", max_length=10, blank=True)
    city = models.CharField("Stadt", max_length=58, blank=True)
    phone_number = models.CharField("Telefonnummer", max_length=60, blank=True)

    objects = UserManager()

    def check_password(self, raw_password):
        """ Check if the user can be authenticated with the given password. """
        if not self.afs_user:
            return super(User, self).check_password(raw_password)

        # AFS can be used to authenticate the user. This method will only be
        # used if the user defined like that.
        afs_auth = subprocess.call(['/usr/bin/klog',
                                    '-principal', self.username,
                                    '-password', raw_password])
        return afs_auth == 0

    class Meta:
        app_label = 'users'
        permissions = (('can_see_admin', 'Can see the adminpanel'),)
        verbose_name = 'Benutzer'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        name = self.get_full_name()
        if not name:
            name = self.username
        return u'%s' % name

    def get_absolute_url(self):
        return reverse('users.profile', kwargs={'username': self.username})
