import time
import datetime

from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.text import get_text_list
from django.utils.translation import ungettext, ugettext_lazy as _
from django.forms.formsets import formset_factory
from reviews.models import Review, ReviewSegment, Category, CategorySegment
from reviews import signing

REVIEW_MAX_LENGTH = getattr(settings,'REVIEW_MAX_LENGTH', 3000)
REVIEWS_ALLOW_PROFANITIES = getattr(settings,'REVIEWS_ALLOW_PROFANITIES', False)

class SignedCharField(forms.CharField):
    """
    SignedCharField is a normal char field, but the content is signed with
    the django Signer to prevent manipulation. Best used together with
    """

    def prepare_value(self, value):
        # test if the value is already signed. if yes, we do not resign it
        try:
            signing.loads(value)
            return value
        except signing.BadSignature:
            return signing.dumps(value)

    def to_python(self, value):
        """ a broken/manipulated value will raise an exception of
        type signing.BadSignature. We do not catch it, it should raise """

        original = signing.loads(value)
        return original

def clean_text(text):
    """
    If REVIEWS_ALLOW_PROFANITIES is False, check that the review doesn't
    contain anything in PROFANITIES_LIST.
    """
    if REVIEWS_ALLOW_PROFANITIES == False:
        bad_words = [w for w in settings.PROFANITIES_LIST if w in text.lower()]
        if bad_words:
            plural = len(bad_words) > 1
            raise forms.ValidationError(ungettext(
                "Watch your mouth! The word %s is not allowed here.",
                "Watch your mouth! The words %s are not allowed here.", plural) % \
                get_text_list(['"%s%s%s"' % (i[0], '-'*(len(i)-2), i[-1]) for i in bad_words], 'and'))
    return text

class ReviewSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for review forms.
    """

    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_pk     = forms.CharField(widget=forms.HiddenInput)
    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None, category=None):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial['category'] = category
        initial.update(self.generate_security_data())

        """ the category of this review. Needed for the form set """
        self.category = category

        super(ReviewSecurityForm, self).__init__(data=data, initial=initial)

    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ErrorDict()
        for f in ["honeypot", "timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            'content_type' : self.data.get("content_type", ""),
            'object_pk' : self.data.get("object_pk", ""),
            'timestamp' : self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            # Fallback to Django 1.2 method for compatibility
            # PendingDeprecationWarning <- here to remind us to remove this
            # fallback in Django 1.5
            expected_hash_old = self._generate_security_hash_old(**security_hash_dict)
            if not constant_time_compare(expected_hash_old, actual_hash):
                raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'content_type'  : str(self.target_object._meta),
            'object_pk'     : str(self.target_object._get_pk_val()),
            'timestamp'     : str(timestamp),
            'security_hash' : self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        initial_security_dict = {
            'content_type' : str(self.target_object._meta),
            'object_pk' : str(self.target_object._get_pk_val()),
            'timestamp' : str(timestamp),
          }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp)
        key_salt = "django.contrib.forms.ReviewSecurityForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()

    def _generate_security_hash_old(self, content_type, object_pk, timestamp):
        """Generate a (SHA1) security hash from the provided info."""
        # Django 1.2 compatibility
        info = (content_type, object_pk, timestamp, settings.SECRET_KEY)
        return sha_constructor("".join(info)).hexdigest()

class ReviewDetailsForm(ReviewSecurityForm):
    """
    Handles the specific details of the review (name, review, etc.).
    """
    name          = forms.CharField(label=_("Name"), max_length=50)
    email         = forms.EmailField(label=_("Email address"))
    text          = forms.CharField(label=_('Review'), widget=forms.Textarea,
                                    max_length=REVIEW_MAX_LENGTH)

    """ SignedCharField is used to hold the category value, but with a digital
    signature attached. This way we can route it through the form, but can be
    sure that it is not changed. If not done this way, the user could change the
    category of the review, which is not good """
    category      = SignedCharField(max_length=200, widget=forms.HiddenInput)

    def get_review_object(self):
        """
        Return a new (unsaved) review object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_review_object may only be called on valid forms")

        ReviewModel = self.get_review_model()
        new = ReviewModel(**self.get_review_create_data())
        new = self.check_for_duplicate_review(new)

        return new

    def get_review_model(self):
        """
        Get the review model to create with this form. Subclasses in custom
        review apps should override this, get_review_create_data, and perhaps
        check_for_duplicate_review to provide custom review models.
        """
        return Review

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
            category     = Category.objects.get(code=self.cleaned_data["category"]),
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
        )

    def get_segment_formset(self):
        cat = Category.objects.get(code=self.category)

        initial = []
        for segment in cat.categorysegment_set.order_by('position'):
            initial.append({
                  'segment_pk': segment.id,
                  'text': ''
                })

        ReviewSegmentFormSet = formset_factory(ReviewSegmentForm, extra=0)
        formset = ReviewSegmentFormSet(initial=initial)

        return formset

    def check_for_duplicate_review(self, new):
        """
        Check that a submitted review isn't a duplicate. This might be caused
        by someone posting a review twice. If it is a dup, silently return the *previous* review.
        """
        possible_duplicates = self.get_review_model()._default_manager.using(
            self.target_object._state.db
        ).filter(
            content_type = new.content_type,
            object_pk = new.object_pk,
            user_name = new.user_name,
            user_email = new.user_email,
        )
        for old in possible_duplicates:
            if old.submit_date.date() == new.submit_date.date() and old.review == new.review:
                return old

        return new

    def clean_text(self):
        return clean_text(self.cleaned_data["text"])

class ReviewForm(ReviewDetailsForm):
    honeypot      = forms.CharField(required=False,
                                    label=_('If you enter anything in this field '\
                                            'your review will be treated as spam'))

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value

class ReviewSegmentBaseForm(forms.Form):
    segment_pk     = forms.CharField(widget=forms.HiddenInput)

    def get_categorysegment(self):
        """
        Gives the category segment for this form.
        Can be used to show the title of the category segment and load other
        data related to it.
        """
        if 'segment' in self:
            return self.segment

        self.segment = CategorySegment.objects.get(pk=self.initial['segment_pk'])
        return self.segment

class ReviewSegmentForm(ReviewSegmentBaseForm):
    rating = forms.IntegerField(label=_('Rating'))
    text   = forms.CharField(label=_('Review'), widget=forms.Textarea,
                            max_length=REVIEW_MAX_LENGTH)

    def clean_text(self):
        return clean_text(self.cleaned_data["text"])
