from unfold_studio.integration_tests.test_files.base_story_tester import BaseStoryTester
from unfold_studio.integration_tests.utils import initialize_chrome_driver
from unfold_studio.integration_tests.utils import print_green
from unfold_studio.integration_tests.constants import DEFAULT_GENERATE_RESPONSE_TEXT

class InputCompileErrorTester(BaseStoryTester):
        
    def test_story_path(self, choices):
        try:
            self.load_story()

            self.assert_error_message("Input variables must be defined before use. Undefined variables: name")
            
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
    test_paths = [{}]
    
    try:
        driver = initialize_chrome_driver()
        tester = InputCompileErrorTester(test_paths, 4, driver)
        tester.setup()
        tester.run_all_tests()
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        raise
    finally:
        if tester and hasattr(tester, 'driver') and tester.driver:
            tester.teardown()