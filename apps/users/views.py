# These are the most commonly used elements for application views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

# Import your models for this application
from .models import User

# Import models from different applications
#from ..books.models import Review


# Create your views here.
def index(request):
	# Render the initial page
	return render(request, 'users/index.html')


def register(request):
	# Make sure this is a post else redirect back to index
	if request.method != 'POST':
		return redirect(reverse('users:index'))
	# We have a valid post. Let's make sure we handle the post data
	else:
		# Call the user manager from models for registration
		results = User.objects.register(request.POST)
		# Handle error responses dicitionary
		if isinstance(results, dict):
			for field in results:
				if 'messages' in results[field]:
					for error in results[field]['messages']:
						messages.error(request, error)
			return redirect(reverse('users:index'))
		# Valid user was received
		elif isinstance(results, User):
			# Store the user ID in the session cookie
			request.session['userid'] = results.id
			request.session['alias'] = results.alias
			# Redirect to the main books page
			return redirect(reverse('travel:index'))


def login(request):
	# Make sure this is a post else redirect back to index
	if request.method != 'POST':
		return redirect(reverse('users:index'))
	# We have a valid post. Let's make sure we handle the post data
	else:
		# Call the user manager from the models for login
		user = User.objects.login(request.POST)
		# Handle error responses dicitionary
		if isinstance(user, dict):
			for field in user:
				if 'messages' in user[field]:
					for error in user[field]['messages']:
						messages.error(request, error)
			return redirect(reverse('users:index'))
		# Valid user was received
		elif isinstance(user, User):
			# Store the user ID in the session cookie
			request.session['userid'] = user.id
			request.session['alias'] = user.alias
			# Redirect to the main books page
			return redirect(reverse('travel:index'))


def logout(request):
	# Clear the session cookie
	request.session.clear()
	# Redirect back to the main login page
	return redirect(reverse('users:index'))
