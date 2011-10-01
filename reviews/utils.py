"""
A few bits of helper functions for review views.
"""

import urllib
import textwrap
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
import reviews

def confirmation_view(template, doc="Display a confirmation view."):
    """
    Confirmation view generator for the "review was
    posted/flagged/deleted/approved" views.
    """
    def confirmed(request):
        review = None
        if 'c' in request.GET:
            try:
                review = reviews.get_model().objects.get(pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        return render_to_response(template,
            {'review': review},
            context_instance=RequestContext(request)
        )

    confirmed.__doc__ = textwrap.dedent("""\
        %s

        Templates: `%s``
        Context:
            review
                The posted review
        """ % (doc, template)
    )
    return confirmed
