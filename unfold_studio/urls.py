"""unfold_studio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from unfold_studio import views
from profiles import views as profile_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'signup', views.signup, name='signup'),
    url(r'^$', views.home, name="home"),
    url('^', include('django.contrib.auth.urls')),
    url(r'about', views.about, name="about"),
    url(r'documentation', views.documentation, name="documentation"),
    url(r'users/(?P<slug>\w+)/?$', profile_views.UserDetailView.as_view(), name="show_user"),
    url(r'users/(?P<slug>\w+)/follow/?$', profile_views.FollowUserView.as_view(), name="follow_user"),
    url(r'users/(?P<slug>\w+)/unfollow/?$', profile_views.UnfollowUserView.as_view(), name="unfollow_user"),
    url(r'stories/?$', views.browse, name="list_stories"),
    url(r'stories/new/?$', views.new_story, name="new_story"),
    url(r'stories/(?P<story_id>\d+)/?$', views.show_story, name="show_story"), 
    url(r'stories/(?P<story_id>\d+)/json/?$', views.show_json, name="show_json"), 
    url(r'stories/(?P<story_id>\d+)/ink/?$', views.show_ink, name="show_ink"), 
    url(r'stories/(?P<story_id>\d+)/edit/?$', views.edit_story, name="edit_story"), 

    url(r'stories/(?P<slug>\d+)/love/?$', views.LoveStoryView.as_view(), name="love_story"), 
    url(r'stories/(?P<slug>\d+)/fork/?$', views.ForkStoryView.as_view(), name="fork_story"), 
    url(r'stories/(?P<slug>\d+)/share/?$', views.ShareStoryView.as_view(), name="share_story"), 
    url(r'stories/(?P<slug>\d+)/unshare/?$', views.UnshareStoryView.as_view(), name="unshare_story"), 
    url(r'books/?$', views.BookListView.as_view(), name='list_books'),
    url(r'books/new/?$', views.CreateBookView.as_view(), name='create_book'),
    url(r'books/(?P<pk>\d+)/?$', views.BookDetailView.as_view(), name="show_book"), 
    url(r'books/(?P<pk>\d+)/edit/?$', views.UpdateBookView.as_view(), name="edit_book"), 
    url(r'require_entry_point.js', views.require_entry_point, name="require_entry_point")
    #url(r'stories/(?P<story_id>\d+)/delete/?$', views.delete_story, name="delete_story"), 
]
