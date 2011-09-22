from django import template
from classytags.core import Tag, Options
from classytags.arguments import Argument

register = template.Library()

class BaseHandler(Tag):
    options = Options(
        'for',
        Argument('name'),
        'category',
        Argument('category', required=False, resolve=False),
        'offset',
        Argument('offset', required=False, resolve=False),
        'limit',
        Argument('limit', required=False, resolve=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )


    def render(self, context):
        items = self.kwargs.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)

        # do something generic with the data
        kwargs['name'] = kwargs['name'] + ' test'

        return self.render_tag(context, **kwargs)

class Hello(BaseHandler):
    name = 'hello'

    def render_tag(self, context, name, varname, category = False, offset = False, limit = False ):
        output = 'hello %s' % name

        if category:
            output += " category %s" % category

        if offset:
            output += " offset %s" % offset

        if limit:
            output += " limit %s" % limit

        if varname:
            context[varname] = output
            return ''
        else:
            return output

register.tag(Hello)