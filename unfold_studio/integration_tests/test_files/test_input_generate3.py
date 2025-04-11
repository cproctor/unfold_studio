from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green
from unfold_studio.integration_tests.constants import *

class InputGenerateTester3(BaseStoryTester):
        
    def test_story_path(self, path):
        self.load_story()
        self.wait_for_story_text("Welcome to the Input/Generate Test Story3!")

        print("Step 1: Verifying initial texts")
        self.assert_exact_texts_in_order([
            "Welcome to the Input/Generate Test Story3!",
            "Let's test different combinations of input and generate functions.",
            "First, let's test input followed by generate."
        ])
        print_green("✓ Initial texts verified successfully")

        print("\nStep 2: Testing input followed by generate")
        self.assert_input_box_exists("What's your name?")
        self.type_input(path['name'])
        self.submit_input()
        
        self.wait_for_story_text("Now, let's test generate followed by input.")
        self.assert_exact_texts_in_order([
            f"First, let's test input followed by generate.",
            GENERATE_RESPONSE_TEXT_1,
            "Now, let's test generate followed by input."
        ])
        print_green("✓ Input followed by generate test completed")

        print("\nStep 3: Testing generate followed by input")
        self.assert_input_box_exists("What's your favorite food?")
        self.type_input(path['food'])
        self.submit_input()
        print_green("✓ Generate followed by input test completed")

        self.assert_exact_texts_in_order([
            "Now, let's test generate followed by input.",
            GENERATE_RESPONSE_TEXT_2,
            "Let's test multiple inputs in sequence."
        ])

        print("\nStep 4: Testing multiple inputs in sequence")
        self.assert_input_box_exists("What's your favorite color?")
        self.type_input(path['color'])
        self.submit_input()
        
        self.assert_input_box_exists("Pick a number between 1 and 10")
        self.type_input(path['number'])
        self.submit_input()
        print_green("✓ Multiple inputs test completed")

        print("\nStep 5: Testing multiple generates in sequence")
        self.wait_for_story_text("Let's test input after multiple generates.")
        self.assert_exact_texts_in_order([
            GENERATE_RESPONSE_TEXT_3,
            GENERATE_RESPONSE_TEXT_4,
            "Let's test input after multiple generates."
        ])
        print_green("✓ Multiple generates test completed")

        print("\nStep 6: Testing input after multiple generates")
        self.assert_input_box_exists("What's your favorite animal?")
        self.assert_exact_texts_in_order([
            "Let's test input after multiple generates.",
            GENERATE_RESPONSE_TEXT_5,
            GENERATE_RESPONSE_TEXT_6,
        ])
        self.type_input(path['animal'])
        self.submit_input()
        print_green("✓ Input after multiple generates test completed")

        print("\nStep 7: Testing generate after multiple inputs")
        self.assert_input_box_exists("What's your favorite season?")
        self.type_input(path['season'])
        self.submit_input()
        
        self.assert_input_box_exists("What's your favorite weather?")
        self.type_input(path['weather'])
        self.submit_input()
        
        self.wait_for_story_text("Here's a summary of your inputs:")
        self.assert_exact_texts_in_order([
            GENERATE_RESPONSE_TEXT_7,
            "Here's a summary of your inputs:",
            f"Name: {path['name']}",
            f"Food: {path['food']}",
            f"Color: {path['color']}",
            f"Number: {path['number']}",
            f"Animal: {path['animal']}",
            f"Season: {path['season']}",
            f"Weather: {path['weather']}"
        ])
        print_green("✓ Generate after multiple inputs test completed")

        print("\nStep 8: Testing end choices")
        self.assert_exact_choices(["End story"])
        self.click_choice("End story")
        print_green("✓ End choices test completed")


if __name__ == "__main__":
    test_paths = [
        {
            'name': 'Asif',
            'food': 'pizza',
            'color': 'blue',
            'number': '7',
            'animal': 'dolphin',
            'season': 'summer',
            'weather': 'sunny'
        },
    ]
    
    try:
        driver = initialize_chrome_driver()
        tester = InputGenerateTester3(test_paths, 45, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        tester.teardown()
