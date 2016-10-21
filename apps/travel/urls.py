# Import statements for application
from django.conf.urls import url
# Import your views
from . import views
# Use this if you want to import views from other applications
# from ../<other_app> import views as <other_app_view_name>

# URL patterns to process for the application
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^destination/(?P<id>\d+)$', views.destination, name='destination'),
	url(r'^add$', views.travel_add, name='travel_add'),
	url(r'^join/(?P<id>\d+)$', views.travel_join, name='travel_join'),
]
