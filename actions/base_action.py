from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Optional


class ParameterType(Enum):
    TEXT = auto()
    NUMBER = auto()
    FILE = auto()
    FOLDER = auto()
    FILES = auto()
    CHOICE = auto()
    BOOLEAN = auto()
    COLOR = auto()


class ActionCategory(Enum):
    FILES_FOLDERS = "Files & Folders"
    IMAGES = "Images"
    TEXT = "Text"
    SYSTEM = "System"
    INPUT_OUTPUT = "Input / Output"
    FILTER = "Filter"


@dataclass
class ActionParameter:
    name: str
    label: str
    param_type: ParameterType
    default: Any = None
    required: bool = True
    choices: list[str] = field(default_factory=list)
    description: str = ""
    label_ja: str = ""
    choices_ja: list[str] = field(default_factory=list)

    def display_label(self) -> str:
        from i18n import is_japanese
        return self.label_ja if is_japanese() and self.label_ja else self.label

    def display_choices(self) -> list[str]:
        from i18n import CHOICES_JA, is_japanese
        if not is_japanese():
            return self.choices
        if self.choices_ja:
            return self.choices_ja
        return [CHOICES_JA.get(c, c) for c in self.choices]


class BaseAction:
    name: str = ""
    description: str = ""
    icon: str = ""
    category: ActionCategory = ActionCategory.SYSTEM
    parameters: list[ActionParameter] = []
    name_ja: str = ""
    description_ja: str = ""
    summary_ja_template: str = ""

    def __init__(self):
        self.config: dict[str, Any] = {}
        for p in self.parameters:
            self.config[p.name] = p.default

    def display_name(self) -> str:
        from i18n import is_japanese
        return self.name_ja if is_japanese() and self.name_ja else self.name

    def display_description(self) -> str:
        from i18n import is_japanese
        return self.description_ja if is_japanese() and self.description_ja else self.description

    def display_summary(self) -> str:
        return self.summary()

    def set_config(self, key: str, value: Any):
        self.config[key] = value

    def get_config(self, key: str) -> Any:
        return self.config.get(key)

    def get_config_dict(self) -> dict:
        return dict(self.config)

    def load_config(self, config: dict):
        for p in self.parameters:
            self.config[p.name] = config.get(p.name, p.default)

    def summary(self) -> str:
        return self.name

    def run(self, input_data: Any) -> Any:
        raise NotImplementedError

    def validate(self) -> tuple[bool, str]:
        for p in self.parameters:
            if p.required:
                val = self.config.get(p.name)
                if val is None:
                    return False, f"'{p.display_label()}' is required"
                if isinstance(val, str) and val.strip() == "":
                    return False, f"'{p.display_label()}' is required"
                if isinstance(val, (list, tuple)) and len(val) == 0:
                    return False, f"'{p.display_label()}' is required"
        return True, ""

    def to_dict(self) -> dict:
        return {
            "action_type": self.__class__.__name__,
            "config": self.get_config_dict(),
        }
