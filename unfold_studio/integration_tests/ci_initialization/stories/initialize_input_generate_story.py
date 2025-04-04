import reversion
from unfold_studio.models import Story
import django.utils.timezone as timezone

def create_input_generate_story(user, site):
    print("Creating input/generate_story...")
    story = Story.objects.create(
        id=29,
        title='Input/Generate Test Story',
        ink='''
VAR name = ""
VAR food = ""
VAR color = ""
VAR number = ""
VAR story = ""

This is a test story for input and generate functionality.

Let's start with a simple input.
~ input("What's your name?", "name")
BUG
Nice to meet you, {name}!

Now let's test generate with some context.
~ generate("Write a short greeting for {name}")

Let's try input after generate.
~ input("What's your favorite food?", "food")
BUG
I see you like {food}. Let's generate something about that.
~ generate("Write a short description about why {name} might like {food} in 20 words")

Now let's test input with choices.
What would you like to do next?

+ Choose a color
    -> color_choice
+ Choose a number
    -> number_choice
+ Skip both
    -> skip_choice

=== color_choice ===
~ input("What's your favorite color?", "color")
BUG
{color} is a great choice!

What would you like to do with this color?

+ Generate something about the color
    ~ generate("Write a short poem about the color {color} in 20 words")
    -> end
+ Skip generation
    -> end

=== number_choice ===
~ input("Pick a number between 1 and 10", "number")
BUG
You chose {number}.

What would you like to do with this number?

+ Generate something about the number
    ~ generate("Write a short story about the number {number} in 20 words")
    -> end
+ Skip generation
    -> end

=== skip_choice ===
Alright, let's move on.
-> end

=== end ===
The end!
-> END
        ''',
        author=user,
        public=True,
        creation_date=timezone.now(),
        edit_date=timezone.now(),
        description='Test story to check input/generate functionality'
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
    
    print(f'Successfully created input/generate test story with ID: {story.id}')
    return story.id 