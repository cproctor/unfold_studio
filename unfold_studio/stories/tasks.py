from celery import shared_task
import reversion


@shared_task(bind=True)
def compile_story_task(self, story_id):
    """
    Compiles a story asynchronously.
    Returns a dict with 'status', 'errors', and 'json' keys.
    """
    from stories.models import Story
    from django.utils.timezone import now

    try:
        story = Story.objects.get(pk=story_id)
    except Story.DoesNotExist:
        return {'status': 'error', 'errors': [{'line': None, 'message': 'Story not found'}]}

    story.edit_date = now()
    story.compile()
    with reversion.create_revision():
        story.save()

    return {
        'status': 'error' if story.errors.exists() else 'ok',
        'errors': [{'line': e.line, 'message': e.message} for e in story.errors.all()],
    }
