import reversion
from unfold_studio.models import Story
import django.utils.timezone as timezone

def create_story(user, site, story_id, title, ink_content, description="Test story", is_public=True):
    """
    Generic function to create a story with given parameters.
    
    Args:
        user: The user who will be the author of the story
        site: The site to associate the story with
        story_id: The ID to assign to the story
        title: The title of the story
        ink_content: The Ink content/template of the story
        description: Story description (default: "Test story")
        is_public: Whether the story should be public (default: True)
    
    Returns:
        int: The ID of the created story
    """
    story = Story.objects.create(
        id=story_id,
        title=title,
        ink=ink_content,
        author=user,
        public=is_public,
        creation_date=timezone.now(),
        edit_date=timezone.now(),
        description=description
    )
    story.sites.add(site)
    
    # Save the story first to get a version
    story.save()
    
    # Register the story with reversion
    with reversion.create_revision():
        reversion.add_to_revision(story)
    
    # Now compile the story
    story.compile()
    story.save()
    
    return story.id 