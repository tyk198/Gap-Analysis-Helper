from dataclasses import fields, is_dataclass
from typing import Any, Dict
import tkinter as tk
from tkinter import ttk

from .custom_widgets import PathSelectorWidget, FoilsSelectorWidget, CollapsibleSection

class SettingsUIBuilder:
    """Builds the Tkinter UI from a settings dataclass."""

    def __init__(self):
        self.widget_map = {}

    def build_ui(self, settings_obj: Any, parent: tk.Frame) -> Dict[str, tk.Widget]:
        self.widget_map.clear()
        self._create_ui_from_dataclass(settings_obj, parent, "MasterSettings", -1)
        return self.widget_map

    def _create_ui_from_dataclass(self, dc_instance: Any, parent: tk.Frame, base_key: str, level: int):
        """Recursively generates UI elements for a dataclass instance."""
        
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.X)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        processed_groups = set()

        for f in fields(dc_instance):
            if not f.metadata.get("visible_in_ui", True):
                continue

            layout_group = f.metadata.get("layout_group")

            if layout_group and layout_group in processed_groups:
                continue

            is_dc = is_dataclass(f.type)

            if is_dc:
                key = f"{base_key}.{f.name}"
                value = getattr(dc_instance, f.name)
                label_text = f.metadata.get("label", f.name)

                section = CollapsibleSection(parent, label_text)
                section.pack(fill=tk.X, padx=5, pady=5)
                self._create_ui_from_dataclass(value, section.contentLayout(), key, level + 1)
            else:
                key = f"{base_key}.{f.name}"
                value = getattr(dc_instance, f.name)
                setting_type = f.metadata.get("setting_type")
                widget_type = f.metadata.get("widget_type")
                widget_style = f.metadata.get("widget_style")
                label_text = f.metadata.get("label", f.name)

                if layout_group == "left":
                    if widget_type == "foils_selector":
                        label = tk.Label(left_frame, text=f"{label_text}:")
                        label.pack(side=tk.TOP, anchor='w')
                        widget = self._create_widget_for_value(left_frame, value, setting_type, widget_type, widget_style)
                        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                        self.widget_map[key] = widget
                    else:
                        row_frame = tk.Frame(left_frame)
                        row_frame.pack(side=tk.TOP, fill=tk.X)
                        label = tk.Label(row_frame, text=f"{label_text}:")
                        label.pack(side=tk.LEFT)
                        widget = self._create_widget_for_value(row_frame, value, setting_type, widget_type, widget_style)
                        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                        self.widget_map[key] = widget
                else:
                    target_frame = right_frame
                    row_frame = tk.Frame(target_frame)
                    row_frame.pack(fill=tk.X, pady=2)
                    
                    if layout_group:
                        processed_groups.add(layout_group)
                        group_fields = [field for field in fields(dc_instance) if field.metadata.get("layout_group") == layout_group]
                    else:
                        group_fields = [f]

                    for field_in_group in group_fields:
                        key = f"{base_key}.{field_in_group.name}"
                        value = getattr(dc_instance, field_in_group.name)
                        setting_type = field_in_group.metadata.get("setting_type")
                        widget_type = field_in_group.metadata.get("widget_type")
                        widget_style = field_in_group.metadata.get("widget_style")
                        label_text = field_in_group.metadata.get("label", field_in_group.name)

                        label = tk.Label(row_frame, text=f"{label_text}:")
                        label.pack(side=tk.LEFT, padx=(0, 5))

                        widget = self._create_widget_for_value(row_frame, value, setting_type, widget_type, widget_style)
                        self.widget_map[key] = widget
                        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)


    def _create_widget_for_value(self, parent: tk.Frame, value: Any, setting_type: str | None, widget_type: str | None, widget_style: str | None) -> tk.Widget:
        widget: tk.Widget
        if widget_type == "foils_selector":
            widget = FoilsSelectorWidget(parent)
        elif setting_type in ["folder", "file"]:
            icon_only = widget_style == "icon_only"
            widget = PathSelectorWidget(parent, selection_mode=setting_type, icon_only=icon_only)
            widget.set(str(value))
        elif isinstance(value, bool):
            widget = ttk.Combobox(parent, values=["True", "False"])
            widget.set(str(value))
        elif isinstance(value, int) or isinstance(value, float):
            widget = tk.Entry(parent)
            widget.insert(0, str(value))
        elif isinstance(value, dict):
            widget = ttk.Treeview(parent)
            # Simplified version, see custom_widgets.py
        else:
            widget = tk.Entry(parent)
            widget.insert(0, str(value))

        return widget