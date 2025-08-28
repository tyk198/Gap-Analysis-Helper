from dataclasses import fields, is_dataclass
from typing import Any, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTreeWidget, QTreeWidgetItem, QComboBox, QFrame, QSizePolicy
)

from .custom_widgets import PathSelectorWidget, FoilsSelectorWidget, CollapsibleSection

SECTION_COLORS = ["#E6F1F6", "#E6F6E8", "#F6F3E6", "#F6E6E6", "#F1E6F6", "#F6E6F1"]

class SettingsUIBuilder:
    """Builds the Qt UI from a settings dataclass."""

    def __init__(self):
        self.widget_map = {}

    def build_ui(self, settings_obj: Any, parent_layout: QVBoxLayout) -> Dict[str, QWidget]:
        self.widget_map.clear()
        self._create_ui_from_dataclass(settings_obj, parent_layout, "MasterSettings", -1)
        return self.widget_map

    def _create_ui_from_dataclass(self, dc_instance: Any, parent_layout: QVBoxLayout, base_key: str, level: int):
        """Recursively generates UI elements for a dataclass instance."""
        
        main_h_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        main_h_layout.addLayout(left_layout, 1)
        main_h_layout.addLayout(right_layout, 2)

        parent_layout.addLayout(main_h_layout)

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
                tooltip = f.metadata.get("tooltip", f.name)
                label_text = f.metadata.get("label", f.name)

                if level >= 0:
                    color = SECTION_COLORS[level % len(SECTION_COLORS)]
                    section_container = CollapsibleSection(label_text, color)
                    content_layout = section_container.contentLayout()
                else:
                    section_container = QFrame()
                    section_container.setFrameShape(QFrame.NoFrame)
                    content_layout = QVBoxLayout(section_container)
                    content_layout.setContentsMargins(0,0,0,0)
                
                section_container.setToolTip(tooltip)
                parent_layout.addWidget(section_container)
                self._create_ui_from_dataclass(value, content_layout, key, level + 1)
            else:
                h_layout = QHBoxLayout()
                
                if layout_group:
                    processed_groups.add(layout_group)
                    group_fields = [field for field in fields(dc_instance) if field.metadata.get("layout_group") == layout_group]
                else:
                    group_fields = [f]

                for field_in_group in group_fields:
                    key = f"{base_key}.{field_in_group.name}"
                    value = getattr(dc_instance, field_in_group.name)
                    tooltip = field_in_group.metadata.get("tooltip", field_in_group.name)
                    setting_type = field_in_group.metadata.get("setting_type")
                    widget_type = field_in_group.metadata.get("widget_type")
                    widget_style = field_in_group.metadata.get("widget_style")
                    label_text = field_in_group.metadata.get("label", field_in_group.name)

                    label = QLabel(f"{label_text}:")
                    label.setToolTip(tooltip)

                    widget = self._create_widget_for_value(value, tooltip, setting_type, widget_type, widget_style)
                    self.widget_map[key] = widget

                    if widget_style == "icon_only":
                        h_layout.addWidget(label)
                        h_layout.addWidget(widget)
                        h_layout.addStretch()
                    elif widget_type == "foils_selector":
                        v_layout = QVBoxLayout()
                        v_layout.addWidget(label)
                        v_layout.addWidget(widget)
                        h_layout.addLayout(v_layout)
                    else:
                        h_layout.addWidget(label)
                        h_layout.addWidget(widget, 1)
                
                if layout_group == "left":
                    left_layout.addLayout(h_layout)
                elif layout_group == "right" or layout_group in ["image_size", "fm_size"]:
                    right_layout.addLayout(h_layout)
                elif not layout_group:
                    right_layout.addLayout(h_layout)


    def _create_widget_for_value(self, value: Any, tooltip: str, setting_type: str | None, widget_type: str | None, widget_style: str | None) -> QWidget:
        widget: QWidget
        if widget_type == "foils_selector":
            widget = FoilsSelectorWidget()
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        elif setting_type in ["folder", "file"]:
            icon_only = widget_style == "icon_only"
            widget = PathSelectorWidget(selection_mode=setting_type, icon_only=icon_only)
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
