from unfold_studio.models import Story, Book
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, Http404                         

class StoryMixin:
    """
    Allows extending class-based views to fetch a story as the subject of 
    an action (such as liking, adding to a book, etc). either via url kwarg
    or by passing an id.
    """
    story_url_kwarg="story_id"

    def get_story(self, story_id=None, queryset=None, to_edit=False):
        storyId = story_id or self.kwargs.get(self.story_url_kwarg)
        queryset = queryset or Story.objects

        access_allowed = Q(public=True)
        if self.request.user.is_authenticated:
            access_allowed |= Q(author=self.request.user)
        if not to_edit:
            access_allowed |= Q(shared=True)
        try:
            return queryset.get(
                access_allowed,
                id=storyId,
                #sites__id=get_current_site(self.request).id,
                deleted=False
            )
        except Story.DoesNotExist:
            raise Http404("No story matched the query")

