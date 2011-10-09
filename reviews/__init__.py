from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from reviews.models import Review
from forms import ReviewForm
from django.utils.importlib import import_module

DEFAULT_REVIEWS_APP = 'reviews'

def get_review_app():
    """
    Get the reviews app (i.e. "reviews") as defined in the settings
    """
    # Make sure the app's in INSTALLED_APPS
    reviews_app = get_review_app_name()
    if reviews_app not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("The REVIEWS_APP (%r) "\
                                   "must be in INSTALLED_APPS" % settings.REVIEWS_APP)

    # Try to import the package
    try:
        package = import_module(reviews_app)
    except ImportError:
        raise ImproperlyConfigured("The REVIEWS_APP setting refers to "\
                                   "a non-existing package.")

    return package

def get_review_app_name():
    """
    Returns the name of the review app (either the setting value, if it
    exists, or the default).
    """
    return getattr(settings, 'REVIEWS_APP', DEFAULT_REVIEWS_APP)

def get_model():
    """
    Returns the review model class.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_model"):
        return get_review_app().get_model()
    else:
        return Review

def get_segment_model():
    """
    Returns the review model class.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_segment_model"):
        return get_review_app().get_segment_model()
    else:
        return ReviewSegment

def get_form():
    """
    Returns the review ModelForm class.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_form"):
        return get_review_app().get_form()
    else:
        return ReviewForm

def get_segment_form():
    """
    Returns the review ModelForm class.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_segment_form"):
        return get_review_app().get_segment_form()
    else:
        return ReviewSegmentForm

def get_form_target():
    """
    Returns the target URL for the review form submission view.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_form_target"):
        return get_review_app().get_form_target()
    else:
        return urlresolvers.reverse("reviews-post-review")
        #return urlresolvers.reverse("reviews.views.reviews.post_review")

def get_flag_url(review):
    """
    Get the URL for the "flag this review" view.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_flag_url"):
        return get_review_app().get_flag_url(review)
    else:
        return urlresolvers.reverse("reviews.views.moderation.flag",
                                    args=(review.id,))

def get_delete_url(review):
    """
    Get the URL for the "delete this review" view.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_delete_url"):
        return get_review_app().get_delete_url(review)
    else:
        return urlresolvers.reverse("reviews.views.moderation.delete",
                                    args=(review.id,))

def get_approve_url(review):
    """
    Get the URL for the "approve this review from moderation" view.
    """
    if get_review_app_name() != DEFAULT_REVIEWS_APP and hasattr(get_review_app(), "get_approve_url"):
        return get_review_app().get_approve_url(review)
    else:
        return urlresolvers.reverse("reviews.views.moderation.approve",
                                    args=(review.id,))
