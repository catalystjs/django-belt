from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.hashers import make_password, check_password
# Get Query Dict classes
from django.http.request import QueryDict, MultiValueDict

from ..users .models import User

from datetime import datetime, date


# Constants
# Text key references
TEXT_REFERENCES = ['destination', 'description']


# Our new manager!
# No methods in our new manager should ever catch the whole request object with a parameter!!! (just parts, like request.POST)
class UserManager(models.Manager):
    # This handles the pushing of the errors into the dictionary handler
    def push_error(self, results, key, error):
        if key not in results:
            # Set the state to False
            results[key] = {'state': False}
        # Append the error to the results list for this key
        if 'messages' not in results[key]:
            print ('new messages')
            results[key]['messages'] = [error]
        else:
            print ('existing messages')
            results[key]['messages'].append(error)

    # This will validate all postData
    def validate_all(self, postData):
        # Initialize the results dictionary
        results = {}
        # Validate name form inputs
        for key in [key for key in postData if key in TEXT_REFERENCES]:
            # Ensure they are greater then 2 characters
            if not postData[key]:
                # Push the error for this check
                self.push_error(results=results, key=key, error=' '.join([key, 'can not be empty']))
        # Validate the travel dates
        # Convert the strings into date objects for comparisons
        travel_from = datetime.strptime(postData['travel_from'], '%Y-%m-%d').date()
        travel_to = datetime.strptime(postData['travel_to'], '%Y-%m-%d').date()
        # Check to make sure the travel from date is not in the past
        if travel_from < date.today():
            # Push the error for this check
            self.push_error(results=results, key='travel_from', error='Travel Date From must not be in past')
        # Check to make sure the travel to date is not in the past
        if travel_to < date.today():
            # Push the error for this check
            self.push_error(results=results, key='travel_to', error='Travel Date To must not be in past')
        if travel_from > travel_to:
            # Push the error for this check
            self.push_error(results=results, key='travel_from', error='Travel Date From must be before Travel Date To')
        # Return the results
        return results

    # Add a trip
    def add_travel(self, postData, userid):
        # Run the Validations on the postData
        results = self.validate_all(postData)
        # If there are users return them
        if results:
            return results
        else:
            # Get the user
            user = User.objects.get(pk=userid)
            # Derive the column keys for contraints on keys to push (no FK's)
            trip_column_keys = [item.name for item in Trip._meta.get_fields() if not item.is_relation]
            # Create the data package for Trip based on column constraints
            data = {key: value for key, value in postData.iteritems() if key in trip_column_keys}
            # Add in the user that planned the trip
            data.update({'planned_by': user})
            # Create and return the Trip
            return self.create(**data)

    # Join a trip
    def join_travel(self, tripid, userid):
        # Get the user
        user = User.objects.get(pk=userid)
        # Get the trip
        trip = Trip.objects.get(pk=tripid)
        # Add the user to the joining column
        trip.joining.add(user)
        # Save the trip
        trip.save()


# Create your models here.
class Trip(models.Model):
    # name = models.CharField(max_length=255)
    planned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_plannedby")
    destination = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    travel_from = models.DateField()
    travel_to = models.DateField()
    joining = models.ManyToManyField(User, related_name="users_joining")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Attach the custom User manager
    objects = UserManager()
