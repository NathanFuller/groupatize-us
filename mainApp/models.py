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
	salt = models.CharField(max_length=70, default="")
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
		s = hashlib.md5()
		# make the hash and set it
		salt = encodeID(randint(1000000000100000000010000000001000000000100000000010000000000000,9000000000100000000010000000001000000000100000000010000000000000))
		s.update(password+salt)
		self.password = s.hexdigest()
		self.salt = salt
		#self.password = new_password
		# save
		self.save()

	# create an event
	def create_event(self, event_name, event_description, group_size):
		# create the event
		new_event = Event(name=event_name, description=event_description, ideal_group_size=group_size, organizer=self)
		# save the event
		new_event.save()
		return new_event
		
		
	#rate a project idea
	def rate_project(self, project_id, my_rating):
		new_rating = U2P_Relation(rater=self, project=project_id, rating=my_rating)
		
		new_rating.save()
		return new_rating

	# get all the events the user has created in list form
	def get_organized_events(self):
		return Event.objects.filter(organizer=self)

	def __str__(self):
		return self.name



class Event(models.Model):
	name = models.CharField(max_length=250)
	eventID = models.CharField(max_length=10)
	description = models.CharField(max_length=2000, default="null")
	organizer = models.ForeignKey(User, related_name='organizer')
	ideal_group_size = models.IntegerField(default=4)
	allow_projects = models.BooleanField(default=True)
	allow_voting = models.BooleanField(default=True)
	participants = models.ManyToManyField(User, related_name='participants')
	groups = models.CharField(max_length=2000, default="")

	# add new project idea to CSV
	def add_project_idea(self, name, description, user):
		self.save()
		project_idea = Project(name=name, description=description, proposer=user, event=self)
		project_idea.save()

	# get project ideas as list
	def get_project_ideas(self):
		return Project.objects.filter(event=self)

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
