from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.hashers import make_password, check_password
# Get Query Dict classes
from django.http.request import QueryDict, MultiValueDict
# Exception classes
from django.core.exceptions import ObjectDoesNotExist

import re


# Constants
# Regular expression to match proper emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+\@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Error key reference
ERROR_REFERENCE = {'first_name': 'First Name', 'last_name': 'Last Name', 'name': 'Name', 'alias': 'Alias'}
# Name key references
NAME_REFERENCES = ['name', 'alias', 'first_name', 'last_name']


# Our new manager!
# No methods in our new manager should ever catch the whole request object with a parameter!!! (just parts, like request.POST)
class UserManager(models.Manager):
    # This handles the pushing of the errors into the dictionary handler
    def push_error(self, results, key, error):
        # Handle named error messages
        if key in ERROR_REFERENCE:
            error = ' '.join([ERROR_REFERENCE[key], error])
        if key not in results:
            # Set the state to False
            results[key] = {'state': False}
        # Append the error to the results list for this key
        if 'messages' not in results[key]:
            results[key]['messages'] = [error]
        else:
            results[key]['messages'].append(error)

    # This will validate the specific login components (email and password)
    def validate_login(self, postData, results={}):
        # Validate the email address format
        if not EMAIL_REGEX.match(postData['email']):
            self.push_error(results=results, key='email', error='Email is not a valid format')
        # Make sure the password is greater then or equal to 8 characters
        if len(postData['password']) < 8:
            self.push_error(results=results, key='password', error='Password is shorter then 8 characters')
        # Make sure that the password has at least one number and one uppercase character
        if postData['password'].islower() or postData['password'].isalpha():
            self.push_error(results=results, key='password', error='Password requires one number and one uppercase letter')
        # Return the results
        return results

    # This will validate all postData
    def validate_all(self, postData):
        # Initialize the results dictionary
        results = {}
        # Validate name form inputs
        for key in [key for key in postData if key in NAME_REFERENCES]:
            # Ensure they are greater then 2 characters
            if len(postData[key]) < 3:
                # Push the error for this check
                self.push_error(results=results, key=key, error='can not be less then 3 characters')
            # Ensure that names have no numbers (whitespaces are ok)
            if not postData[key].replace(' ', '', 1).isalpha():
                # Push the error for this check
                self.push_error(results=results, key=key, error='has characters that are not letters \
                                                                 or multiple spaces')
        # Login validations for email and password
        results = self.validate_login(postData, results)
        # Validate that the confirmation matches (registration only)
        if postData['password'] != postData['password_confirm']:
            self.push_error(results=results, key='password', error='Password fields do not match')
        # Return the results
        return results

    # Common method to register a user
    def register(self, postData):
        # Run the Validations on the postData
        results = self.validate_all(postData)
        # If there are users return them
        if results:
            return results
        else:
            # Handle spliting the combined name for the database
            if 'name' in postData:
                # Make a mutable copy of the QueryDict
                data = dict(postData.iteritems())
                # Split the name
                if len(data['name'].split(' ')) == 2:
                    data['first_name'], data['last_name'] = data['name'].split(' ')
                elif len(data['name'].split(' ')) == 1:
                    data['first_name'] = data['name']
                # Change it back to a QueryDict (Retain polymorphic features)
                import urllib
                postData = QueryDict(urllib.urlencode(data, doseq=True))
            # Check to make sure email does not already exist
            try:
                user = User.objects.get(email=postData['email'])
                # If we didn't get an exception, this user exists
                self.push_error(results=results, key='email', error='This email already exists and must be unique')
                # Return the error results
                return results
            except ObjectDoesNotExist:
                # Derive the column keys for contraints on keys to push
                column_keys = [item.name for item in User._meta.get_fields()]
                # Create the data package based on column constraints
                data = {key: value for key, value in postData.iteritems() if key in column_keys}
                # Hash the password
                if 'password' in data:
                    data['password'] = make_password(data['password'])
                # Create and return the user
                return self.create(**data)

    # Common method to login a user
    def login(self, postData):
        # Run the Validations on the postData
        results = self.validate_login(postData)
        # If there are users return them
        if results:
            return results
        else:
            # Email/Account Lookup
            try:
                user = User.objects.get(email=postData['email'])
                # Check the password against the hash
                if check_password(postData['password'], user.password):
                    return user
                else:
                    self.push_error(results=results, key='password', error='Password did not match')
                    return results
            # Handle cases where there no users
            except (ObjectDoesNotExist):
                self.push_error(results=results, key='email', error='Email was not found')
                return results


# Create your models here.
class User(models.Model):
    # name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True, blank=False)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Attach the custom User manager
    objects = UserManager()

    def name(self):
        return ('%s %s' % (self.first_name, self.last_name))
