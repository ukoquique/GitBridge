#!/usr/bin/env python3
"""
Standalone launcher for GitBridge GUI application.
Simply run this file to start the GitBridge application.
"""
import sys
import os
import tkinter as tk

# Add the parent directory to the path so we can import gitbridge modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the GUI application
    from gitbridge.gui_app import GitBridgeGUI
    
    # Display a splash message
    print("Starting GitBridge GUI...")
    print("A tool for managing Git repositories across different accounts")
    print("Copyright © 2025 ukoquique")
    
    # Launch the application
    if __name__ == "__main__":
        GitBridgeGUI()
        
except ImportError as e:
    print(f"Error importing GitBridge modules: {e}")
    print("Make sure you're running this script from the GitBridge directory.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting GitBridge: {e}")
    sys.exit(1)
