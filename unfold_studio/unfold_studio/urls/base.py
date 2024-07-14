from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from unfold_studio import views
from profiles import views as profile_views
from prompts import views as prompt_views
from literacy_events import views as literacy_event_views
from literacy_groups import views as literacy_group_views
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

    path('groups/', literacy_group_views.ListGroupsView.as_view(), name="list_groups"),
    path('groups/new', literacy_group_views.CreateGroupView.as_view(), name="create_group"),
    path('groups/<int:pk>/', literacy_group_views.ShowGroupView.as_view(), name="show_group"),
    path('groups/<int:pk>/edit', literacy_group_views.UpdateGroupView.as_view(), name="update_group"),
    path('groups/<int:pk>/invite', literacy_group_views.InviteToGroupView.as_view(), name="invite_to_group"),
    path('groups/<int:pk>/change_invite', literacy_group_views.ChangeGroupInviteView.as_view(), name="change_group_invite"),
    path('groups/<int:pk>/join', literacy_group_views.JoinGroupView.as_view(), name="join_group"),
    path('groups/<int:pk>/leave', literacy_group_views.LeaveGroupView.as_view(), name="leave_group"),
    path('groups/<int:pk>/prompts/new/', prompt_views.CreatePromptView.as_view(), 
            name="create_prompt"),
    path('groups/<int:group_pk>/prompts/<int:pk>/', prompt_views.ShowPromptView.as_view(), 
            name="show_prompt"),
    path('groups/<int:group_pk>/prompts/<int:pk>/edit/', prompt_views.UpdatePromptView.as_view(), 
            name="update_prompt"),
    path('groups/<int:group_pk>/prompts/<int:pk>/clear/', prompt_views.ClearPromptSubmissionView.as_view(), 
            name="clear_prompt_submission"),
    path('groups/<int:group_pk>/prompts/<int:pk>/export/', prompt_views.ExportPromptAsCsvView.as_view(), 
            name="export_prompt_as_csv"),
    path('groups/<int:group_pk>/prompts/<int:pk>/publish/', prompt_views.PublishAsBookView.as_view(), 
            name="publish_prompt"),
    path('groups/<int:group_pk>/prompts/<int:pk>/unpublish/', prompt_views.UnpublishBookView.as_view(), 
            name="unpublish_prompt"),
    path('groups/<int:group_pk>/prompts/<int:pk>/delete/', prompt_views.DeletePromptView.as_view(), 
            name="delete_prompt"),

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
    path('books/<int:pk>/remove/<int:story_id>/', views.RemoveStoryFromBookView.as_view(), 
            name="remove_story_from_book"), 

    path('reading/', literacy_event_views.LogReadingEvent.as_view(), name="log_reading_event"),
    path('require_entry_point.js', views.require_entry_point, name="require_entry_point"),
    path('embed_entry_point.js', views.embed_entry_point, name="embed_entry_point"),
    path('', include('text_generation.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
