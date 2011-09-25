from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail

from testdata.models import TestModel1, TestModel2

urlpatterns = patterns('',
     (r'^$', direct_to_template, {'template': 'index.html'}),
     (r'^testmodel1/(?P<object_id>\d+)/$', object_detail, {
          'queryset': TestModel1.objects.all(),
          'template_name': 'entry.html'
        },
        'testmodel1_detail'),
     (r'^testmodel2/(?P<object_id>\d+)/$', object_detail, {
          'queryset': TestModel2.objects.all(),
          'template_name': 'entry.html'
        },
        'testmodel2_detail'),

     url(r'reviews/', include('reviews.urls')),
)
