from django.conf.urls.defaults import *

urlpatterns = patterns('reviews.views',
    url(r'^post/$',          'post_review',       name='reviews-post-review'),
    url(r'^posted/$',        'review_done',       name='reviews-review-done'),
)

urlpatterns += patterns('',
    url(r'^cr/(\d+)/(.+)/$', 'django.contrib.contenttypes.views.shortcut', name='reviews-url-redirect'),
)
