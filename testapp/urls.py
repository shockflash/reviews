from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail
from reviews.models import Review
from testdata.models import Car, Restaurant

urlpatterns = patterns('',
     (r'^$', direct_to_template, {'template': 'index.html'}, 'index'),

     # view for a single car
     (r'^car/(?P<object_id>\d+)/$', object_detail, {
          'queryset': Car.objects.all(),
          'template_name': 'entry.html',
          'extra_context': {'cat': 'Car'}
        },
        'car_detail'),

     # view for a single restaurant. same template as the car, since it is
     # not important here / contains the same information.
     # Remember this is an example, a real live application can differ here, if
     # needed.
     (r'^restaurant/(?P<object_id>\d+)/$', object_detail, {
          'queryset': Restaurant.objects.all(),
          'template_name': 'entry.html',
          'extra_context': {'cat': 'Restaurant'}
        },
        'restaurant_detail'),

     # shows a detailed view of one single review
     (r'^review/(?P<object_id>\d+)/$', object_detail, {
          'queryset': Review.objects.all(),
          'template_name': 'review.html',
        },
        'review_detail'),


     url(r'reviews/', include('reviews.urls')),
)
