"""Wrapper for Render.com deployment."""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
try:
    from examples.web_server import app
    print("Successfully imported Flask app from examples.web_server")
except ImportError as e:
    print(f"Failed to import app: {e}")
    
    # Show available files in the directory
    print("Files in current directory:")
    for item in os.listdir('.'):
        print(f"  - {item}")
    
    print("\nFiles in examples directory:")
    try:
        for item in os.listdir('./examples'):
            print(f"  - {item}")
    except:
        print("  Examples directory not found or not accessible")
    
    raise
