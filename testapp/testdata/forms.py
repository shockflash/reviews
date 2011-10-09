import time
import datetime

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from reviews.forms import ReviewForm, ReviewSegmentForm, REVIEW_MIN_RATING, REVIEW_MAX_RATING
from reviews.models import Category
from models import TestReview, TestReviewSegment

"""
These forms are used to extend the basic forms of the review app with additional
fields.
Take a look at the models.py, too.
"""

class TestReviewForm(ReviewForm):

    price   = forms.IntegerField()

    def get_review_model(self):
        return TestReview

    def get_segment_form(self):
        return TestReviewSegmentForm

    def get_review_create_data(self):
        """
        Returns the dict of data to be used to create a review. Subclasses in
        custom review apps that override get_review_model can override this
        method to add extra fields onto a custom review model.
        """
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            user_name    = self.cleaned_data["name"],
            user_email   = self.cleaned_data["email"],
            text         = self.cleaned_data["text"],
            title        = self.cleaned_data["title"],
            rating       = self.cleaned_data["rating"],
            price        = self.cleaned_data["price"],
            category     = Category.objects.get(code=self.cleaned_data["category"]),
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
        )

class TestReviewSegmentForm(ReviewSegmentForm):

    title    = forms.CharField(max_length=200)

    def get_segment_model(self):
        return TestReviewSegment

    def get_segment_create_data(self, categorysegment_id):
        """
        Returns the dict of data to be used to create a review. Subclasses in
        custom review apps that override get_review_model can override this
        method to add extra fields onto a custom review model.
        """

        # todo fill dict with right values
        return dict(
            segment_id = self.initial['categorysegment_id'],
            text = self.cleaned_data["text"],
            rating = self.cleaned_data["rating"],
            title = self.cleaned_data["title"],
        )