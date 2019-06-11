"""unfold_studio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path(r'$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path(r'$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path(r'blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from unfold_studio import views
from profiles import views as profile_views
from prompts import views as prompt_views
from literacy_events import views as literacy_event_views
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path('favicon.ico', favicon_view),

    path('admin/', admin.site.urls),
    path('signup', views.signup, name='signup'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', views.home, name="home"),
    path('', include('django.contrib.auth.urls')),
    path('users/<slug:slug>/', profile_views.UserDetailView.as_view(), name="show_user"),
    path('users/<slug:slug>/feed/', profile_views.FeedView.as_view(), name="show_feed"),
    path('users/<slug:slug>/follow/', profile_views.FollowUserView.as_view(), name="follow_user"),
    path('users/<slug:slug>/unfollow/', profile_views.UnfollowUserView.as_view(), name="unfollow_user"),

    path('stories/', views.browse, name="list_stories"),
    path('stories/new/', views.new_story, name="new_story"),
    path('stories/<int:story_id>/', views.show_story, name="show_story"), 
    path('stories/<int:pk>/history/', views.StoryVersionListView.as_view(), name="show_story_versions"), 
    path('stories/<int:pk>/history/<int:version>/', views.StoryVersionDetailView.as_view(), 
            name="show_story_version"), 
    path('stories/<int:story_id>/compile/', views.compile_story, name="compile_story"), 
    path('stories/<int:story_id>/json/', views.show_json, name="show_json"), 
    path('stories/<int:story_id>/edit/', views.edit_story, name="edit_story"), 
    path('stories/<int:pk>/love/', views.LoveStoryView.as_view(), name="love_story"), 
    path('stories/<int:pk>/fork/', views.ForkStoryView.as_view(), name="fork_story"), 
    path('stories/<int:pk>/share/', views.ShareStoryView.as_view(), name="share_story"), 
    path('stories/<int:pk>/unshare/', views.UnshareStoryView.as_view(), name="unshare_story"), 
    path('stories/<int:pk>/version/', views.NewStoryVersionView.as_view(), name="new_story_version"), 
    path('stories/<int:pk>/delete/', views.DeleteStoryView.as_view(), name="delete_story"), 

    path('books/', views.BookListView.as_view(), name='list_books'),
    path('books/new/', views.CreateBookView.as_view(), name='create_book'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name="show_book"), 
    path('books/<int:pk>/edit/', views.UpdateBookView.as_view(), name="edit_book"), 
    path('books/<int:pk>/add/<int:story_id>/', views.AddStoryToBookView.as_view(), name="add_story_to_book"), 
    path('books/<int:pk>/remove/<int:story_id>/', views.RemoveStoryFromBookView.as_view(), name="remove_story_from_book"), 

    path('prompts/manage/', prompt_views.PromptsOwnedListView.as_view(), name="list_prompts_owned"),
    path('prompts/manage/csv/', prompt_views.PromptsOwnedCSVView.as_view(), name="prompts_owned_csv"),
    path('prompts/', prompt_views.PromptsAssignedListView.as_view(), name="list_prompts_assigned"),
    path('prompts/<int:pk>/', prompt_views.PromptAssignedDetailView.as_view(), name="show_prompt_assigned"), 
    path('prompts/<int:pk>/clear/', prompt_views.ClearPromptSubmissionView.as_view(),  
            name="clear_prompt_submission"), 
    path('prompts/manage/<int:pk>/', prompt_views.PromptOwnedDetailView.as_view(), name="show_prompt_owned"), 
    path('prompts/manage/<int:pk>/publish/', prompt_views.PublishAsBookView.as_view(), name="publish_prompt"), 
    path('prompts/manage/<int:pk>/unpublish/', prompt_views.UnpublishBookView.as_view(), name="unpublish_prompt"), 

    path('reading/', literacy_event_views.LogReadingEvent.as_view(), name="log_reading_event"),

    path('require_entry_point.js', views.require_entry_point, name="require_entry_point"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
