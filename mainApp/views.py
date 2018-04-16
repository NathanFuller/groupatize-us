from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
import smtplib
from .models import User, Event, Project
import hashlib
from random import randint
# import sha3

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
	
	if request.GET.get('rate_success', None) == 'True':
		print "Ratings submitted successfully"

	# if we found the event
	if len(events) == 1:
		# get the event from the list
		event = events[0]

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
						'event_id': event_id}
		else:
			# context info
			context = {'found_event':True,
						'event_name':event.name,
						'event_description':event.description,
						'preffered_size':event.ideal_group_size,
						'project_ideas': project_ideas,
						'event_id': event_id}
	else:
		context = {'found_event':False}

	return render(request, 'mainApp/event.html', context)

def dashboard_page(request):
	print "Dashboard"

	if request.session.get('user', None) != None:
		print "user logged in"
		user = User.objects.filter(pk=request.session['user'])[0]

		event_list = user.get_organized_events()

		# context info
		if len(event_list) > 0:
			context = {'event_list': event_list}
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


def rate_project_ideas(request, event_id):
	print "You tried to rate projects on ", event_id
	
	# find the event
	events = Event.objects.filter(pk=event_id)
	event = events[0]
	
	# get the project keys associated with this event
	project_ideas = event.get_project_ideas()
	
	# context info
	context = {'found_event':True,
				'event_name':event.name,
				'event_description':event.description,
				'preffered_size':event.ideal_group_size,
				'project_ideas': project_ideas,
				'event_id': event_id}
				
	if request.POST.get('test', None):
		print request.POST['nonexistant']
	
	
	return render(request, 'mainApp/rateProjects.html', context)
	
	
def submit_ratings(request, event_id): #probably something else too
	user = User.objects.get(request.session.get('user', None))
	
	#loop through projects of event and call function from user


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
