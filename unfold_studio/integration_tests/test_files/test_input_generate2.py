from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green
from unfold_studio.integration_tests.constants import DEFAULT_GENERATE_RESPONSE_TEXT

class InputGenerateTester2(BaseStoryTester):
        
    def test_story_path(self, path):
        self.load_story()
        self.wait_for_story_text("Welcome to the Interactive Story Test!")

        print("Step 1: Verifying initial texts")
        self.assert_exact_texts_in_order([
            "Welcome to the Interactive Story Test!",
            "Let's start with some basic information."
        ])
        print_green("✓ Initial texts verified successfully")

        print("Step 2: Entering name")
        self.assert_input_box_exists("What's your name?")
        self.type_input(path['name'])
        self.submit_input()
        self.assert_exact_texts_in_order([
            f"Hello {path['name']}!",
            "Now, let's get to know you better."
        ])
        print_green(f"✓ Name '{path['name']}' entered successfully")
        
        print("Step 3: Entering age")
        self.assert_input_box_exists("How old are you?")
        self.type_input(path['age'])
        self.submit_input()
        self.assert_exact_texts_in_order([
            f"{path['age']} is a great age!",
            "Let's generate something about your age."
        ])
        print_green(f"✓ Age '{path['age']}' entered successfully")
        
        print("Step 4: Waiting for age generation")
        self.wait_for_story_text("What would you like to do next?")
        self.assert_exact_texts_in_order([
            "Let's generate something about your age.",
            DEFAULT_GENERATE_RESPONSE_TEXT,
            "What would you like to do next?",
        ])
        print_green("✓ Age generation completed")
        
        print(f"Step 5: Choosing path '{path['choice1']}'")
        self.click_choice(path['choice1'])
        
        if path['choice1'] == "Share your hobby":
            print(f"Step 6: Entering hobby '{path['hobby']}'")
            self.assert_input_box_exists("What's your favorite hobby?")
            self.type_input(path['hobby'])
            self.submit_input()
            self.assert_exact_texts_in_order([
                path['choice1'],
                f"I love {path['hobby']} too!",
                "Would you like to:"
            ])
            print_green(f"✓ Hobby '{path['hobby']}' entered successfully")
            
            print(f"Step 7: Choosing hobby option '{path['choice2']}'")
            self.click_choice(path['choice2'])
            self.wait_for_story_text("Let's wrap up with one final generation.")
            self.assert_exact_texts_in_order([
                path['choice2'],
                DEFAULT_GENERATE_RESPONSE_TEXT,
                "Let's wrap up with one final generation."
            ])
            print_green("✓ Hobby generation completed")
        elif path['choice1'] == "Share your dream":
            print(f"Step 6: Entering dream '{path['dream']}'")
            self.assert_input_box_exists("What's your biggest dream?")
            self.type_input(path['dream'])
            self.submit_input()
            self.assert_exact_texts_in_order([
                path['choice1'],
                f"That's an amazing dream! {path['dream']} is inspiring.",
                "Would you like to:"
            ])
            print_green(f"✓ Dream '{path['dream']}' entered successfully")
            
            print(f"Step 7: Choosing dream option '{path['choice2']}'")
            self.click_choice(path['choice2'])
            self.wait_for_story_text("Let's wrap up with one final generation.")
            self.assert_exact_texts_in_order([
                path['choice2'],
                DEFAULT_GENERATE_RESPONSE_TEXT,
                "Let's wrap up with one final generation."
            ])
            print_green("✓ Dream generation completed")
        else:
            print("Step 6: Skipping to end")
            self.wait_for_story_text("Let's wrap up with one final generation.")
            print_green("✓ Skipped to end successfully")
        
        print("Step 8: Final generation and end")
        self.wait_for_story_text("Thank you for participating!")
        self.assert_exact_texts_in_order([
            "Let's wrap up with one final generation.",
            DEFAULT_GENERATE_RESPONSE_TEXT,
            "Thank you for participating!"
        ])
        print_green("✓ Final generation completed")
        print_green("✓ Path completed successfully with all assertions passed!")

if __name__ == "__main__":
    test_paths = [
        {
            'name': 'Alice',
            'age': '25',
            'choice1': 'Share your hobby',
            'hobby': 'painting',
            'choice2': 'Generate a story about your hobby'
        },
        {
            'name': 'Bob',
            'age': '30',
            'choice1': 'Share your hobby',
            'hobby': 'gaming',
            'choice2': 'Generate a poem about your hobby'
        },
        {
            'name': 'Charlie',
            'age': '20',
            'choice1': 'Share your dream',
            'dream': 'becoming an astronaut',
            'choice2': 'Generate a plan to achieve it'
        },
        {
            'name': 'Diana',
            'age': '35',
            'choice1': 'Share your dream',
            'dream': 'opening a cafe',
            'choice2': 'Generate a motivational quote'
        },
        {
            'name': 'Eve',
            'age': '28',
            'choice1': 'Skip to the end'
        }
    ]
    
    try:
        driver = initialize_chrome_driver()
        tester = InputGenerateTester2(test_paths, 2, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        tester.teardown()
