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
from django.conf import settings
from django.contrib import admin
from unfold_studio import views
from profiles import views as profile_views
from prompts import views as prompt_views
from literacy_events import views as literacy_event_views
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    url(r'^favicon\.ico$', favicon_view),

    url(r'^admin/', admin.site.urls),
    url(r'signup', views.signup, name='signup'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^$', views.home, name="home"),
    url('^', include('django.contrib.auth.urls')),
    url(r'users/(?P<slug>\w+)/?$', profile_views.UserDetailView.as_view(), name="show_user"),
    url(r'users/(?P<slug>\w+)/feed/?$', profile_views.FeedView.as_view(), name="show_feed"),
    url(r'users/(?P<slug>\w+)/follow/?$', profile_views.FollowUserView.as_view(), name="follow_user"),
    url(r'users/(?P<slug>\w+)/unfollow/?$', profile_views.UnfollowUserView.as_view(), name="unfollow_user"),

    url(r'stories/?$', views.browse, name="list_stories"),
    url(r'stories/new/?$', views.new_story, name="new_story"),
    url(r'stories/(?P<story_id>\d+)/?$', views.show_story, name="show_story"), 
    url(r'stories/(?P<story_id>\d+)/compile/?$', views.compile_story, name="compile_story"), 
    url(r'stories/(?P<story_id>\d+)/json/?$', views.show_json, name="show_json"), 
    url(r'stories/(?P<story_id>\d+)/edit/?$', views.edit_story, name="edit_story"), 
    url(r'stories/(?P<slug>\d+)/love/?$', views.LoveStoryView.as_view(), name="love_story"), 
    url(r'stories/(?P<slug>\d+)/fork/?$', views.ForkStoryView.as_view(), name="fork_story"), 
    url(r'stories/(?P<slug>\d+)/share/?$', views.ShareStoryView.as_view(), name="share_story"), 
    url(r'stories/(?P<slug>\d+)/unshare/?$', views.UnshareStoryView.as_view(), name="unshare_story"), 
    url(r'stories/(?P<slug>\d+)/delete/?$', views.DeleteStoryView.as_view(), name="delete_story"), 

    url(r'books/?$', views.BookListView.as_view(), name='list_books'),
    url(r'books/new/?$', views.CreateBookView.as_view(), name='create_book'),
    url(r'books/(?P<pk>\d+)/?$', views.BookDetailView.as_view(), name="show_book"), 
    url(r'books/(?P<pk>\d+)/edit/?$', views.UpdateBookView.as_view(), name="edit_book"), 
    url(r'books/(?P<pk>\d+)/add/(?P<story_id>\d+)/?$', views.AddStoryToBookView.as_view(), name="add_story_to_book"), 
    url(r'books/(?P<pk>\d+)/remove/(?P<story_id>\d+)/?$', views.RemoveStoryFromBookView.as_view(), name="remove_story_from_book"), 

    url(r'prompts/manage/?$', prompt_views.PromptsOwnedListView.as_view(), name="list_prompts_owned"),
    url(r'prompts/manage/csv/?$', prompt_views.PromptsOwnedCSVView.as_view(), name="prompts_owned_csv"),
    url(r'prompts/?$', prompt_views.PromptsAssignedListView.as_view(), name="list_prompts_assigned"),
    url(r'prompts/(?P<pk>\d+)/?$', prompt_views.PromptAssignedDetailView.as_view(), name="show_prompt_assigned"), 
    url(r'prompts/(?P<pk>\d+)/clear/?$', prompt_views.ClearPromptSubmissionView.as_view(),  
            name="clear_prompt_submission"), 
    url(r'prompts/manage/(?P<pk>\d+)/?$', prompt_views.PromptOwnedDetailView.as_view(), name="show_prompt_owned"), 
    url(r'prompts/manage/(?P<pk>\d+)/publish/?$', prompt_views.PublishAsBookView.as_view(), name="publish_prompt"), 
    url(r'prompts/manage/(?P<pk>\d+)/unpublish/?$', prompt_views.UnpublishBookView.as_view(), name="unpublish_prompt"), 

    url(r'reading/?', literacy_event_views.LogReadingEvent.as_view(), name="log_reading_event"),

    url(r'require_entry_point.js', views.require_entry_point, name="require_entry_point"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        #path('__debug__/', include(debug_toolbar.urls)),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
