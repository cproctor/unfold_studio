from integration_tests.ci_initialization.stories.initialize_story import create_story
from integration_tests.constants import STORY_ID_PREFIX

STORY_TITLE = 'Continue Test Story'
STORY_DESCRIPTION = 'Test story to check continue functionality'
STORY_ID = STORY_ID_PREFIX + 0

STORY_TEMPLATE = '''
This is a integration test story for continue.
Let's call the continue function now.

 + Go to final knot
 -> final_knot
 + Go to direct continue knot
 -> direct_continue_knot
 + Go to bridge and continue knot
 -> bridge_and_continue_knot
 + Go to needs input knot
 -> needs_input_knot
 + Go to invalid user input knot
 -> invalid_user_input_knot
 
 
=== direct_continue_knot === 
You are inside direct_continue_knot
-> continue(->final_knot)
-> DONE

=== bridge_and_continue_knot ===
You are inside bridge_and_continue_knot
-> continue(->final_knot)
-> DONE

=== needs_input_knot === 
You are inside needs_input_knot
-> continue(->final_knot)
-> DONE

=== invalid_user_input_knot ===
You are inside invalid_user_input_knot
-> continue(->final_knot)
-> DONE


=== final_knot ===
This is the final knot text.
-> DONE
'''

def create_continue_story(user, site):
    story_id = create_story(
        user=user,
        site=site,
        story_id=STORY_ID,
        title=STORY_TITLE,
        ink_content=STORY_TEMPLATE,
        description=STORY_DESCRIPTION
    )

    return story_id 
