from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green

class InputGenerateTester(BaseStoryTester):
        
    def test_story_path(self, choices):
        try:
            self.load_story()

            self.wait_for_story_text("This is a test story for input and generate functionality.")

            self.assert_exact_texts_in_order([
                "This is a test story for input and generate functionality.",
                "Let's start with a simple input."
            ])
            print_green("✓ Initial texts verified successfully")

            print("\nStep 1: Entering name...")
            self.assert_input_box_exists("What's your name?")
            self.type_input(choices['name'])
            self.submit_input()
            
            self.wait_for_story_text("Let's try input after generate.")
            
            self.assert_exact_texts_in_order([
                "Let's start with a simple input.",
                f"Nice to meet you, {choices['name']}!",
                "Now let's test generate with some context.",
                "cached gen text yayyyyyyyy",
                "Let's try input after generate."
            ])
            print_green("✓ Name step completed successfully")
            
            print("\nStep 2: Entering food...")
            self.assert_input_box_exists("What's your favorite food?")
            self.type_input(choices['food'])
            self.submit_input()
            
            self.wait_for_story_text("What would you like to do next?")
            
            self.assert_exact_texts_in_order([
                f"I see you like {choices['food']}. Let's generate something about that.",
                "Now let's test input with choices.",
                "What would you like to do next?"
            ])
            print_green("✓ Food step completed successfully")
            
            print("\nStep 3: Selecting path...")
            self.assert_exact_choices([
                "Choose a color",
                "Choose a number",
                "Skip both"
            ])
            
            self.click_choice(choices['choice1'])
            
            self.assert_exact_texts_in_order([
                "What would you like to do next?",
                choices['choice1']
            ])
            print_green(f"✓ Selected path: {choices['choice1']}")
            
            if 'color' in choices:
                print("\nStep 4: Handling color path...")
                self.assert_input_box_exists("What's your favorite color?")
                self.type_input(choices['color'])
                self.submit_input()
                
                self.assert_exact_texts_in_order([
                    f"{choices['color']} is a great choice!",
                    "What would you like to do with this color?"
                ])
                
                self.assert_exact_choices([
                    "Generate something about the color",
                    "Skip generation"
                ])
                
                self.click_choice(choices['choice2'])
                
                self.wait_for_story_text("The end!")
                
                self.assert_exact_texts_in_order([
                    choices['choice2'],
                    "The end!"
                ])
                
                print_green(f"✓ Color path completed - Choice: {choices['choice2']}")
                
            elif 'number' in choices:
                print("\nStep 4: Handling number path...")
                self.assert_input_box_exists("Pick a number between 1 and 10")
                self.type_input(choices['number'])
                self.submit_input()
                
                self.assert_exact_texts_in_order([
                    f"You chose {choices['number']}.",
                    "What would you like to do with this number?"
                ])
                
                self.assert_exact_choices([
                    "Generate something about the number",
                    "Skip generation"
                ])
                
                self.click_choice(choices['choice2'])
                
                self.wait_for_story_text("The end!")
                
                self.assert_exact_texts_in_order([
                    choices['choice2'],
                    "The end!"
                ])
                
                print_green(f"✓ Number path completed - Choice: {choices['choice2']}")
            
            else:
                print("\nStep 4: Handling skip path...")
                self.assert_exact_texts_in_order([
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
            print(self.driver.page_source[:1000])
            raise e

if __name__ == "__main__":
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
    
    try:
        driver = initialize_chrome_driver()
        tester = InputGenerateTester(test_paths, 29, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        if tester and hasattr(tester, 'driver') and tester.driver:
            tester.teardown()