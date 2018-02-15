from __future__ import unicode_literals

from django.db import models

class User(models.Model):
	name = models.CharField(max_length=250)
	email = models.EmailField(max_length=250)
	account = models.BooleanField()
	password = models.CharField(max_length=260)
	org_Events = models.CharField(max_length=2000)
	part_Events = models.CharField(max_length=2000)

	def join_event(self, event_ID):
		# assuming the list is going to be a CSV
		part_Events = self.part_Events + event_ID + ","

class Event(models.Model):
	name = models.CharField(max_length=250)
	organizer = models.ForeignKey(User)
	ideal_group_size = models.IntegerField()
	allow_projects = models.BooleanField()
	allow_voting = models.BooleanField()
	participants = models.CharField(max_length=2000)
	project_ideas = models.CharField(max_length=2000)
	groups = models.CharField(max_length=2000)
