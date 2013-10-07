from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .user import UserProfile
from .document import Document


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(pre_delete, sender=Document)
def delete_authors(sender, instance, **kwargs):
    for author in (instance.get_authors() or instance.get_editors()):
        if len(author.document_set.all()) == 1:
            author.delete()


@receiver(pre_delete, sender=Document)
def delete_publisher(sender, instance, **kwargs):
    if len(instance.publisher.document_set.all()) == 1:
        instance.publisher.delete()
