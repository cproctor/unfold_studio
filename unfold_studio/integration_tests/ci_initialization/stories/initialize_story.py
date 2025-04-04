import reversion
from unfold_studio.models import Story
import django.utils.timezone as timezone

def create_story(user, site, story_id, title, ink_content, description, is_public=True):
    story = Story.objects.create(
        id=story_id,
        title=title,
        ink=ink_content,
        author=user,
        public=is_public,
        creation_date=timezone.now(),
        edit_date=timezone.now(),
        description=description,
        sites=[site],
    )
    
    # Save the story first to get a version
    story.save()
    
    # Register the story with reversion
    with reversion.create_revision():
        reversion.add_to_revision(story)
    
    # Now compile the story
    story.compile()
    story.save()
    
    return story.id 
