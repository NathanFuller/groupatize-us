from django.shortcuts import render
from django.shortcuts import redirect
from .models import User
from hashlib import sha3_256

def index(request):
	context = {'login_success':request.GET.get('login_success'),
				'logout_success':request.GET.get('logout_success')
				}
	return render(request, 'mainApp/index.html', context)


def login(request):
	print("Entered login processing")
	# get username and password
	email = request.POST['email']
	password = request.POST['password']

	# hash password
	s = sha3_256()
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
	request.session['user'] = None
	return redirect('../?logout_success=True')
