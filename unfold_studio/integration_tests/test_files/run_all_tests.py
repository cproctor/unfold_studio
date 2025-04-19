import os
import sys
import subprocess
from unfold_studio.integration_tests.utils import print_green, print_bright_green

def run_test_file(file_path):
    print_bright_green(f"\nRunning tests from {file_path}")
    try:
        result = subprocess.run([sys.executable, file_path], check=True)
        print_green(f"✓ {file_path} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {file_path} failed with error: {str(e)}")
        return False

def main():
    test_files_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        # 'test_input_generate.py',
        # 'test_input_generate2.py',
        # 'test_input_generate3.py',
        'test_continue.py'
    ]
    
    success_count = 0
    total_tests = len(test_files)
    
    print_bright_green(f"\nStarting {total_tests} test files...")
    
    for test_file in test_files:
        file_path = os.path.join(test_files_dir, test_file)
        if run_test_file(file_path):
            success_count += 1
    
    print_bright_green(f"\nTest Summary:")
    print(f"Total tests run: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    
    if success_count == total_tests:
        print_green("✓ All tests passed successfully!")
    else:
        print("✗ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 