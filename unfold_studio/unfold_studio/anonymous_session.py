SESSION_KEY_ANONYMOUS_STORIES = "anonymous_owned_story_ids"


def get_anonymous_owned_story_ids(request):
    raw = request.session.get(SESSION_KEY_ANONYMOUS_STORIES)
    if not raw:
        return []
    if not isinstance(raw, list):
        return []
    return [pk for pk in raw if isinstance(pk, int)]


def add_anonymous_owned_story(request, story_id):
    ids = list(get_anonymous_owned_story_ids(request))
    if story_id not in ids:
        ids.append(story_id)
    request.session[SESSION_KEY_ANONYMOUS_STORIES] = ids
    request.session.modified = True


def owns_anonymous_story(request, story):
    if story.author_id is not None:
        return False
    return story.id in get_anonymous_owned_story_ids(request)


def remove_anonymous_owned_story(request, story_id):
    ids = [pk for pk in get_anonymous_owned_story_ids(request) if pk != story_id]
    request.session[SESSION_KEY_ANONYMOUS_STORIES] = ids
    request.session.modified = True
