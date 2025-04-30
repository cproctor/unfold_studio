from .initialize_story import create_story
from integration_tests.constants import STORY_ID_PREFIX

STORY_TITLE = 'Input compile error story'
STORY_DESCRIPTION = 'Test story to check input compile error'
STORY_ID = STORY_ID_PREFIX + 4
STORY_TEMPLATE = """
~input("What's your name?", "name")
"""

def create_input_compile_error_story(user, site):
    story_id = create_story(
        user=user,
        site=site,
        story_id=STORY_ID,
        title=STORY_TITLE,
        ink_content=STORY_TEMPLATE,
        description=STORY_DESCRIPTION
    )

    return story_id 
