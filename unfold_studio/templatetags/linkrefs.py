from django import template
from unfold_studio.models import Story
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.urls import reverse
import re

register = template.Library()

def ref_token(entity, pk):
    return "@{}:{}".format(entity, pk)
def ref_pattern(entity):
    return "@{}:(\d+)".format(entity)

def story_replacement(storyId, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        story = Story.objects.get(pk=storyId)
        if story.visible_to_user(user):
            if story.author:
                return '<a href="{}">{}</a> by <a href="{}">{}</a>'.format(
                    reverse('show_story', args=[story.id]),
                    esc(story.title),
                    reverse('show_user', args=[user.username]),
                    esc(user.username)
                )
            else:
                return '<a href="{}">{}</a>'.format(
                    reverse('show_story', args=[story.id]),
                    esc(story.title),
                )
        else:
            return "a story"
    except Story.DoesNotExist:
        return "a missing story"

@register.filter(needs_autoescape=True)
def linkstory(storyId, user, autoescape=True):
    return mark_safe(story_replacement(storyId, user))

@register.filter(needs_autoescape=True)
def linkrefs(text, user, autoescape=True):  
    "Converts references into HTML links suitable for the user"
    replacements = []
    for storyref in re.findall(ref_pattern('story'), text):
        storyId = int(storyref)
        replacements.append((ref_token('story', storyId), story_replacement(storyId, user, autoescape)))
    for bookref in re.findall(ref_pattern('book'), text):
        bookId = int(bookref)
        try:
            book = Book.objects.get(pk=bookId)
            replacement = '<a href="{}">{}</a>'.format(
                reverse('show_book', args=[int(bookref)]),
                book.title
            )
        except Book.DoesNotExist: 
            replacement = "a missing book"
        replacements.append((ref_token('book', bookId), replacement))

    # TODO: Add refs to users and prompts if useful.
    
    for old, new in replacements:
        text = text.replace(old, new)
        
    return mark_safe(text)
