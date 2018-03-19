from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from .models import *
import hashlib
# import sha3

def index(request):
	print "Main page!"
	context = {'login_success':request.GET.get('login_success'),
				'logout_success':request.GET.get('logout_success'),
				'email_in_use':request.GET.get('email_in_use'),
				'create_account':request.GET.get('create_account')
				}
	return render(request, 'mainApp/index.html', context)


def login(request):
	print "Entered login processing"
	# get username and password
	email = request.POST['email'].strip()
	password = request.POST['password'].strip()

	# hash password
	s = hashlib.sha3_256()
	s.update(bytearray(password, 'utf8'))
	password = s.hexdigest()

	# search for account associated with Email
	results = User.objects.filter(email=email)

	# if we found the account
	if len(results) == 1 and results[0].password == password:
		# log them in
		request.session['user'] = results[0].pk
		#send them back
		return redirect('../?login_success=True')
	else:
		return redirect('../?login_success=False')

def logout(request):
	print "logout"
	request.session['user'] = None
	return redirect('../?logout_success=True')

def create_account(request):
	print "Create account!"
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
	s = hashlib.sha3_256()
	s.update(bytearray(password, 'utf8'))
	password = s.hexdigest()


	#create the user
	user = User(name=full_name, email=email, password=password)
	user.save()

	#log the user in
	request.session['user'] = user.pk

	# return
	return redirect('../?create_account=True')

# redirects to the real page where they create an event
def redir_create_event_page(request):
	print "Redirect create event"

	if request.GET.get('email_in_use') == 'True':
		context = {'event_name':request.GET.get('event_name'),
					'first_name':request.GET.get('first_name'),
					'last_name':request.GET.get('last_name'),
					'email_in_use':'True',
					'email':"",
					'password':'',
					'description':request.GET.get('description'),
					'preffered_size':request.GET.get('preffered_size')
					}
	else:
		# get form data
		event_name = request.POST.get('event_name', "")
		context = {'event_name':event_name}
	return render(request, 'mainApp/createEvent.html', context)

def create_event(request):
	print "Create event"
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
			'&preffered_size='+ preffered_size +'&event_name='+event_name + '&description='+description)

		# hash password
		s = hashlib.sha3_256()
		s.update(bytearray(password, 'utf8'))
		password = s.hexdigest()

		#create the user
		user = User(name=full_name, email=email, password=password)
		user.save()

		#log the user in
		request.session['user'] = user.pk

		#create the event
		event = user.create_event(event_name, description, preffered_size)
	return redirect(reverse('event_page', kwargs={'event_id': event.pk}))

def event_page(request, event_id=None):
	# find the event
	events = Event.objects.filter(pk=event_id)
	context = {}

	# if we found the event
	if len(events) == 1:
		# get the event from the list
		event = events[0]

		# get the project keys associated with this event
		project_ideas_keys = event.get_project_ideas()

		# set up an empty list to put the actual project idea objects in
		project_ideas = []

		# loop through the keys and put the acutal project object in the lsit
		for key in project_ideas_keys:
			project_ideas.append(Project.objects.filter(pk=key)[0])

		# context info
		context = {'found_event':True,
					'event_name':event.name,
					'event_description':event.description,
					'preffered_size':event.ideal_group_size,
					'project_ideas': project_ideas}
	else:
		context = {'found_event':False}

	return render(request, 'mainApp/event.html', context)

def dashboard_page(request):
	print "Dashboard"

	if request.session.get('user', None) != None:
		print "user logged in"
		user = User.objects.filter(pk=request.session['user'])[0]

		event_keys = user.get_organized_events()
		event_list = []

		for key in event_keys:
			event_list.append(Event.objects.filter(pk=key)[0])

		# context info
		if len(event_list) > 0:
			context = {'event_list': event_list}
		else:
			context = {'events': []}
		return render(request, 'mainApp/dashboard.html', context)
	else:
		print "Not Logged in"

	return redirect(index)
