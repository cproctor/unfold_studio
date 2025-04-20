from unfold_studio.models import Story
import django.utils.timezone as timezone

def create_story(user, site, story_id, title, ink_content, description, is_public=True):
    try:
        story = Story.objects.get(id=story_id)
        print(f'Story with ID {story_id} already exists')
        return story.id
    except Story.DoesNotExist:
        print(f"Creating {title} story...")
        story = Story.objects.create(
            id=story_id,
            title=title,
            ink=ink_content,
            author=user,
            public=is_public,
            creation_date=timezone.now(),
            edit_date=timezone.now(),
            description=description,
        )

        story.sites.set([site])
        story.compile()

        story.save()
        print(f'Successfully created {title} test story with ID: {story_id} and ink content: {story.ink}')
        
        return story.id
