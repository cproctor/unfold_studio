from .initialize_story import create_story
from integration_tests.constants import STORY_ID_PREFIX

STORY_TITLE = 'Input/Generate Test Story 3'
STORY_DESCRIPTION = 'Test story to check input/generate functionality 3'
STORY_ID = STORY_ID_PREFIX + 3
STORY_TEMPLATE = """
VAR name = ""
VAR food = ""
VAR color = ""
VAR number = ""
VAR animal = ""
VAR season = ""
VAR weather = ""


Welcome to the Input/Generate Test Story3!

Let's test different combinations of input and generate functions.
-> test1

=== test1 ===
First, let's test input followed by generate.
~ input("What's your name?", "name")
~generate("Write a short greeting for {name} in 20 words")
-> test2

=== test2 ===
Now, let's test generate followed by input.
~generate("Generate a random food suggestion")
~ input("What's your favorite food?", "food")
-> test3

=== test3 ===
Let's test multiple inputs in sequence.
~ input("What's your favorite color?", "color")
~ input("Pick a number between 1 and 10", "number")
-> test4

=== test4 ===
Now let's test multiple generates in sequence.
~generate("Write a short poem about the color: {color} in 20 words")
~generate("Write a fun fact about the number {number} in 20 words")
-> test5

=== test5 ===
Let's test input after multiple generates.
~generate("Generate a random adjective")
~generate("Generate a random noun")
~ input("What's your favorite animal?", "animal")
-> test6

=== test6 ===
Finally, let's test generate after multiple inputs.
~ input("What's your favorite season?", "season")
~ input("What's your favorite weather?", "weather")
~generate("Write a short story in 20 words combining {season} season and {weather} weather in 20 words")
-> end

=== end ===
Here's a summary of your inputs:
Name: {name}
Food: {food} 
Color: {color}
Number: {number}
Animal: {animal}
Season: {season}
Weather: {weather}
Would you like to:
* [End story]
    -> DONE
"""

def create_input_generate_story3(user, site):
    story_id = create_story(
        user=user,
        site=site,
        story_id=STORY_ID,
        title=STORY_TITLE,
        ink_content=STORY_TEMPLATE,
        description=STORY_DESCRIPTION
    )

    return story_id 
