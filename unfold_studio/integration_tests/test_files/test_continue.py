from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green
from unfold_studio.integration_tests.constants import CONTINUE_INPUT_BOX_PLACEHOLDER
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

        self.click_choice(path["choice_1"])

        self.assert_exact_texts_in_order([
            "This is a integration test story for continue.",
            "Let's call the continue function now.",
            path["choice_1"],
        ])

        self.assert_input_box_exists(CONTINUE_INPUT_BOX_PLACEHOLDER)
        self.type_input(path["continue_1_input"])
        self.submit_input()

        if path["choice_1"] == "Go to direct continue knot":
            self.wait_for_story_text("This is the final knot text.")
            self.assert_exact_texts_in_order([
                "You are inside direct_continue_knot",
                "This is the final knot text.",
            ])

        elif path["choice_1"] == "Go to bridge and continue knot":
            self.wait_for_story_text("This is the final knot text.")
            self.assert_exact_texts_in_order([
                "You are inside bridge_and_continue_knot",
                "After following through with your input, the journey continues, leading you closer to the final destination..",
                "This is the final knot text.",
            ])
        elif path["choice_1"] == "Go to needs input knot":
            self.wait_for_story_text("This is the needs input knot text.")
        elif path["choice_1"] == "Go to invalid user input knot":
            self.wait_for_story_text("This is the invalid user input knot text.")


if __name__ == "__main__":
    test_paths = [
        {
            "choice_1": "Go to direct continue knot",
            "continue_1_input": "direct_continue_input"
        },
        {   
            "choice_1": "Go to bridge and continue knot",
            "continue_1_input": "bridge_and_continue_input"
        },
        # {
        #     "choice_1": "Go to needs input knot",
        #     "continue_1_input": "needs_input_input"
        # },
        # {
        #     "choice_1": "Go to invalid user input knot",
        #     "continue_1_input": "invalid_user_input"
        # }

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
