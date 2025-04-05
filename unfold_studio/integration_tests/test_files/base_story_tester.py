from selenium.webdriver.common.by import By
import os
from selenium.common.exceptions import TimeoutException
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os



LIGHT_GREEN = '\033[38;5;120m'
DEEP_GREEN = '\033[32m'
RESET = '\033[0m'

class BaseStoryTester:
    """Base class for story testing with common functionality"""
    
    def __init__(self, test_paths, story_id, driver):
        self.test_paths = test_paths
        self.story_id = story_id
        self.driver = driver

    def setup(self):
        self.host = os.environ.get('DJANGO_HOST', 'localhost')
        self.port = os.environ.get('DJANGO_PORT', '8000')
        self.url = f"http://{self.host}:{self.port}/stories/{self.story_id}/"

    def load_story(self):
        print(f"Loading story from {self.url}")
        self.driver.get(self.url)
        assert self.driver.current_url == self.url, f"URL mismatch. Expected: {self.url}, Got: {self.driver.current_url}"
        self.print_green("✓ Initial page loaded successfully")

    def run_all_tests(self):
        print(f"Starting {self.__class__.__name__} testing...")
        
        for i, path in enumerate(self.test_paths, 1):
            print(f"\n{'='*50}")
            self.print_bright_green(f"Running test path {i} of {len(self.test_paths)}")
            self.print_bright_green(f"Test path details: {path}")
            self.print_bright_green(f"{'='*50}\n")
            self.test_story_path(path)
            self.print_bright_green(f"\n✓ Test path {i} completed successfully\n")

        
    def teardown(self):
        if self.driver:
            try:
                print("Quitting driver")
                self.driver.quit()
                print("Driver quit")
            except Exception as e:
                print(f"Error quitting driver: {str(e)}")

    def print_green(self, message):
        print(f"{DEEP_GREEN}{message}{RESET}")

    def print_bright_green(self, message):
        print(f"\033[1;{LIGHT_GREEN}{message}{RESET}")

    def _get_story_text(self):
        try:
            story_div = self.driver.find_element(By.CLASS_NAME, "innerText")
            return story_div.text.replace("Submit", "").strip()
        except Exception as e:
            print(f"Failed to get story text: {str(e)}")
            return ""
            
    def submit_input(self):
        submit_button = self._wait_for_enabled_submit()
        submit_button.click()
        time.sleep(0.5)

    def type_input(self, text):   
        input_box = self._wait_for_enabled_input()
        input_box.clear()
        input_box.send_keys(text)

    def click_choice(self, choice_text):
        choice = self._wait_for_choice(choice_text)
        choice.click()
        time.sleep(0.5)

    def assert_input_box_exists(self, placeholder):
        input_box = self._wait_for_input_box_with_placeholder(placeholder)
        self.print_green(f"✓ Found input box with placeholder: '{placeholder}'")
        return input_box 
    
    def assert_exact_choices(self, expected_choices):
        try:
            choices = self.driver.find_elements(By.CSS_SELECTOR, ".innerText a, .story-content a")
            latest_choices = choices[-len(expected_choices):]
            
            if len(latest_choices) != len(expected_choices):
                print(f"✗ Number of choices mismatch. Expected {len(expected_choices)}, found {len(latest_choices)}")
                print(f"All choices found: {[c.text.strip() for c in choices]}")
                raise AssertionError("Incorrect number of choices")
                
            for i, (actual, expected) in enumerate(zip(latest_choices, expected_choices)):
                actual_text = actual.text.strip()
                if actual_text != expected:
                    print(f"✗ Choice mismatch at position {i+1}. Expected: '{expected}', Got: '{actual_text}'")
                    print(f"All choices found: {[c.text.strip() for c in choices]}")
                    raise AssertionError(f"Choice mismatch at position {i+1}")
                self.print_green(f"✓ Choice verified at position {i+1}: '{actual_text}'")
                
            self.print_green("✓ All choices verified in exact order")
            return True
        except Exception as e:
            print(f"✗ Failed to verify choices: {str(e)}")
            raise

    def assert_exact_texts_in_order(self,expected_texts, timeout=10):
        try:
            story_text = self._get_story_text()

            lines = [line.strip() for line in story_text.split('\n') if line.strip()]
            if not lines:
                print(f"✗ No text found in story")
                print(f"Current story text: '{story_text}'")
                raise AssertionError("No text found in story")
                
            current_line_idx = 0
            current_expected_idx = 0
            
            while current_line_idx < len(lines) and current_expected_idx < len(expected_texts):
                if expected_texts[current_expected_idx] == lines[current_line_idx]:
                    current_expected_idx += 1
                current_line_idx += 1
                
            if current_expected_idx < len(expected_texts):
                missing_texts = expected_texts[current_expected_idx:]
                print(f"✗ Not all expected texts found in correct order")
                print(f"Missing texts: {missing_texts}")
                print(f"Story lines: {lines}")
                raise AssertionError(f"Expected texts not found in correct order: {missing_texts}")
                
            self.print_green("✓ Found all expected texts in correct order in story history")
            return True
        except Exception as e:
            print(f"✗ Failed to verify texts: {str(e)}")
            raise
        
    def _wait_for_enabled_input(self, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                input_boxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if not input_boxes:
                    time.sleep(0.1)
                    continue
                latest_input = input_boxes[-1]
                if not latest_input.get_attribute("disabled"):
                    return latest_input
            except:
                pass
            time.sleep(0.5)
        raise TimeoutException("Input field did not become enabled within timeout period")

    def _wait_for_enabled_submit(self, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                if not submit_buttons:
                    time.sleep(0.1)
                    continue
                latest_button = submit_buttons[-1]
                if latest_button.is_enabled():
                    return latest_button
            except:
                pass
            time.sleep(0.5)
        raise TimeoutException("Submit button did not become enabled within timeout period")

    def _wait_for_choice(self, choice_text):
        start_time = time.time()
        timeout = 10  # Use same default timeout as other functions
        
        while time.time() - start_time < timeout:
            try:
                choices = self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{choice_text}')]")
                if not choices:
                    time.sleep(0.1)
                    continue
                for choice in choices:
                    if choice.is_displayed() and choice.is_enabled():
                        return choice
            except:
                pass
            time.sleep(0.5)
        raise TimeoutException(f"Choice '{choice_text}' not found or not clickable within {timeout} seconds")

    def wait_for_story_text(self, text, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: text in self._get_story_text()
            )
        except TimeoutException:
            current_text = self._get_story_text()
            raise TimeoutException(
                f"Timeout waiting for text: '{text}'\n"
                f"Current story text: '{current_text}'"
            )
        
    def _wait_for_input_box_with_placeholder(self, placeholder):
        start_time = time.time()
        timeout = 10
        
        while time.time() - start_time < timeout:
            try:
                input_boxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                if not input_boxes:
                    time.sleep(0.1)
                    continue
                latest_input = input_boxes[-1]
                if (latest_input.is_displayed() and 
                    latest_input.is_enabled() and 
                    latest_input.get_attribute('placeholder') == placeholder):
                    return latest_input
            except:
                pass
            time.sleep(0.5)
        raise TimeoutException(f"Input box with placeholder '{placeholder}' not found or not enabled within {timeout} seconds")
