from django.conf import settings
from django.db import models

"""
These are test models. They are used to show how reviews are assigned to models.
Please look at the "entry.html" to see how this works.

Like the comments you need to combine your models and the review system in the
templates.

The models itself are not important, we have two to show that the system can
do this.
"""

class Car(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name