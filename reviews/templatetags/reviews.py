from django import template

register = template.Library()

class BaseCommentNode(template.Node):

    @classmethod
    def handle_token(cls, parser, token):
        pass

class ReviewCountNode(BaseCommentNode):
    """Insert a count of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()

@register.tag
def get_review_count(parser, token):
    """
    Gets the review count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_review_count for [object] as [varname]  %}
        {% get_review_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_count for event as comment_count %}
        {% get_comment_count for calendar.event event.id as comment_count %}
        {% get_comment_count for calendar.event 17 as comment_count %}

    """
    return ReviewCountNode.handle_token(parser, token)


# {% get_review_form for [object] type [blabla] as [varname] %}
