# These are the most commonly used elements for application views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from django.db.models import Q

# Import your models for this application
from .models import Trip

# Import models from different applications
# from ..<different_app>.models import <table_name>


# Create your views here.
def index(request):
	#Trip.objects.all().delete()
	# Filter all the trips we created or are apart of
	trips = Trip.objects.filter(Q(planned_by__id=request.session['userid']) | Q(joining__id=request.session['userid']))
	# Exclude all the trips we did not create or have not joined
	other_user_trips = Trip.objects.exclude(Q(planned_by__id=request.session['userid']) | Q(joining__id=request.session['userid']))
	# Build the context
	context = {
		'trips': trips,
		'other_user_trips': other_user_trips
	}
	return render(request, 'travel/index.html', context)


def destination(request, id):
	context = {'trip': Trip.objects.get(pk=id)}
	return render(request, 'travel/destination.html', context)


def travel_add(request):
	# Render the Add Travel page if we sent a GET request
	if request.method == 'GET':
		return render(request, 'travel/add-travel.html')
	# Do table insertion if we sent a POST request
	elif request.method == 'POST':
		# Call the user manager from models for travel addition
		results = Trip.objects.add_travel(postData=request.POST, userid=request.session['userid'])
		# Handle error responses dicitionary
		if isinstance(results, dict):
			for field in results:
				if 'messages' in results[field]:
					for error in results[field]['messages']:
						messages.error(request, error)
			return redirect(reverse('travel:travel_add'))
		# Valid user was received
		elif isinstance(results, Trip):
			# Redirect to the main books page
			return redirect(reverse('travel:index'))


def travel_join(request, id):
	# Call the user manager from models for travel addition
	Trip.objects.join_travel(tripid=id, userid=request.session['userid'])
	# Redirect to the main books page
	return redirect(reverse('travel:index'))
