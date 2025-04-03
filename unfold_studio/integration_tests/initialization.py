import os
import django
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from unfold_studio.models import Story

def initialize_test_environment():
    """
    Initialize the test environment by creating necessary test data.
    Returns the created story ID.
    """
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unfold_studio.settings')
    django.setup()
    
    # Create test user
    user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
    
    # Get the default site
    site = Site.objects.get(id=1)
    
    # Create test story
    story = Story.objects.create(
        id=29,
        title='Test Story',
        ink='''
VAR name = """"
VAR food = """"
VAR color = """"
VAR number = """"
VAR story = """"

This is a test story for input and generate functionality.

Let's start with a simple input.
~ input(""What's your name?"", ""name"")
BUG
Nice to meet you, {name}!

Now let's test generate with some context.
~ generate(""Write a short greeting for {name}"")

Let's try input after generate.
~ input(""What's your favorite food?"", ""food"")
BUG
I see you like {food}. Let's generate something about that.
~ generate(""Write a short description about why {name} might like {food} in 20 words"")

Now let's test input with choices.
What would you like to do next?

+ Choose a color
    -> color_choice
+ Choose a number
    -> number_choice
+ Skip both
    -> skip_choice

=== color_choice ===
~ input(""What's your favorite color?"", ""color"")
BUG
{color} is a great choice!

What would you like to do with this color?

+ Generate something about the color
    ~ generate(""Write a short poem about the color {color} in 20 words"")
    -> end
+ Skip generation
    -> end

=== number_choice ===
~ input(""Pick a number between 1 and 10"", ""number"")
BUG
You chose {number}.

What would you like to do with this number?

+ Generate something about the number
    ~ generate(""Write a short story about the number {number} in 20 words"")
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
        description='Test story for integration tests'
    )
    story.sites.add(site)
    
    # Compile the story
    story.compile()
    story.save()
    
    print(f'Created test story with ID: {story.id}')
    print(f'Story JSON: {story.json}')
    
    return story.id

if __name__ == '__main__':
    initialize_test_environment() 