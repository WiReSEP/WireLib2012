from __future__ import unicode_literals

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .document import Document


@receiver(pre_delete, sender=Document)
def delete_authors(sender, instance, **kwargs):
    for author in (instance.get_authors() or instance.get_editors()):
        if len(author.document_set.all()) == 1:
            author.delete()


@receiver(pre_delete, sender=Document)
def delete_publisher(sender, instance, **kwargs):
    if len(instance.publisher.document_set.all()) == 1:
        instance.publisher.delete()
