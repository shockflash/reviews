"""
Signals relating to reviews.
"""
from django.dispatch import Signal

# Sent just before a review will be posted (after it's been approved and
# moderated; this can be used to modify the review (in place) with posting
# details or other such actions. If any receiver returns False the review will be
# discarded and a 403 (not allowed) response. This signal is sent at more or less
# the same time (just before, actually) as the Review object's pre-save signal,
# except that the HTTP request is sent along with this signal.
review_will_be_posted = Signal(providing_args=["review", "segments", "request"])

# Sent just after a review was posted. See above for how this differs
# from the Review object's post-save signal.
review_was_posted = Signal(providing_args=["review", "segments", "request"])

# Sent after a review was "flagged" in some way. Check the flag to see if this
# was a user requesting removal of a review, a moderator approving/removing a
# review, or some other custom user flag.
review_was_flagged = Signal(providing_args=["review", "flag", "created", "request"])
