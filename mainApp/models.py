from __future__ import unicode_literals
from django.db import models
import hashlib
import sha3
from random import randint


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
		s = hashlib.sha3_256()
		# make the hash and set it
		s.update(password)
		self.password = s.hexdigest()
		#self.password = new_password
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

	def __str__(self):
		return self.name





class Event(models.Model):
	name = models.CharField(max_length=250)
	eventID = models.CharField(max_length=10)
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
		
	# make a hash to use as ID
	def encodeID(num, alphabet="23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"):
	    if num == 0:
	        return alphabet[0]
	    arr = []
	    base = len(alphabet)
	    while num:
	        num, rem = divmod(num, base)
	        arr.append(alphabet[rem])
	    arr.reverse()
	    return ''.join(arr)
		
		

	def __str__(self):
		return self.name



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
