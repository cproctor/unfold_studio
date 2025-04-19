from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green

class ContinueTester(BaseStoryTester):
        
    def test_story_path(self, path):
        self.load_story()
        self.wait_for_story_text("This is a integration test story for continue.")

        print("Step 1: Verifying initial texts")
        self.assert_exact_texts_in_order([
            "This is a integration test story for continue.",
            "Let's call the continue function now."

        ])
        print_green("✓ Initial texts verified successfully")

        self.click_choice("Go to continue function call knot")

        self.assert_exact_texts_in_order([
            "This is a integration test story for continue.",
            "Let's call the continue function now.",
            "Go to continue function call knot",
            "You are inside continue function knot"
        ])

        self.assert_input_box_exists("what would you like to do next?")
        self.type_input(path["continue_1_input"])
        self.submit_input()

        self.wait_for_story_text("This is the final knot text.")


if __name__ == "__main__":
    test_paths = [
        {"continue_1_input": "nothing"}
    ]
    
    try:
        driver = initialize_chrome_driver()
        tester = ContinueTester(test_paths, 0, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        tester.teardown()
