from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green
from unfold_studio.integration_tests.constants import DEFAULT_GENERATE_RESPONSE_TEXT

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


if __name__ == "__main__":
    test_paths = [
        {},
        {},
        {},
    ]
    
    try:
        driver = initialize_chrome_driver()
        tester = ContinueTester(test_paths, 33, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        tester.teardown()
