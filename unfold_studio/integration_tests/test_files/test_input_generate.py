import os
from unfold_studio.integration_tests.test_files.test_utils import (
    print_green,
    wait_for_story_text,
    assert_exact_choices,
    assert_exact_texts_in_order,
    initialize_chrome_driver,
    type_input,
    submit_input,
    click_choice,
    assert_input_box_exists
)

def test_story_path(driver, choices):
    try:
        host = os.environ.get('DJANGO_HOST', 'localhost')
        port = os.environ.get('DJANGO_PORT', '8000')
        story_id = 29
        url = f"http://{host}:{port}/stories/{story_id}/"

        print(f"Attempting to load URL: {url}")
        
        driver.get(url)
        assert driver.current_url == url, f"URL mismatch. Expected: {url}, Got: {driver.current_url}"
        print_green("✓ Initial page loaded successfully")

        wait_for_story_text(driver, "This is a test story for input and generate functionality.")

        assert_exact_texts_in_order(driver, [
            "This is a test story for input and generate functionality.",
            "Let's start with a simple input."
        ])
        print_green("✓ Initial texts verified successfully")


        print("\nStep 1: Entering name...")

        assert_input_box_exists(driver, "What's your name?")
        type_input(driver, choices['name'])
        submit_input(driver)
        
        wait_for_story_text(driver, "Let's try input after generate.")
        
        assert_exact_texts_in_order(driver, [
            "Let's start with a simple input.",
            f"Nice to meet you, {choices['name']}!",
            "Now let's test generate with some context.",
            "Let's try input after generate."
        ])
        print_green("✓ Name step completed successfully")
        
        print("\nStep 2: Entering food...")

        assert_input_box_exists(driver, "What's your favorite food?")
        type_input(driver, choices['food'])
        submit_input(driver)
        
        wait_for_story_text(driver, "What would you like to do next?")
        
        assert_exact_texts_in_order(driver, [
            f"I see you like {choices['food']}. Let's generate something about that.",
            "Now let's test input with choices.",
            "What would you like to do next?"
        ])
        print_green("✓ Food step completed successfully")
        
        print("\nStep 3: Selecting path...")

        assert_exact_choices(driver, [
            "Choose a color",
            "Choose a number",
            "Skip both"
        ])
        
        click_choice(driver, choices['choice1'])
        
        assert_exact_texts_in_order(driver, [
            "What would you like to do next?",
            choices['choice1']
        ])
        print_green(f"✓ Selected path: {choices['choice1']}")
        
        if 'color' in choices:
            print("\nStep 4: Handling color path...")

            assert_input_box_exists(driver, "What's your favorite color?")
            type_input(driver, choices['color'])
            submit_input(driver)
            
            assert_exact_texts_in_order(driver, [
                f"{choices['color']} is a great choice!",
                "What would you like to do with this color?"
            ])
            
            assert_exact_choices(driver, [
                "Generate something about the color",
                "Skip generation"
            ])
            
            click_choice(driver, choices['choice2'])
            
            wait_for_story_text(driver, "The end!")
            
            assert_exact_texts_in_order(driver, [
                choices['choice2'],
                "The end!"
            ])
            
            print_green(f"✓ Color path completed - Choice: {choices['choice2']}")
            
        elif 'number' in choices:
            print("\nStep 4: Handling number path...")

            assert_input_box_exists(driver, "Pick a number between 1 and 10")
            type_input(driver, choices['number'])
            submit_input(driver)
            
            assert_exact_texts_in_order(driver, [
                f"You chose {choices['number']}.",
                "What would you like to do with this number?"
            ])
            
            assert_exact_choices(driver, [
                "Generate something about the number",
                "Skip generation"
            ])
            
            click_choice(driver, choices['choice2'])
            
            wait_for_story_text(driver, "The end!")
            
            assert_exact_texts_in_order(driver, [
                choices['choice2'],
                "The end!"
            ])
            
            print_green(f"✓ Number path completed - Choice: {choices['choice2']}")
        
        else:
            print("\nStep 4: Handling skip path...")

            assert_exact_texts_in_order(driver, [
                "Alright, let's move on.",
                "The end!"
            ])
            print_green("✓ Skip path completed")
        
        print_green("\n✓ Path completed successfully with all assertions passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        print("\nCurrent page source:")
        print(driver.page_source[:1000])
        raise e

def test_all_paths():
    print("Starting input/generate story testing...")
    
    test_paths = [
        {
            'name': 'Asif1',
            'food': 'pizza',
            'choice1': 'Choose a color',
            'color': 'blue',
            'choice2': 'Generate something about the color'
        },
        {
            'name': 'Asif2',
            'food': 'sushi',
            'choice1': 'Choose a color',
            'color': 'red',
            'choice2': 'Skip generation'
        },
        {
            'name': 'Asif3',
            'food': 'tacos',
            'choice1': 'Choose a number',
            'number': '7',
            'choice2': 'Generate something about the number'
        },
        {
            'name': 'Asif4',
            'food': 'pasta',
            'choice1': 'Choose a number',
            'number': '3',
            'choice2': 'Skip generation'
        },
        {
            'name': 'Asif5',
            'food': 'burger',
            'choice1': 'Skip both'
        }
    ]
    
    driver = None
    try:
        driver = initialize_chrome_driver()
        for i, path in enumerate(test_paths, 1):
            print(f"\n{'='*50}")
            print(f"Running test path {i} of {len(test_paths)}")
            print(f"Test path details: {path}")
            print(f"{'='*50}\n")
            test_story_path(driver, path)
            print(f"\n✓ Test path {i} completed successfully\n")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_all_paths()