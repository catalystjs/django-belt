# Import statements for application
from django.conf.urls import url
# Import your views
from . import views
# Use this if you want to import views from other applications
# from ../<other_app> import views as <other_app_view_name>

# URL patterns to process for the application
urlpatterns = [
	url(r'^$', views.index, name='index'),
	#url(r'^course/add$', views.course_add, name='course_add'),
	#url(r'^course/destroy/(?P<course_id>\d+)$', views.course_destroy, name='destroy'),
	#url(r'^course/delete/(?P<course_id>\d+)$', views.course_remove, name='course_remove'),
	#url(r'^course/comment/(?P<course_id>\d+)$', views.course_comment, name='course_comment_show'),
	#url(r'^course/comment/add/(?P<course_id>\d+)$', views.course_comment_add, name='course_comment_add'),
	#url(r'^course/comment/delete/(?P<comment_id>\d+)$', views.course_comment_delete, name='course_comment_delete'),
]
