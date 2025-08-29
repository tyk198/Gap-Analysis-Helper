import json
from dataclasses import fields, is_dataclass, asdict
from typing import Any, Dict, List
import os
import tkinter as tk
from tkinter import ttk

from .settings import MasterSettings
from .custom_widgets import PathSelectorWidget, FoilsSelectorWidget

class SettingsService:
    """Handles the business logic for settings management."""

    def load_from_json(self, file_path: str) -> MasterSettings:
        """Loads settings from a JSON file and returns a new MasterSettings instance."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"Successfully loaded settings from {file_path}")
        except FileNotFoundError:
            print("settings file not found, use default settings")
            return MasterSettings()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}, using default settings instead.")
            return MasterSettings()
        
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
        folder_path = 'python/tkinter_app'
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

    def build_dataclass_from_ui(self, widget_map: Dict[str, tk.Widget]) -> MasterSettings:
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

    def _get_value_from_widget(self, widget: tk.Widget, field_type: Any) -> Any:
        """Retrieves the value from a widget, converting it to the correct type."""
        if isinstance(widget, FoilsSelectorWidget):
            return widget.get_selected_as_dict()
        if isinstance(widget, PathSelectorWidget):
            return widget.get()
        if isinstance(widget, ttk.Combobox):
            return widget.get() == "True"
        
        if isinstance(widget, tk.Entry):
            text = widget.get()
            if field_type is int:
                try: return int(text)
                except (ValueError, TypeError): return 0
            elif field_type is float:
                try: return float(text)
                except (ValueError, TypeError): return 0.0
            return text

        if isinstance(widget, ttk.Treeview):
            return self._get_dict_from_tree(widget)
        return None

    def _get_dict_from_tree(self, tree: ttk.Treeview) -> Dict:
        """Converts a ttk.Treeview's content back into a dictionary."""
        result = {}
        for item_id in tree.get_children():
            key = tree.item(item_id, "text")
            children = tree.get_children(item_id)
            if children:
                result[key] = self._get_child_dict(tree, children)
            else:
                # This is a simplified version. A more complex implementation would be needed to get values.
                pass
        return result

    def _get_child_dict(self, tree: ttk.Treeview, children: List[str]) -> Dict:
        """Recursive helper to get child dictionaries from a tree item."""
        child_dict = {}
        for child_id in children:
            key = tree.item(child_id, "text")
            grandchildren = tree.get_children(child_id)
            if grandchildren:
                child_dict[key] = self._get_child_dict(tree, grandchildren)
            else:
                # This is a simplified version.
                pass
        return child_dict
