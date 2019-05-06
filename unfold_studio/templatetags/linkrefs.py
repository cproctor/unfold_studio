from django import template
from unfold_studio.models import Story
from django.contrib.auth.models import User
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
            return '<a href="{}">{}</a>'.format(
                reverse('show_story', args=[story.id]),
                esc(story.title),
            )
        else:
            return "a story"
    except Story.DoesNotExist:
        return "a missing story"

def book_replacement(bookId, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        book = Book.objects.get(pk=bookId)
        replacement = '<a href="{}">{}</a>'.format(
            reverse('show_book', args=[int(bookref)]),
            esc(book.title)
        )
    except Book.DoesNotExist: 
        replacement = "a missing book"

def user_replacement(userId, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        if userId == user.id:
            return "you"
        else: 
            subjectUser = User.objects.get(pk=userId)
            return '<a href="{}">{}</a>'.format(
                reverse('show_user', args=[subjectUser.username]),
                esc(subjectUser.username)
            )
    except User.DoesNotExist:
        return "a missing user"

@register.filter(needs_autoescape=True)
def linkstory(storyId, user, autoescape=True):
    return mark_safe(story_replacement(storyId, user))

@register.filter(needs_autoescape=True)
def linkuser(userId, user, autoescape=True):
    return mark_safe(user_replacement(userId, user))

@register.filter(needs_autoescape=True)
def linkrefs(text, user, autoescape=True):  
    "Converts references into HTML links suitable for the user"
    replacements = []
    for storyref in re.findall(ref_pattern('story'), text):
        storyId = int(storyref)
        replacement = story_replacement(storyId, user, autoescape)
        replacements.append((ref_token('story', storyId), replacement))
    for bookref in re.findall(ref_pattern('book'), text):
        bookId = int(bookref)
        replacement = book_replacement(bookId, user, autoescape)
        replacements.append((ref_token('book', bookId), replacement))
    for userref in re.findall(ref_pattern('user'), text):
        userId = int(userref)
        replacement = user_replacement(userId, user, autoescape)
        replacements.append((ref_token('user', userId), replacement))

    for old, new in replacements:
        text = text.replace(old, new)
    return mark_safe(text)
