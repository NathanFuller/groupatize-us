from __future__ import unicode_literals
from hashlib import sha3_256
from django.db import models


class User(models.Model):
	name = models.CharField(max_length=250)
	email = models.EmailField(max_length=250)
	account = models.BooleanField(default=False)
	password = models.CharField(max_length=260, default="")
	org_Events = models.CharField(max_length=2000, default="")
	part_Events = models.CharField(max_length=2000, default="")

	def join_event(self, event_ID):
		# assuming the list is going to be a CSV
		self.part_Events = self.part_Events + "," + event_ID
		# save
		self.save()

	# get all the events the user is a participant of in list form
	def get_participant_events(self):
		return self.part_Events.split(",")[1:]

	# if you get compile error on sha3_256() try installing pysha3 with "$ pip install pysha3"
	def change_password(self, new_password):
		s = sha3_256()
		# make the hash and set it
		s.update(bytearray(new_password, 'utf8'))
		self.password = s.hexdigest()
		# save
		self.save()

	# create an event
	def create_event(self, event_name, event_description, group_size):
		# save the user first
		self.save()
		# create the event
		new_event = Event(name=event_name, description=event_description, ideal_group_size=group_size, organizer=self)
		# save the event
		new_event.save()
		# update the events the user has created
		self.org_Events = self.org_Events + "," + str(new_event.pk)
		# save user again
		self.save()

	# get all the events the user has created in list form
	def get_organized_events(self):
		return self.org_Events.split(",")[1:]





class Event(models.Model):
	name = models.CharField(max_length=250)
	description = models.CharField(max_length=2000, default="null")
	organizer = models.ForeignKey(User)
	ideal_group_size = models.IntegerField(default=4)
	allow_projects = models.BooleanField(default=True)
	allow_voting = models.BooleanField(default=True)
	participants = models.CharField(max_length=2000, default="")
	project_ideas = models.CharField(max_length=2000, default="")
	groups = models.CharField(max_length=2000, default="")

	# add participant to CSV
	def add_participant(self, user):
		self.participants = self.participants + "," + str(user.pk)
		self.save()

	# get participants as list
	def get_participants(self):
		return self.participants.split(",")[1:]

	# add new project idea to CSV
	def add_project_idea(self, name, description, user):
		self.save()
		project_idea = Project(name=name, description=description, proposer=user, event=self)
		project_idea.save()
		self.project_ideas = self.project_ideas + "," + str(project_idea.pk)
		self.save()

	# get project ideas as list
	def get_project_ideas(self):
		return self.project_ideas.split(",")[1:]



class Project(models.Model):
	name = models.CharField(max_length=250)
	description = models.CharField(max_length=2000)
	proposer = models.ForeignKey(User)
	event = models.ForeignKey(Event)
	ratings = models.CharField(max_length=2000, default="")


class U2P_Relation(models.Model):
	rater = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	rating = models.IntegerField()
