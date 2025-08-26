from dataclasses import fields, is_dataclass
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTreeWidget, QTreeWidgetItem, QComboBox
)

from custom_widgets import PathSelectorWidget, FoilsSelectorWidget, CollapsibleSection

SECTION_COLORS = ["#E6F1F6", "#E6F6E8", "#F6F3E6", "#F6E6E6", "#F1E6F6", "#F6E6F1"]

class SettingsUIBuilder:
    """Builds the Qt UI from a settings dataclass."""

    def __init__(self):
        self.widget_map = {}

    def build_ui(self, settings_obj: Any, parent_layout: QVBoxLayout) -> Dict[str, QWidget]:
        self.widget_map.clear()
        self._create_ui_from_dataclass(settings_obj, parent_layout, "MasterSettings", -1) # Start level at -1
        return self.widget_map

    def _create_ui_from_dataclass(self, dc_instance: Any, parent_layout: QVBoxLayout, base_key: str, level: int):
        """Recursively generates UI elements for a dataclass instance."""
        for f in fields(dc_instance):
            if not f.metadata.get("visible_in_ui", True):
                continue

            key = f"{base_key}.{f.name}"
            value = getattr(dc_instance, f.name)
            tooltip = f.metadata.get("tooltip", f.name)
            setting_type = f.metadata.get("setting_type")
            widget_type = f.metadata.get("widget_type")
            label_text = f.metadata.get("label", f.name)

            if is_dataclass(value):
                # Only color sections inside the top level
                color = SECTION_COLORS[level % len(SECTION_COLORS)] if level >= 0 else "transparent"
                
                section = CollapsibleSection(label_text, color)
                section.setToolTip(tooltip)
                parent_layout.addWidget(section)
                # Pass the content layout of the new section for the recursive call
                self._create_ui_from_dataclass(value, section.contentLayout(), key, level + 1)
            else:
                h_layout = QHBoxLayout()
                label = QLabel(f"{label_text}:")
                label.setToolTip(tooltip)
                h_layout.addWidget(label)

                widget = self._create_widget_for_value(value, tooltip, setting_type, widget_type)
                self.widget_map[key] = widget
                h_layout.addWidget(widget, 1)
                parent_layout.addLayout(h_layout)

    def _create_widget_for_value(self, value: Any, tooltip: str, setting_type: str | None, widget_type: str | None) -> QWidget:
        widget: QWidget
        if widget_type == "foils_selector":
            widget = FoilsSelectorWidget()
        elif setting_type in ["folder", "file"]:
            widget = PathSelectorWidget(selection_mode=setting_type)
            widget.setText(str(value))
        elif isinstance(value, bool):
            widget = QComboBox()
            widget.addItems(["True", "False"])
            widget.setCurrentText(str(value))
        elif isinstance(value, int):
            widget = QLineEdit(str(value))
            widget.setValidator(QIntValidator())
        elif isinstance(value, float):
            widget = QLineEdit(str(value))
            widget.setValidator(QDoubleValidator())
        elif isinstance(value, dict):
            widget = QTreeWidget()
            widget.setHeaderLabels(["Key", "Value"])
            self._populate_tree_from_dict(widget, value)
            widget.expandAll()
        else:
            widget = QLineEdit(str(value))

        widget.setToolTip(tooltip)
        return widget

    def _populate_tree_from_dict(self, tree_widget: QTreeWidget, data: Dict):
        tree_widget.clear()
        for key, value in data.items():
            parent_item = QTreeWidgetItem(tree_widget, [key, ""])
            self._add_tree_items(parent_item, value)

    def _add_tree_items(self, parent_item: QTreeWidgetItem, value: Any):
        if isinstance(value, dict):
            parent_item.setText(1, "")
            for key, val in value.items():
                child_item = QTreeWidgetItem(parent_item, [key, ""])
                self._add_tree_items(child_item, val)
        elif isinstance(value, list):
            parent_item.setText(1, str(value))
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsEditable)
        else:
            parent_item.setText(1, str(value))
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsEditable)
