# coding: utf-8
import logging
import simple_audit
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User

LOG = logging.getLogger(__name__)

class Topping(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)

    def __unicode__(self):
        return self.name


class Pizza(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)
    toppings = models.ManyToManyField(Topping)

    def __unicode__(self):
        return self.name

    @staticmethod
    def set_friendly_description(audit):
        """
        Set friendly description depending of which fields has
        been changed
        TODO:
            Improve translation
        """
        def _add(audit):
            _("Object %(name)s added")
            return {
                "description": "Object %(name)s added",
                "vars": {"name": audit.content_object.name}
            }

        def _change(audit):
            _("Change %(name)s pizza")
            _("Foo's %(name)s")

            # option 1 - fields changed "name"
            options = [
                {
                    "fields_changed": set(["name"]),
                    "description": "Change %(name)s pizza",
                    "vars": {"name": audit.content_object.name}
                },
                {
                    "fields_changed": set(["foo"]),
                    "description": "Foo's %(name)s change",
                    "vars": {"name": audit.content_object.name}
                }
            ]
            fields_changed = set(
                [field.field for field in audit.field_changes.all()]
            )

            for option in options:
                if len(option["fields_changed"] - fields_changed) == 0:
                    return option

            return {}

        def _delete(audit):
            _("Object %(name)s deleted")
            return {
                "description": "Object %(name)s deleted",
                "vars": {"name": audit.content_object.name}
            }

        lookup = {
            audit.ADD: _add,
            audit.CHANGE: _change,
            audit.DELETE: _delete
        }

        option = lookup[audit.operation](audit)
        audit.friendly_description = option.get("description", "")
        audit.friendly_description_vars = option.get("vars", "")
        audit.save()


class Message(models.Model):

    title = models.CharField(max_length=50, blank=False)
    text = models.TextField(blank=False)

    def __unicode__(self):
        return self.text


class Owner(models.Model):

    name = models.CharField(max_length=50, blank=False)

    def __unicode__(self):
        return self.name


class VirtualMachine(models.Model):

    name = models.CharField(max_length=50, blank=False)
    cpus = models.IntegerField()
    owner = models.ForeignKey(Owner)
    so = models.CharField(max_length=100, blank=False)
    started = models.BooleanField()

    def __unicode__(self):
        return self.name


simple_audit.register(Message, Owner, VirtualMachine, User, Pizza, Topping)
