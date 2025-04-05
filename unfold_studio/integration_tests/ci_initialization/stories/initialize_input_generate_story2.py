from .initialize_story import create_story

STORY_TITLE = 'Input/Generate Test Story 2'
STORY_DESCRIPTION = 'Test story to check input/generate functionality 2'
STORY_ID = 31
STORY_TEMPLATE = """
VAR name = ""
VAR age = ""
VAR hobby = ""
VAR dream = ""
VAR story = ""

Welcome to the Interactive Story Test!

Let's start with some basic information.
~ input("What's your name?", "name")
BUG
Hello {name}!

Now, let's get to know you better.
~ input("How old are you?", "age")
BUG
{age} is a great age!

Let's generate something about your age.
~ generate("Write a fun fact about being {age} years old in 20 words")

What would you like to do next?

+ Share your hobby
    -> hobby_path
+ Share your dream
    -> dream_path
+ Skip to the end
    -> end_path

=== hobby_path ===
~ input("What's your favorite hobby?", "hobby")
BUG
I love {hobby} too!

Would you like to:
+ Generate a story about your hobby
    ~ generate("Write a short story about someone who loves {hobby} in 20 words")
    -> end_path
+ Generate a poem about your hobby
    ~ generate("Write a short poem about {hobby} in 20 words")
    -> end_path
+ Continue to end
    -> end_path

=== dream_path ===
~ input("What's your biggest dream?", "dream")
BUG
That's an amazing dream! {dream} is inspiring.

Would you like to:
+ Generate a plan to achieve it
    ~ generate("Write a 3-step plan to achieve the dream of {dream} in 20 words")
    -> end_path
+ Generate a motivational quote
    ~ generate("Write a motivational quote about pursuing the dream of {dream} in 20 words")
    -> end_path
+ Continue to end
    -> end_path

=== end_path ===
Let's wrap up with one final generation.
~ generate("Write a farewell message for {name} who is {age} years old in 20 words")

Thank you for participating!
-> END
"""

def create_input_generate_story2(user, site):
    story_id = create_story(
        user=user,
        site=site,
        story_id=STORY_ID,
        title=STORY_TITLE,
        ink_content=STORY_TEMPLATE,
        description=STORY_DESCRIPTION
    )

    return story_id 
