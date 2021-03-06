from django.conf import settings
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode
from django.template.loader import render_to_string
from classytags.core import Tag, Options
from classytags.arguments import Argument
import reviews

"""
the file was named reviews.py at start, but needed to be renamed reviewtags.py
because of import problems.
"""

register = template.Library()

class BaseHandler(Tag):
    """
    Base class used by all review template tags. Defines the parameters and
    do the basic parsing & object handling.

    The tag-parsing is done by django-classy-tags. After it parses the tag
    it will call the render() function, which is/are defined in the sub-classes
    of the BaseHandler. So don't look for it in this class, you won't find it.
    """

    options = Options(
        'for',      Argument('name'),
        'category', Argument('category', required=False),

        # used in rendering lists
        'offset',   Argument('offset', required=False),
        'limit',    Argument('limit', required=False),

        # used in render_* to set the template
        'with',     Argument('with', required=False, resolve=False),

        'as',       Argument('varname', required=False, resolve=False)
    )

    def get_target_ctype_pk(self, context, object_expr):
        return ContentType.objects.get_for_model(object_expr), object_expr.pk

    def get_query_set(self, context, model, ctype, object_expr):
        ctype, object_pk = self.get_target_ctype_pk(context, object_expr)
        if not object_pk:
            return model.objects.none()

        qs = model.objects.filter(
            content_type = ctype,
            object_pk    = smart_unicode(object_pk),
            site__pk     = settings.SITE_ID,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in review model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'REVIEWS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)

        qs = qs.order_by('-id')

        return qs

    def handle_result(self, context, kwargs, rs):
        """
        if "as" was used, we fill the value into this variable
        """

        if kwargs.has_key('varname') and kwargs['varname']:
            context[kwargs['varname']] = rs
            return ''
        else:
            return rs

class ListHandler(BaseHandler):
    """
    Extends BaseHandler by creating the queryset used in all list-based tags
    """

    def render(self, context):
        # resolv kwargs values
        items = self.kwargs.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)

        ctype = self.get_target_ctype_pk(context, kwargs['name'])
        qs = self.get_query_set(context, reviews.get_model(), ctype, kwargs['name'])

        rs = self.render_tag(context, qs)
        return self.handle_result(context, kwargs, rs)

class RenderListHandler(BaseHandler):
    """
    Extends BaseHandler by creating the queryset used in all list-based tags
    """

    def render(self, context):
        # resolv kwargs values
        items = self.kwargs.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)

        ctype = self.get_target_ctype_pk(context, kwargs['name'])
        qs = self.get_query_set(context, reviews.get_model(), ctype, kwargs['name'])

        template = []
        if 'with' in kwargs:
            template.append(kwargs['with'])

        rs = self.render_tag(context, kwargs['name'], kwargs['category'], qs, template)
        return self.handle_result(context, kwargs, rs)

class EntryHandler(BaseHandler):

    def render(self, context):
        # resolv kwargs values
        items = self.kwargs.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)

        rs = self.render_tag(context, kwargs['name'], kwargs['category'])
        return self.handle_result(context, kwargs, rs)

class RenderEntryHandler(BaseHandler):

    def render(self, context):
        # resolv kwargs values
        items = self.kwargs.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)

        template = []
        if 'with' in kwargs:
            template.append(kwargs['with'])

        rs = self.render_tag(context, kwargs['name'], kwargs['category'], template)
        return self.handle_result(context, kwargs, rs)


# ----------------------------------------


class GetReviewCount(ListHandler):
    """
    Counts the reviews for one object.
    """

    name = 'get_review_count'

    def render_tag(self, context, qs):
        return qs.count()

class GetReviewList(ListHandler):
    """
    returns the queryset for all reviews of an object
    """

    name = 'get_review_list'

    def render_tag(self, context, qs):
        return qs.all()

class GetReviewtForm(EntryHandler):
    """
    returns a ReviewForm instance
    """

    name = 'get_review_form'

    def render_tag(self, context, object_expr, category):
        return reviews.get_form()(object_expr, category=category)

class RenderReviewForm(RenderEntryHandler):
    """
    renders the review form, looks for different locations of the form html
    file
    """

    name = 'render_review_form'


    def render_tag(self, context, object_expr, category, template_search_list = []):
        ctype, object_pk = self.get_target_ctype_pk(context, object_expr)
        if object_pk:
            template_search_list.extend([
                # classic comments like
                "reviews/%s/%s/form.html" % (ctype.app_label, ctype.model),
                "reviews/%s/form.html" % ctype.app_label,

                # like before, but with optional different template per category
                "reviews/%s/%s/form_%s.html" % (ctype.app_label, ctype.model, category),
                "reviews/%s/form_%s.html" % (ctype.app_label, category),
                "reviews/form_%s.html" % category,

                "reviews/form.html"
            ])
            context.push()
            formstr = render_to_string(template_search_list, {
                    "form" : reviews.get_form()(object_expr, category=category)
                }, context)
            context.pop()
            return formstr
        else:
            return ''

class RenderReviewList(RenderListHandler):
    """
    returns a rendered list of all reviews of a list
    """

    name = 'render_review_list'

    def render_tag(self, context, object_expr, category, qs, template_search_list = [], offset = None, limit = None):
        ctype, object_pk = self.get_target_ctype_pk(context, object_expr)
        template_search_list.extend([
            # classic comments like
            "reviews/%s/%s/folistrm.html" % (ctype.app_label, ctype.model),
            "reviews/%s/list.html" % ctype.app_label,

            # like before, but with optional different template per category
            "reviews/%s/%s/list_%s.html" % (ctype.app_label, ctype.model, category),
            "reviews/%s/list_%s.html" % (ctype.app_label, category),
            "reviews/list_%s.html" % category,

            "reviews/list.html"
        ])

        context.push()
        liststr = render_to_string(template_search_list, {
                    "object": object_expr,
                    "category": category,
                    "review_list" : qs.all()
                  }, context)
        context.pop()
        return liststr


@register.simple_tag
def review_form_target():
    """
    Get the target URL for the reviews form.

    Example::

        <form action="{% review_form_target %}" method="post">
    """
    return reviews.get_form_target()

register.tag(GetReviewCount)
register.tag(GetReviewList)
register.tag(RenderReviewList)
register.tag(GetReviewtForm)
register.tag(RenderReviewForm)

# TODO
# get_review_toplist
# render_review_toplist