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

# ANSI color codes for terminal output
LIGHT_GREEN = '\033[38;5;120m'
DEEP_GREEN = '\033[32m'
RESET = '\033[0m'

def initialize_chrome_driver():
    """Initialize and return a configured Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-browser-side-navigation')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Use system Chrome binary if available
    if os.environ.get('CHROME_BIN'):
        chrome_options.binary_location = os.environ.get('CHROME_BIN')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    return driver

def print_green(message):
    """Print a message in green color."""
    print(f"{DEEP_GREEN}{message}{RESET}")

def print_bright_green(message):
    """Print a message in bright green color."""
    print(f"\033[1;{LIGHT_GREEN}{message}{RESET}")

def wait_for_enabled_input(driver, timeout=10):
    """Wait for and return the most recent enabled input field"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            input_boxes = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
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

def wait_for_enabled_submit(driver, timeout=10):
    """Wait for and return the most recent enabled submit button"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
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

def get_story_text(driver):
    """Return the current story text from the page"""
    try:
        story_div = driver.find_element(By.CLASS_NAME, "innerText")
        return story_div.text.replace("Submit", "").strip()
    except Exception as e:
        print(f"Failed to get story text: {str(e)}")
        return ""

def wait_for_story_text(driver, text, timeout=10):
    """Wait for specific text to appear in the story."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: text in get_story_text(d)
        )
        return True
    except TimeoutException:
        print(f"✗ Timeout waiting for text: '{text}'")
        print(f"Current story text: '{get_story_text(driver)}'")
        return False

def assert_input_state(driver, expected_value="", should_be_enabled=True):
    """Verify the state and value of the most recent input box"""
    try:
        input_boxes = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if not input_boxes:
            raise AssertionError("No input boxes found")
        
        latest_input = input_boxes[-1]
        actual_value = latest_input.get_attribute("value")
        is_enabled = not latest_input.get_attribute("disabled")
        
        if actual_value != expected_value:
            raise AssertionError(f"Input value mismatch. Expected: '{expected_value}', Got: '{actual_value}'")
        
        if is_enabled != should_be_enabled:
            raise AssertionError(f"Input enabled state mismatch. Expected: {should_be_enabled}, Got: {is_enabled}")
            
        print_green(f"✓ Input state verified - Value: '{actual_value}', Enabled: {is_enabled}")
        return True
    except Exception as e:
        print(f"✗ Failed to verify input state: {str(e)}")
        raise

def assert_exact_choices(driver, expected_choices):
    """
    Verify that the latest choices in the story exactly match the expected choices in order.
    Only checks links within the story content area (.innerText, .story-content).
    """
    try:
        # Find story-specific choice links
        choices = driver.find_elements(By.CSS_SELECTOR, ".innerText a, .story-content a")
        latest_choices = choices[-len(expected_choices):]
        
        if len(latest_choices) != len(expected_choices):
            print(f"✗ Number of choices mismatch. Expected {len(expected_choices)}, found {len(latest_choices)}")
            print(f"All choices found: {[c.text.strip() for c in choices]}")
            raise AssertionError("Incorrect number of choices")
            
        # Verify each choice matches in order
        for i, (actual, expected) in enumerate(zip(latest_choices, expected_choices)):
            actual_text = actual.text.strip()
            if actual_text != expected:
                print(f"✗ Choice mismatch at position {i+1}. Expected: '{expected}', Got: '{actual_text}'")
                print(f"All choices found: {[c.text.strip() for c in choices]}")
                raise AssertionError(f"Choice mismatch at position {i+1}")
            print_green(f"✓ Choice verified at position {i+1}: '{actual_text}'")
            
        print_green("✓ All choices verified in exact order")
        return True
    except Exception as e:
        print(f"✗ Failed to verify choices: {str(e)}")
        raise

def assert_exact_texts(driver, expected_texts, timeout=10):
    """
    Verify that the expected texts appear in order within the story history.
    Checks the entire story text and ensures texts appear in the specified sequence.
    """
    try:
        story_text = get_story_text(driver)

        lines = [line.strip() for line in story_text.split('\n') if line.strip()]
        if not lines:
            print(f"✗ No text found in story")
            print(f"Current story text: '{story_text}'")
            raise AssertionError("No text found in story")
            
        # Verify text sequence
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
            
        print_green("✓ Found all expected texts in correct order in story history")
        return True
    except Exception as e:
        print(f"✗ Failed to verify texts: {str(e)}")
        raise 