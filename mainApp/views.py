from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
import smtplib
from .models import User, Event, Project, U2P_Relation, Group
import hashlib
from random import randint


EMAIL_HOST_USER = 'groupatizer@gmail.com'

EMAIL_HOST_PASSWORD = 'gr0up4t1z3r'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 465


# import sha3
from django.http import HttpResponse
import numpy as np
from scipy.optimize import linear_sum_assignment

def index(request):
	#print "Main page!"

	context = {'login_success':request.GET.get('login_success'),
				'logout_success':request.GET.get('logout_success'),
				'email_in_use':request.GET.get('email_in_use'),
				'create_account':request.GET.get('create_account')
				}

	#s=smtplib.SMTP("smtp.gmail.com", 587)
	#s.ehlo()
	#s.starttls()
	#s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
	#to_email = "groupatizer@gmail.com"
	#msg = '\r\n'.join(['Subject: Test Subject 2', "", "this is the body 2"])
	#s.sendmail(EMAIL_HOST_USER, to_email, msg)

	return render(request, 'mainApp/index.html', context)


def login(request):
	#print "Entered login processing"
	# get username and password
	email = request.POST['email'].strip()
	password = request.POST['password'].strip()
	# search for account associated with Email
	results = User.objects.filter(email=email)

	# if we found the account
	if len(results) == 1:
		user = results[0]
		salt = user.salt

		# hash password
		s = hashlib.md5()
		s.update(password+salt)
		password = s.hexdigest()

		if password == user.password:
			# log them in
			request.session['user'] = results[0].pk
			#send them back
			return redirect('../?login_success=True')
		return redirect('../?login_success=False')
	else:
		return redirect('../?login_success=False')

def groupatize(request):
	#Get the event
	event_id = request.POST.get('event_id', None)
	events = Event.objects.filter(pk=event_id)
	if len(events) == 1:
		event = events[0]

		#Get the U2P_Relations
		u2p_list = U2P_Relation.objects.filter(event=event_id)
		if len(u2p_list) < 1:
			return redirect('../dashboard/?ratings_present=False')
		user_list = []
		project_list = []
		project_popularity = {}

		#Strip out the user_list, project_popularity from the U2P_Relations
		for u2p in u2p_list:
			#print str(u2p.rater) + "\t" + str(u2p.rating) + "\t" + str(u2p.project.name) + "\n"
			if u2p.rater not in user_list:
				user_list.append(u2p.rater)
			if u2p.project not in project_list:
				project_list.append(u2p.project)
				project_popularity[u2p.project] = 0
			project_popularity[u2p.project] += u2p.rating

		#Determine the number of projects
		num_proj = min(len(user_list)/event.ideal_group_size, len(project_list))
		if num_proj == 0: num_proj = 1
		proj_pop_sorted = sorted(project_popularity.items(), key=lambda x: x[1], reverse=True)
		selected_proj = [proj_pop_sorted[proj][0] for proj in xrange(num_proj)]

		#Determine how many people will be on each project
		group_sizes = {}
		for x in xrange(num_proj): group_sizes[x] = 0
		for x in xrange(len(user_list)): group_sizes[x%num_proj] += 1
		group_sizes = group_sizes.values()

		#Make duplicates of the projects for each position
		sel_proj_pos = []
		for proj in xrange(num_proj):
			for num_pos in xrange(group_sizes[proj]):
				sel_proj_pos.append(selected_proj[proj])

		#Construct the ratings_matrix
		ratings_array = []
		for user in user_list:
			user_ratings = []
			for position in sel_proj_pos:
				user_ratings.append(u2p_list.filter(rater=user).filter(project=position)[0].rating)
			ratings_array.append(user_ratings)
		ratings_matrix = np.array(ratings_array)

		#Run the algorithm, print the satisfaction.
		ratings_matrix *= -1
		row_ind, col_ind = linear_sum_assignment(ratings_matrix)
		print "\nSatisfaction ", ratings_matrix[row_ind, col_ind].sum() * -1 / len(user_list) * 10, "%"
		
		#Create the groups
		for proj in selected_proj:
			event.add_group(proj)
		
		#Assign the users to the groups
		for user in xrange(len(user_list)):
			print user_list[user], "will work on", sel_proj_pos[col_ind[user]].name
			assigned_group = Group.objects.filter(project=sel_proj_pos[col_ind[user]])
			if len(assigned_group) > 1: assigned_group[1].delete()
			assigned_group[0].users.add(user_list[user])
			assigned_group[0].save()
			
		#Send Emails
		send_group_emails(event)
		notify_creator(event)
		
		
		
		return redirect("".join(["../event/", str(event.id)]))
	else:
		return redirect("../")

def logout(request):
	#print "logout"
	request.session['user'] = None
	return redirect('../?logout_success=True')

def create_account(request):
	#print "Create account!"
	# get form data
	first_name = request.POST['first_name'].strip()
	last_name = request.POST['last_name'].strip()
	email = request.POST['email'].strip()
	password = request.POST['password']
	full_name = first_name + " " + last_name

	# check if that email is already associated with an account
	results = User.objects.filter(email=email)

	# if theres already an account with that email then return an error
	if len(results) > 0:
		return redirect('../?email_in_use=True')

	# hash password
	s = hashlib.md5()
	salt = encodeID(randint(1000000000100000000010000000001000000000100000000010000000000000,9000000000100000000010000000001000000000100000000010000000000000))
	s.update(password + salt)
	password = s.hexdigest()


	#create the user
	user = User(name=full_name, email=email, password=password, salt=salt)
	user.save()

	#log the user in
	request.session['user'] = user.pk

	# return
	return redirect('../?create_account=True')

# redirects to the real page where they create an event
def redir_create_event_page(request):
	#print "Redirect create event"

	if request.GET.get('email_in_use') == 'True':
		context = {'event_name':request.GET.get('event_name'),
					'first_name':request.GET.get('first_name'),
					'last_name':request.GET.get('last_name'),
					'email_in_use':'True',
					'description':request.GET.get('description'),
					'preffered_size':request.GET.get('preffered_size')
					}
	else:
		# get form data
		event_name = request.POST.get('event_name', "")
		context = {'event_name':event_name}
	return render(request, 'mainApp/createEvent.html', context)

def join_event(request):
	event_id = request.POST['groupHash']
	events = Event.objects.filter(pk=event_id)
	if len(events) == 1:
		event = events[0]
		if request.session.get('user', None) != None:
			user = User.objects.get(pk=request.session['user'])
			user.join_event(event)
			return redirect("../event/" + event_id + "?joined=true")
		else:
			return redirect("../?Login=false")
	else:
		return redirect("../event/" + event_id)

def create_event(request):
	#print "Create event"
	# get form data
	event_name = request.POST['event_name']
	description = request.POST['description']
	preffered_size = request.POST['preffered_size']
	print "Creating event"
	event = None

	if request.session.get('user', None):
		print "user logged in"
		user = User.objects.filter(pk=request.session.get('user'))[0]
		event = user.create_event(event_name, description, preffered_size)
	else:
		# get form data
		first_name = request.POST['first_name'].strip()
		last_name = request.POST['last_name'].strip()
		email = request.POST['email'].strip()
		password = request.POST['password']
		full_name = first_name + " " + last_name

		# check if that email is already associated with an account
		results = User.objects.filter(email=email)

		# if theres already an account with that email then return an error
		if len(results) > 0:
			return redirect('../?email_in_use=True&first_name='+first_name+'&last_name='+last_name+
			'&email='+email+'&preffered_size'+ preffered_size + '&description='+description)

		# hash password
		s = hashlib.md5()
		salt = encodeID(randint(1000000000100000000010000000001000000000100000000010000000000000,9000000000100000000010000000001000000000100000000010000000000000))
		s.update(password + salt)
		password = s.hexdigest()

		#create the user
		user = User(name=full_name, email=email, password=password, salt=salt)
		user.save()

		#log the user in
		request.session['user'] = user.pk

		#create the event
		event = user.create_event(event_name, description, preffered_size)
	return redirect(reverse('event_page', kwargs={'event_id': event.pk}))

def event_page(request, event_id=None):
	# find the event
	events = Event.objects.filter(pk=event_id)
	context = {'event_id':event_id}

	# if we found the event
	if len(events) == 1:
		# get the event from the list
		event = events[0]

		groups = Group.objects.filter(event=event)

		if request.POST:
			if 'createProject' in request.POST:
				project_name = request.POST['title']
				project_description = request.POST['description']
				event.add_project_idea(project_name, project_description,
									   User.objects.get(pk=request.session['user']))

		# get the project keys associated with this event
		project_ideas = event.get_project_ideas()

		# if the user is logged in and they are the creator of the event
		if request.session.get('user', None) and event.organizer == User.objects.get(pk=request.session['user']):
			# context info
			context = {'found_event':True,
						'event_name':event.name,
						'event_description':event.description,
						'preffered_size':event.ideal_group_size,
						'project_ideas': project_ideas,
						'creator_access':True,
						'event_id': event_id,
						'groups':groups}
		else:
			# context info
			context = {'found_event':True,
						'event_name':event.name,
						'event_description':event.description,
						'preffered_size':event.ideal_group_size,
						'project_ideas': project_ideas,
						'event_id': event_id,
						'groups':groups}
	else:
		context = {'found_event':False}

	if request.GET.get('rate_success', None) == 'True':
		print "Ratings submitted successfully"
		context['rated'] = 'True'

	return render(request, 'mainApp/event.html', context)

def dashboard_page(request):
	print "Dashboard"

	if request.POST:
		if 'createEvent' in request.POST:
			event_name = request.POST['title']
			description = request.POST['description']
			preffered_size = request.POST['size']

			user = User.objects.filter(pk=request.session.get('user'))[0]
			event = user.create_event(event_name, description, preffered_size)
			return redirect(reverse('event_page', kwargs={'event_id': event.pk}))

	if request.session.get('user', None) != None:
		print "user logged in"
		user = User.objects.filter(pk=request.session['user'])[0]

		event_list = user.get_organized_events()
		part_list = user.get_participant_events()

		# context info
		if len(event_list) > 0:
			if len(part_list) > 0:
				context = {'event_list': event_list, 'part_list' : part_list}
			else:
				context = {'event_list': event_list}
		elif len(part_list) > 0:
			context = {'part_list': part_list}
		else:
			context = {'events': []}
		return render(request, 'mainApp/dashboard.html', context)
	else:
		print "Not Logged in"

	return redirect(index)


def edit_project_idea(request):
	# get post data
	name = request.POST.get('title', None)
	description = request.POST.get('description', None)
	submit_type = request.POST.get('submit_type', None)
	project_id = request.POST.get('projectID', None)
	event_id = request.POST.get('event_id', None)

	# get the project
	project = Project.objects.get(id=project_id)

	# if they want to delete it then delete it
	if submit_type == 'delete':
		project.delete()
	# else edit it
	elif submit_type == 'edit':
		project.name = name
		project.description = description
		project.save()

	return redirect('event_page', event_id)

def edit_event(request):
	# get post data
	name = request.POST.get('title', None)
	description = request.POST.get('description', None)
	size = request.POST.get('size', None)
	submit_type = request.POST.get('submit_type', None)
	event_id = request.POST.get('event_id', None)

	event = Event.objects.get(id=event_id)

	if submit_type == 'delete':
		event.delete()

	elif submit_type == 'edit':
		event.name = name
		event.description = description
		event.ideal_group_size = size
		event.save()

	return redirect(dashboard_page)

def rate_project_ideas(request, event_id):
	print "You tried to rate projects on ", event_id

	# find the event
	events = Event.objects.filter(pk=event_id)
	event = events[0]
	
	#Added user to event if not already added
	user = User.objects.get(pk=request.session.get('user', None))
	event.participants.add(user)
	

	# get the project keys associated with this event
	project_ideas = event.get_project_ideas()

	# context info
	context = {'found_event':True,
				'event_name':event.name,
				'event_description':event.description,
				'preffered_size':event.ideal_group_size,
				'project_ideas': project_ideas,
				'event_id': event_id}

	return render(request, 'mainApp/rateProjects.html', context)


def submit_ratings(request, event_id): #probably something else too
	user = User.objects.get(pk=request.session.get('user', None))

	events = Event.objects.filter(pk=event_id)
	event = events[0]

	#loop through projects of event and call function from user
	for key in request.POST: #rate_project(self, project_id, my_rating):
		if (key != 'csrfmiddlewaretoken'):
			rating = request.POST[key]
			project = Project.objects.get(pk=key)
			print "Rate project ", key, " with rating ", rating
			user.rate_project(project, rating, event)

	return redirect('../?rate_success=True')


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
    
def show_results(request, event_id=None):
	# find the event
	events = Event.objects.filter(pk=event_id)
	context = {'event_id':event_id}

	# if we found the event
	if len(events) == 1:
		# get the event from the list
		event = events[0]

		groups = Group.objects.filter(event=event)

		if request.POST:
			if 'createProject' in request.POST:
				project_name = request.POST['title']
				project_description = request.POST['description']
				event.add_project_idea(project_name, project_description,
									   User.objects.get(pk=request.session['user']))

		# get the project keys associated with this event
		project_ideas = event.get_project_ideas()
		
		context = {'found_event':True,
						'event_name':event.name,
						'event_description':event.description,
						'preffered_size':event.ideal_group_size,
						'project_ideas': project_ideas,
						'event_id': event_id,
						'groups':groups}
	else:
		context = {'found_event':False}

	if request.GET.get('rate_success', None) == 'True':
		print "Ratings submitted successfully"
		context['rated'] = 'True'

	return render(request, 'mainApp/results.html', context)
	


def send_group_emails(event):
	groups = Group.objects.filter(event=event)
	s=smtplib.SMTP("smtp.gmail.com", 587)
	s.ehlo()
	s.starttls()
	s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

	for group in groups:
		project = group.project
		for user in group.users.all():
			to_email = user.email
			body = "You have been sorted into the following project: " + project.name + " \n\nProject Description: " +project.description +"\n\n\n"+ "Your group is as follows: \n\n"
			for user_send in group.users.all():
				if user.pk != user_send.pk:
					body += (user_send.name + " : Their email is " + user_send.email + "\n")
			msg = '\r\n'.join(['Subject: You have been sorted!', "", body])
			s.sendmail(EMAIL_HOST_USER, to_email, msg)


def notify_creator(event):
	groups = Group.objects.filter(event=event)
	s=smtplib.SMTP("smtp.gmail.com", 587)
	s.ehlo()
	s.starttls()
	s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

	creator = event.organizer
	body = "The groups have been created for your event! They are as follows:\n\n"
	for group in groups:
		project = group.project
		body += 'Project: ' + project.name + '\n' + 'Project Description: ' + project.description + '\nTeam Members:\n\n'
		for user in group.users.all():
			body += user.name + " " + user.email + '\n'
		body += '\n\n'

	msg = '\r\n'.join(['Subject: Groups have been sorted!', "", body])
	s.sendmail(EMAIL_HOST_USER, creator.email, msg)
