"""
Automator - Windows Workflow Automation Tool
Inspired by Mac Automator. Drag & drop workflow builder with GUI.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from automator_app import launch_gui
    launch_gui()
