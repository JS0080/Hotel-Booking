from __future__ import unicode_literals

from django.db import models

class Search(models.Model):
	keyword = models.CharField(max_length=100)
	frequency = models.IntegerField(default=0)
	image = models.CharField(max_length=500)
	lowest_price = models.CharField(max_length=50)
	lowest_points = models.CharField(max_length=50)

	def __unicode__(self):
		return self.keyword
