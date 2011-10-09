django-reviews
==============

The django-reviews app gives you an easy to use set of template-tags, models,
forms and admin integration to allow your site visitors to review any django
model instance (as long as you allow it).

Every reviews based has a basic text and sub-segments.
If you would review cars, you could have a basic text and segments for handling,
design and speed. Which segments are available is defined by the category and
the category segments. Category segments belongs to categorys, and which category
is to use is given as parameter in the template tags. See below for examples.

You can have as many categories as you like, with as many different category
segments as needed.

django-reviews based on the basic design of the django comment contrib.

Dependencies:
- django-classy-tags

Usage
-----

First, please take a look at the testapp that is part of this project. Run syncdb,
then use runserver to start the testapp. Admin is also provided, login is
user "admin" and password "admin.

The template "testapp/templates/entry.html" shows the usage of the template
tags to write new reviews for an instance. It also shows how to use the tags
to retrieve a list of reviews for the instance.

Template tags
-------------

get_review_count
****************
Retrieve the count of reviews for an object

Examples:
{% get_review_count for entry %}
{% get_review_count for entry as review_count %}

render_review_list
******************
Renders a list of reviews for an object

Examples:
{% render_review_list for event %}
{% render_review_list for event offset 10 limit 5 %}
{% render_review_list for event offset 10 limit 5 with "template2.html" %}

get_review_list
***************
Retrieve a list of reviews for an object. You need to assign it to a variable
with "as"

Example:
{% get_review_list for event as review_list %}

render_review_form
******************
Renders the review form

Examples:
{% render_review_form for event category "car" %}
{% render_review_form for event category "car" with "templateexample.html" %}

get_review_form
***************
Retrieve the review form.  You need to assign it to a variable with "as"

Example:
{% get_review_form for event category "car" as form %}

Extend
------

You can extend and change the behaviour of the django-review app by writing your
own app on top of it, which replaces the form, models and views.

Please have a look at the __init__.py file in the reviews directory. The system
is the same as in the comments application.

The testdata-app also contains an example, it extends the Review and ReviewSegmet
models with one new field each. The forms are also changed.
The templates in the testapp are using these fields.
