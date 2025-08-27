import json
from dataclasses import fields, is_dataclass, asdict
from typing import Any, Dict, List, List

from PySide6.QtWidgets import QWidget, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt

from settings import MasterSettings
from custom_widgets import PathSelectorWidget, FoilsSelectorWidget
import os

class SettingsService:
    """Handles the business logic for settings management."""

    def load_from_json(self, file_path: str) -> MasterSettings:
        """Loads settings from a JSON file and returns a new MasterSettings instance."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        def create_from_dict(cls, data_dict):
            field_names = {f.name for f in fields(cls)}
            filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
            
            for f in fields(cls):
                if is_dataclass(f.type) and f.name in filtered_data:
                    filtered_data[f.name] = create_from_dict(f.type, filtered_data[f.name])
            
            return cls(**filtered_data)

        return create_from_dict(MasterSettings, data)

    def save_to_json(self, settings: MasterSettings):
        """Saves a MasterSettings instance to a JSON file."""
        folder_path = 'python/app'
        settings_file_path  = os.path.join(folder_path, 'settings.json')
        os.makedirs(folder_path, exist_ok=True)
        with open(settings_file_path, 'w') as f:
            json.dump(asdict(settings), f, indent=4)

    def _get_field_type_from_path(self, path: list[str]) -> Any:
        """Inspects the MasterSettings dataclass to find the type of a nested field."""
        current_type = MasterSettings
        for part in path:
            found = False
            for f in fields(current_type):
                if f.name == part:
                    current_type = f.type
                    found = True
                    break
            if not found:
                return None
        return current_type

    def build_dataclass_from_ui(self, widget_map: Dict[str, QWidget]) -> MasterSettings:
        """Reconstructs the MasterSettings object from the current UI values."""
        new_data = {}
        for key, widget in widget_map.items():
            path = key.split('.')[1:]
            current_level = new_data

            for i, part in enumerate(path):
                if i == len(path) - 1:
                    field_type = self._get_field_type_from_path(path)
                    current_level[part] = self._get_value_from_widget(widget, field_type)
                else:
                    current_level = current_level.setdefault(part, {})
        
        def dict_to_dataclass(cls, data):
            field_values = {}
            for f in fields(cls):
                if f.name in data:
                    if is_dataclass(f.type):
                        field_values[f.name] = dict_to_dataclass(f.type, data[f.name])
                    else:
                        field_values[f.name] = data[f.name]
            return cls(**field_values)
        
        return dict_to_dataclass(MasterSettings, new_data)

    def _get_value_from_widget(self, widget: QWidget, field_type: Any) -> Any:
        """Retrieves the value from a widget, converting it to the correct type."""
        if isinstance(widget, FoilsSelectorWidget):
            return widget.get_selected_as_dict()
        if isinstance(widget, PathSelectorWidget):
            return widget.text()
        if isinstance(widget, QComboBox):
            return widget.currentText() == "True"
        
        if isinstance(widget, QLineEdit):
            text = widget.text()
            if (hasattr(field_type, '__origin__') and field_type.__origin__ is list) or field_type is list:
                items = []
                for item in text.split(','):
                    item = item.strip()
                    if item:
                        try:
                            items.append(int(item))
                        except ValueError:
                            # Ignore non-integer values
                            pass
                return items

            if field_type is int:
                try: return int(text)
                except (ValueError, TypeError): return 0
            elif field_type is float:
                try: return float(text)
                except (ValueError, TypeError): return 0.0
            return text

        if isinstance(widget, QTreeWidget):
            return self._get_dict_from_tree(widget)
        return None

    def _get_dict_from_tree(self, tree: QTreeWidget) -> Dict:
        """Converts a QTreeWidget's content back into a dictionary."""
        result = {}
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            key = item.text(0)
            if item.childCount() > 0:
                result[key] = self._get_child_dict(item)
            else:
                result[key] = self._parse_value(item.text(1))
        return result

    def _get_child_dict(self, item: QTreeWidgetItem) -> Dict:
        """Recursive helper to get child dictionaries from a tree item."""
        child_dict = {}
        for i in range(item.childCount()):
            child = item.child(i)
            key = child.text(0)
            if child.childCount() > 0:
                child_dict[key] = self._get_child_dict(child)
            else:
                child_dict[key] = self._parse_value(child.text(1))
        return child_dict

    def _parse_value(self, value_str: str) -> Any:
        """Tries to intelligently parse a string value from the GUI to a Python type."""
        try:
            return json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            return value_str