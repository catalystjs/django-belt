# These are the most commonly used elements for application views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from ..users import views as user_views

# Import your models for this application
# from .models import Course, Description, Comment

# Import models from different applications
# from ..<different_app>.models import <table_name>

# Create your views here.
def index(request):
	return redirect(reverse('users:index'))
