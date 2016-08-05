# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse

# Create your models here.

class Host(models.Model):
	 ip = models.GenericIPAddressField(db_index=True)
	 hostname = models.CharField(max_length=100)
	 group = models.CharField(max_length=20)
	 create_time = models.DateTimeField(auto_now_add = True)
         
         def __unicode__(self):
		return self.hostname
