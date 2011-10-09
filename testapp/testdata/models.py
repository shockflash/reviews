from django.conf import settings
from django.db import models
from reviews.models import Review, ReviewSegment

"""
These models extend the basic review models with new fields. You do not need to
do this, but you can do it.

Take a look at the forms.py, too.
Also visit the __init__.py.
This all works only if the REVIEW_APP value in settings.py is set to this app.

"""

class TestReview(Review):
    price = models.IntegerField()

class TestReviewSegment(ReviewSegment):
    title = models.CharField(max_length=200)

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

    @models.permalink
    def get_absolute_url(self):
        return ('car_detail', [str(self.id)])



class Restaurant(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('restaurant_detail', [str(self.id)])