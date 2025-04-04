from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import os

LIGHT_GREEN = '\033[38;5;120m'
DEEP_GREEN = '\033[32m'
RESET = '\033[0m'

def print_green(message):
    print(f"{DEEP_GREEN}{message}{RESET}")

def print_bright_green(message):
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
        return story_div.text.strip()
    except Exception as e:
        print(f"Failed to get story text: {str(e)}")
        return ""

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

def test_story_path(driver, choices):
    """
    Test a complete story path with the given choices or inputs.
    Verifies all inputs, choices, and story text at each step.
    """
    try:
        # Initial setup and navigation
        url = os.environ.get('TEST_URL', "http://local.unfoldstudio.net:8000/stories/29/")
        print(f"\nTesting path with choices: {choices}")
        print(f"Attempting to load URL: {url}")
        
        driver.get(url)
        time.sleep(2)
        
        # Verify initial page load
        assert driver.current_url == url, f"URL mismatch. Expected: {url}, Got: {driver.current_url}"
        print_green("✓ Initial page loaded successfully")

        # Verify initial texts  
        assert_exact_texts(driver, [
            "This is a test story for input and generate functionality.",
            "Let's start with a simple input."
        ])
        print_green("✓ Initial texts verified successfully")
        
        # Enter name
        print("\nStep 1: Entering name...")
        # Verify input is empty and enabled
        assert_input_state(driver, "", True)
        input_box = wait_for_enabled_input(driver)
        input_box.send_keys(choices['name'])
        # Verify input contains name
        assert_input_state(driver, choices['name'], True)
        submit_button = wait_for_enabled_submit(driver)
        submit_button.click()
        time.sleep(2)
        # Verify texts appear in order
        assert_exact_texts(driver, [
            "Nice to meet you, "+ choices['name'] + "!",
            "Now let's test generate with some context.",
            "Let's try input after generate."
        ])
        print_green("✓ Name step completed successfully")
        
        # Enter food
        print("\nStep 2: Entering food...")
        # Verify new input is empty and enabled
        assert_input_state(driver, "", True)
        input_box = wait_for_enabled_input(driver)
        input_box.send_keys(choices['food'])
        # Verify input contains food
        assert_input_state(driver, choices['food'], True)
        submit_button = wait_for_enabled_submit(driver)
        submit_button.click()
        time.sleep(2)
        # Verify texts appear in order
        assert_exact_texts(driver, [
            "I see you like " + choices['food'] + ". Let's generate something about that.",
            "Now let's test input with choices.",
            "What would you like to do next?"
        ])
        print_green("✓ Food step completed successfully")
        
        # Select path
        print("\nStep 3: Selecting path...")
        path_choices = [
            "Choose a color",
            "Choose a number",
            "Skip both"
        ]
        # Verify the exact order of choices
        assert_exact_choices(driver, path_choices)
        
        # Select the specified path
        choice_text = path_choices[['color', 'number', 'skip'].index(choices['path'])]
        choice = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{choice_text}')]"))
        )
        choice.click()
        time.sleep(2)
        # Verify texts appear in order
        assert_exact_texts(driver, [
            "What would you like to do next?",
            choice_text
        ])
        print_green(f"✓ Selected path: {choice_text}")
        
        # Handle specific path
        if choices['path'] == 'color':
            print("\nStep 4: Handling color path...")
            # Verify color input is available
            assert_input_state(driver, "", True)
            input_box = wait_for_enabled_input(driver)
            input_box.send_keys(choices['color'])
            # Verify input contains color
            assert_input_state(driver, choices['color'], True)
            submit_button = wait_for_enabled_submit(driver)
            submit_button.click()
            time.sleep(2)
            # Verify texts appear in order
            assert_exact_texts(driver, [
                f"{choices['color']} is a great choice!",
                "What would you like to do with this color?"
            ])
            
            # Handle color generation choice
            choice_text = "Generate something about the color" if choices['generate_color'] else "Skip generation"
            # Replace individual assertions with exact list check
            assert_exact_choices(driver, [
                "Generate something about the color",
                "Skip generation"
            ])
            choice = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{choice_text}')]"))
            )
            choice.click()
            time.sleep(2)
            
            if choices['generate_color']:
                # Verify texts appear in order
                assert_exact_texts(driver, [
                    "Generate something about the color",
                    "The end!"
                ])
            else:
                # Verify texts appear in order
                assert_exact_texts(driver, [
                    "Skip generation",
                    "The end!"
                ])
            
            print_green(f"✓ Color path completed - Generation: {choices['generate_color']}")
            
        elif choices['path'] == 'number':
            print("\nStep 4: Handling number path...")
            # Verify number input is available
            assert_input_state(driver, "", True)
            input_box = wait_for_enabled_input(driver)
            input_box.send_keys(choices['number'])
            
            # Verify input contains number
            assert_input_state(driver, choices['number'], True)
            
            # Find and click the submit button
            submit_button = wait_for_enabled_submit(driver)
            submit_button.click()
            time.sleep(2)  # Wait for submission
            
            # Verify texts appear in order
            assert_exact_texts(driver, [
                f"You chose {choices['number']}.",
                "What would you like to do with this number?"
            ])
            
            # Handle number generation choice
            choice_text = "Generate something about the number" if choices['generate_number'] else "Skip generation"
            # Replace individual assertions with exact list check
            assert_exact_choices(driver, [
                "Generate something about the number",
                "Skip generation"
            ])
            choice = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{choice_text}')]"))
            )
            choice.click()
            time.sleep(2)
            
            if choices['generate_number']:
                # Verify texts appear in order
                assert_exact_texts(driver, [
                    "Generate something about the number",
                    "The end!"
                ])
            else:
                # Verify texts appear in order
                assert_exact_texts(driver, [
                    "Skip generation",
                    "The end!"
                ])
            
            print_green(f"✓ Number path completed - Generation: {choices['generate_number']}")
        
        elif choices['path'] == 'skip':
            print("\nStep 4: Handling skip path...")
            # Verify texts appear in order
            assert_exact_texts(driver, [
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
        print(driver.page_source[:1000])  # Print first 1000 chars for debugging
        raise e

def test_all_paths():
    """Run comprehensive tests for all possible story paths"""
    print("Starting comprehensive story testing...")
    
    # Chrome setup
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
    
    # Test paths covering all possible story branches
    test_paths = [
        # Color path with generation
        {
            'name': 'Asif1',
            'food': 'pizza',
            'path': 'color',
            'color': 'blue',
            'generate_color': True
        },
        # Color path without generation
        {
            'name': 'Asif2',
            'food': 'sushi',
            'path': 'color',
            'color': 'red',
            'generate_color': False
        },
        # Number path with generation
        {
            'name': 'Asif3',
            'food': 'tacos',
            'path': 'number',
            'number': '7',
            'generate_number': True
        },
        # Number path without generation
        {
            'name': 'Asif4',
            'food': 'pasta',
            'path': 'number',
            'number': '3',
            'generate_number': False
        },
        # Skip path
        {
            'name': 'Asif5',
            'food': 'burger',
            'path': 'skip'
        }
    ]
    
    try:
        for index, path in enumerate(test_paths, 1):
            print_bright_green(f"\n=== Running Test #{index} ===")
            test_story_path(driver, path)
            print_bright_green(f"=== Test #{index} Completed ===\n")
            driver.delete_all_cookies()
            time.sleep(2)
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    test_all_paths() 