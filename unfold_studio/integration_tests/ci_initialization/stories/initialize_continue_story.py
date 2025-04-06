from integration_tests.ci_initialization.stories.initialize_story import create_story


STORY_TITLE = 'Continue Test Story'
STORY_DESCRIPTION = 'Test story to check continue functionality'
STORY_ID = 33

STORY_TEMPLATE = '''
This is a integration test story for continue.
Let's call the continue function now.

 + Go to final knot
 -> final_knot
 + Go to continue function call knot
 -> continue_knot
 
 
=== continue_knot === 
You are inside continue function knot
~ continue("final_knot")
-> DONE



=== final_knot ===
This is the final knot text.
-> DONE
'''

def create_input_generate_story(user, site):
    story_id = create_story(
        user=user,
        site=site,
        story_id=STORY_ID,
        title=STORY_TITLE,
        ink_content=STORY_TEMPLATE,
        description=STORY_DESCRIPTION
    )

    return story_id 
