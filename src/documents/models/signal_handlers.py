from __future__ import unicode_literals

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .document import Document, Author


@receiver(pre_delete, sender=Document)
def delete_authors(sender, instance, **kwargs):
    for author in (instance.get_authors() or instance.get_editors()):
        if len(author.document_set.all()) == 1:
            author.delete()


@receiver(pre_delete, sender=Document)
def delete_publisher(sender, instance, **kwargs):
    if len(instance.publisher.document_set.all()) == 1:
        instance.publisher.delete()


@receiver(pre_save, sender=Author)
def save_author(sender, instance, **kwargs):
    first_name = instance.first_name
    last_name = instance.last_name
    if first_name or last_name:
        instance.full_name = "%s %s" % (first_name, last_name)
    else:
        if instance.full_name:
            split = instance.full_name.split(' ', 1)
            if len(split) > 1:
                first_name = split[0]
                last_name = split[1]
            else:
                last_name = split[0]
            instance.first_name = first_name
            instance.last_name = last_name
