from dataclasses import fields, is_dataclass
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QSpinBox, QDoubleSpinBox, QComboBox
)

from custom_widgets import PathSelectorWidget

class SettingsUIBuilder:
    """Builds the Qt UI from a settings dataclass."""

    def __init__(self):
        self.widget_map = {}

    def build_ui(self, settings_obj: Any, parent_layout: QVBoxLayout) -> Dict[str, QWidget]:
        """
        Generates the UI for the given settings object and populates the parent layout.
        Returns a map of setting keys to their corresponding widgets.
        """
        self.widget_map.clear()
        self._create_ui_from_dataclass(settings_obj, parent_layout, "MasterSettings")
        return self.widget_map

    def _create_ui_from_dataclass(self, dc_instance: Any, parent_layout: QVBoxLayout, base_key: str):
        """Recursively generates UI elements for a dataclass instance."""
        for f in fields(dc_instance):
            key = f"{base_key}.{f.name}"
            value = getattr(dc_instance, f.name)
            tooltip = f.metadata.get("tooltip", f.name)
            setting_type = f.metadata.get("setting_type")

            if is_dataclass(value):
                group_box = QGroupBox(f.name)
                group_box.setToolTip(tooltip)
                group_box_layout = QVBoxLayout(group_box)
                parent_layout.addWidget(group_box)
                self._create_ui_from_dataclass(value, group_box_layout, key)
            else:
                h_layout = QHBoxLayout()
                label = QLabel(f"{f.name}:")
                label.setToolTip(tooltip)
                h_layout.addWidget(label)

                widget = self._create_widget_for_value(value, tooltip, setting_type)
                self.widget_map[key] = widget
                h_layout.addWidget(widget, 1)
                parent_layout.addLayout(h_layout)

    def _create_widget_for_value(self, value: Any, tooltip: str, setting_type: str | None) -> QWidget:
        """Creates an appropriate widget for a given data type."""
        widget: QWidget
        if setting_type in ["folder", "file"]:
            widget = PathSelectorWidget(selection_mode=setting_type)
            widget.setText(str(value))
        elif isinstance(value, bool):
            widget = QComboBox()
            widget.addItems(["True", "False"])
            widget.setCurrentText(str(value))
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setRange(-1000000, 1000000)
            widget.setValue(value)
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setDecimals(4)
            widget.setRange(-1000000.0, 1000000.0)
            widget.setValue(value)
        elif isinstance(value, dict):
            widget = QTreeWidget()
            widget.setHeaderLabels(["Key", "Value"])
            widget.setAlternatingRowColors(True)
            self._populate_tree_from_dict(widget, value)
            widget.expandAll()
            widget.setMinimumHeight(200)
        else:
            widget = QLineEdit(str(value))

        widget.setToolTip(tooltip)
        return widget

    def _populate_tree_from_dict(self, tree_widget: QTreeWidget, data: Dict):
        """Populates a QTreeWidget from a dictionary."""
        tree_widget.clear()
        for key, value in data.items():
            parent_item = QTreeWidgetItem(tree_widget, [key, ""])
            self._add_tree_items(parent_item, value)

    def _add_tree_items(self, parent_item: QTreeWidgetItem, value: Any):
        """Recursive helper to add items to the tree."""
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