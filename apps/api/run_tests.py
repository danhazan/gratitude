#!/usr/bin/env python3
"""
Simple test runner for Grateful API
This script runs tests in a WSL-compatible way.
"""

import subprocess
import sys
import os

def run_basic_tests():
    """Run basic endpoint tests that don't require database."""
    print("🧪 Running basic endpoint tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit/test_basic.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True, timeout=30)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_all_tests():
    """Run all tests with proper async handling."""
    print("🧪 Running all tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", "--tb=short", "--asyncio-mode=auto"
    ], capture_output=True, text=True, timeout=120)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def main():
    """Main test runner."""
    print("🚀 Grateful API Test Runner")
    print("=" * 40)
    
    # Run basic tests first
    print("\n1. Testing basic endpoints...")
    basic_success = run_basic_tests()
    
    if basic_success:
        print("✅ Basic tests passed!")
        
        # Ask if user wants to run all tests
        print("\n2. Run all tests (including database tests)?")
        print("   Note: This may take longer and requires database setup.")
        response = input("   Continue? (y/n): ").lower().strip()
        
        if response == 'y':
            all_success = run_all_tests()
            if all_success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed.")
        else:
            print("⏭️  Skipping full test suite.")
    else:
        print("❌ Basic tests failed!")

if __name__ == "__main__":
    main() 