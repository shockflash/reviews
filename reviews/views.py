from django import http
from django.conf import settings
from django.contrib.comments.views.utils import next_redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from reviews.utils import confirmation_view
from reviews import signals, signing
import reviews



class ReviewPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a review post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(ReviewPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("reviews/400-debug.html", {"why": why})

@csrf_protect
@require_POST
def post_review(request, next=None, using=None):
    """
    Post a review.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``reviews/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object we're trying to review about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return ReviewPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return ReviewPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return ReviewPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return ReviewPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return ReviewPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))

    # Do we want to preview the review?
    preview = "preview" in data

    category = signing.loads(data['category'])

    # Construct the review form
    form = reviews.get_form()(target, data=data, category=category)

    # Check security information
    if form.security_errors():
        return ReviewPostBadRequest(
            "The review form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the review
    if form.errors or not form.formset.is_valid() or preview:
        template_list = [
            # Now the usual directory based template heirarchy.
            "reviews/%s/%s/preview.html" % (model._meta.app_label, model._meta.module_name),
            "reviews/%s/preview.html" % model._meta.app_label,

            # like before, but with optional different template per category
            "reviews/%s/%s/preview_%s.html" % (model._meta.app_label, model._meta.module_name, category),
            "reviews/%s/preview_%s.html" % (model._meta.app_label, category),
            "reviews/preview_%s.html" % category,

            "reviews/preview.html",
        ]
        return render_to_response(
            template_list, {
                "review" : form.data.get("review", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
        )

    # Otherwise create the review
    review = form.get_review_object()
    review.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        review.user = request.user

    # get the segments
    segments = form.get_segment_objects()

    # Signal that the review is about to be saved
    responses = signals.review_will_be_posted.send(
        sender  = review.__class__,
        review = review,
        segments = segments,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return ReviewPostBadRequest(
                "review_will_be_posted receiver %r killed the review" % receiver.__name__)

    # Save the review and signal that it was saved
    review.save()
    for segment in segments:
        segment.review = review
        segment.save()

    signals.review_was_posted.send(
        sender  = review.__class__,
        review = review,
        request = request
    )

    return next_redirect(data, next,review_done, c=review._get_pk_val())

review_done = confirmation_view(
    template = "reviews/posted.html",
    doc = """Display a "review was posted" success page."""
)
