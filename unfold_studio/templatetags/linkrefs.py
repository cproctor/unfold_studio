from django import template
from unfold_studio.models import Story, Book
from prompts.models import Prompt
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.urls import reverse
import re

register = template.Library()

def ref_token(entity, pk):
    return "@{}:{}".format(entity, pk)

def ref_pattern(entity):
    if entity == 'user':
        return "@{}:(\w+)".format(entity)
    else:
        return "@{}:(\d+)".format(entity)

def prompt_replacement(promptId, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        prompt = Prompt.objects.get(pk=promptId, deleted=False)
        if prompt.literacy_group in user.literacy_groups.all():
            return '<a href="{}">{}</a>'.format(
                reverse('show_prompt', args=(prompt.literacy_group.id, prompt.id)),
                esc(prompt.name)
            )
        else:
            return 'a prompt'
    except Prompt.DoesNotExist:
        return 'a missing prompt'
    

def story_replacement(storyId, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        story = Story.objects.get(pk=storyId, deleted=False)
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
        book = Book.objects.get(pk=bookId, deleted=False)
        return '<a href="{}">{}</a>'.format(
            reverse('show_book', args=[bookId]),
            esc(book.title)
        )
    except Book.DoesNotExist: 
        return "a missing book"

def user_replacement(username, user, autoescape=True):
    esc = conditional_escape if autoescape else lambda x: x
    try:
        if username == user.username:
            return "you"
        else: 
            subjectUser = User.objects.get(username=username, active=True)
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
def linkuser(username, user, autoescape=True):
    return mark_safe(user_replacement(username, user))

@register.filter(needs_autoescape=True)
def linkbook(bookId, user, autoescape=True):
    return mark_safe(book_replacement(bookId, user))

@register.filter(needs_autoescape=True)
def linkprompt(promptId, user, autoescape=True):
    return mark_safe(prompt_replacement(promptId, user))

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
    for promptref in re.findall(ref_pattern('prompt'), text):
        promptId = int(promptref)
        replacement = prompt_replacement(promptId, user, autoescape)
        replacements.append((ref_token('prompt', promptId), replacement))
    for username in re.findall(ref_pattern('user'), text):
        replacement = user_replacement(username, user, autoescape)
        replacements.append((ref_token('user', username), replacement))

    for old, new in replacements:
        text = text.replace(old, new)
    return mark_safe(text)
