import json
import os
from pathlib import Path
from typing import Any, Optional

from actions import ALL_ACTIONS
from actions.base_action import BaseAction

ACTION_CLASSES = {cls.__name__: cls for cls in ALL_ACTIONS}


def create_action(action_type: str) -> Optional[BaseAction]:
    cls = ACTION_CLASSES.get(action_type)
    if cls:
        return cls()
    return None


def get_action_by_type(action_type: str) -> Optional[type]:
    return ACTION_CLASSES.get(action_type)


class Workflow:
    def __init__(self, name: str = "Untitled Workflow"):
        self.name = name
        self.actions: list[BaseAction] = []
        self.description: str = ""

    def add_action(self, action: BaseAction, index: Optional[int] = None):
        if index is not None:
            self.actions.insert(index, action)
        else:
            self.actions.append(action)

    def remove_action(self, index: int):
        if 0 <= index < len(self.actions):
            self.actions.pop(index)

    def move_action(self, from_index: int, to_index: int):
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)

    def clear(self):
        self.actions.clear()

    def get_action_count(self) -> int:
        return len(self.actions)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "actions": [a.to_dict() for a in self.actions],
        }

    def save_to_file(self, filepath: str):
        data = self.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        wf = cls(name=data.get("name", "Untitled"))
        wf.description = data.get("description", "")
        for act_data in data.get("actions", []):
            action = create_action(act_data.get("action_type", ""))
            if action:
                action.load_config(act_data.get("config", {}))
                wf.actions.append(action)
        return wf

    @classmethod
    def load_from_file(cls, filepath: str) -> "Workflow":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class WorkflowEngine:
    def __init__(self):
        self.current_input: Any = None
        self.log_callback = None

    def set_log_callback(self, callback):
        self.log_callback = callback

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)

    def run(self, workflow: Workflow, initial_input: Any = None) -> tuple[bool, Any]:
        self.current_input = initial_input
        data = initial_input
        success = True
        try:
            for i, action in enumerate(workflow.actions):
                ok, msg = action.validate()
                if not ok:
                    self.log(f"[{i + 1}] {action.display_name()}: FAILED - {msg}")
                    success = False
                    break
                self.log(f"[{i + 1}] {action.display_name()}: {action.display_summary()}...")
                data = action.run(data)
                self.log(f"[{i + 1}] {action.display_name()}: Done")
            if success:
                self.log("Workflow completed successfully!")
            return success, data
        except Exception as e:
            self.log(f"Error: {str(e)}")
            return False, str(e)
