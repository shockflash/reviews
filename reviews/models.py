import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from reviews.managers import ReviewManager

REVIEW_MAX_LENGTH = getattr(settings,'REVIEW_MAX_LENGTH',3000)

class Category(models.Model):
    code = models.CharField(_('category code'), max_length = 200)

    class Meta:
        verbose_name = _('review category')
        verbose_name_plural = _('review categories')

class CategorySegment(models.Model):
    title    = models.CharField(max_length = 200)
    category = models.ForeignKey(Category)

    class Meta:
        verbose_name = _('review category segment')
        verbose_name_plural = _('review category segments')

class BaseReviewAbstractModel(models.Model):
    """
    An abstract base class that any custom review models probably should
    subclass.
    """

    # Content-object field
    content_type   = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="content_type_set_for_%(class)s")
    object_pk      = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    # Metadata about the review
    site        = models.ForeignKey(Site)

    class Meta:
        abstract = True

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "reviews-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )

class Review(BaseReviewAbstractModel):
    """
    A user wrote a review about some object.
    """

    # Who posted this review? If ``user`` is set then it was an authenticated
    # user; otherwise at least user_name should have been set and the review
    # was posted by a non-authenticated user.
    user        = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_reviews")
    user_name   = models.CharField(_("user's name"), max_length=50, blank=True)
    user_email  = models.EmailField(_("user's email address"), blank=True)

    text = models.TextField(_('review'), max_length=REVIEW_MAX_LENGTH)

    # Metadata about the review
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    ip_address  = models.IPAddressField(_('IP address'), blank=True, null=True)
    is_public   = models.BooleanField(_('is public'), default=True,
                    help_text=_('Uncheck this box to make the review effectively ' \
                                'disappear from the site.'))
    is_removed  = models.BooleanField(_('is removed'), default=False,
                    help_text=_('Check this box if the review is inappropriate. ' \
                                'A "This review has been removed" message will ' \
                                'be displayed instead.'))

    # Manager
    objects = ReviewManager()

    class Meta:
        ordering = ('submit_date',)
        permissions = [("can_moderate", "Can moderate reviews")]
        verbose_name = _('review')
        verbose_name_plural = _('reviews')

    def __unicode__(self):
        return "%s: %s..." % (self.name, self.text [:50])

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(Review, self).save(*args, **kwargs)

    def _get_userinfo(self):
        """
        Get a dictionary that pulls together information about the poster
        safely for both authenticated and non-authenticated reviews.

        This dict will have ``name`` and ``email`` fields.
        """
        if not hasattr(self, "_userinfo"):
            self._userinfo = {
                "name"  : self.user_name,
                "email" : self.user_email
            }
            if self.user_id:
                u = self.user
                if u.email:
                    self._userinfo["email"] = u.email

                # If the user has a full name, use that for the user name.
                # However, a given user_name overrides the raw user.username,
                # so only use that if this review has no associated name.
                if u.get_full_name():
                    self._userinfo["name"] = self.user.get_full_name()
                elif not self.user_name:
                    self._userinfo["name"] = u.username
        return self._userinfo
    userinfo = property(_get_userinfo, doc=_get_userinfo.__doc__)


    def _get_email(self):
        return self.userinfo["email"]
    def _set_email(self, val):
        if self.user_id:
            raise AttributeError(_("This review was posted by an authenticated "\
                                   "user and thus the email is read-only."))
        self.user_email = val
    email = property(_get_email, _set_email, doc="The email of the user who posted this review")

    def get_absolute_url(self, anchor_pattern="#c%(id)s"):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)

    def get_as_text(self):
        """
        Return this review as plain text.  Useful for emails.
        """
        d = {
            'user': self.user or self.name,
            'date': self.submit_date,
            'text': self.text,
            'domain': self.site.domain,
            'url': self.get_absolute_url()
        }
        return _('Posted by %(user)s at %(date)s\n\n%(review)s\n\nhttp://%(domain)s%(url)s') % d

class ReviewFlag(models.Model):
    """
    Records a flag on a review. This is intentionally flexible; right now, a
    flag could be:

        * A "removal suggestion" -- where a user suggests a review for (potential) removal.

        * A "moderator deletion" -- used when a moderator deletes a review.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a review with a given flag once;
    if you want rating look elsewhere.
    """
    user      = models.ForeignKey(User, verbose_name=_('user'), related_name="review_flags")
    review    = models.ForeignKey(Review, verbose_name=_('review'), related_name="flags")
    flag      = models.CharField(_('flag'), max_length=30, db_index=True)
    flag_date = models.DateTimeField(_('date'), default=None)

    # Constants for flag types
    SUGGEST_REMOVAL = "removal suggestion"
    MODERATOR_DELETION = "moderator deletion"
    MODERATOR_APPROVAL = "moderator approval"

    class Meta:
        unique_together = [('user', 'review', 'flag')]
        verbose_name = _('review flag')
        verbose_name_plural = _('review flags')

    def __unicode__(self):
        return "%s flag of review ID %s by %s" % \
            (self.flag, self.review_id, self.user.username)

    def save(self, *args, **kwargs):
        if self.flag_date is None:
            self.flag_date = datetime.datetime.now()
        super(ReviewFlag, self).save(*args, **kwargs)


class ReviewSegment(models.Model):
    """
    Every review has a base-text, and in addition to this it can have multiple segments.
    Each segment has an own text and an own
    """
    review    = models.ForeignKey(Review, verbose_name=_('review'), related_name="segments")
    rating    = models.IntegerField(_('rating'))
    text      = models.TextField(_('review text'), max_length=REVIEW_MAX_LENGTH)
    segment   = models.ForeignKey(CategorySegment, verbose_name=_('review category segment'))

    class Meta:
        verbose_name = _('review segment')
        verbose_name_plural = _('review segments')
