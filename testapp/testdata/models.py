from django.conf import settings
from django.db import models

class TestModel1(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name


class TestModel2(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name