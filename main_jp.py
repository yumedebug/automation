"""
Automator - ワークフロー自動化ツール（日本語版）
MacのAutomator風のドラッグ＆ドロップ操作で作業を自動化します。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n import set_japanese
set_japanese()

if __name__ == "__main__":
    from automator_app import launch_gui
    launch_gui()
