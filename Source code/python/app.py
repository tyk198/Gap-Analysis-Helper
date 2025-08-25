import sys
import json
from dataclasses import fields, is_dataclass, asdict
from typing import Any, Dict

# PySide6 Imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QGroupBox, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QMessageBox, QSpinBox, QDoubleSpinBox,
    QComboBox
)
from PySide6.QtCore import Qt
from settings import MasterSettings


class SettingsEditor(QMainWindow):
    """A GUI for editing a MasterSettings dataclass instance."""

    def __init__(self, settings: MasterSettings):
        super().__init__()
        self.settings_obj = settings
        self.widget_map = {}

        self.setWindowTitle("Settings Editor")
        self.setGeometry(100, 100, 800, 600)

        # Main container and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # Add a scroll area for potentially long settings
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.scroll_area.setWidget(self.settings_container)

        # Create UI from the settings object
        self.create_ui_from_dataclass(self.settings_obj, self.settings_layout, "MasterSettings")

        # Add Save and Load buttons
        self.setup_buttons()

    def setup_buttons(self):
        """Creates and configures the Save and Load buttons."""
        button_layout = QHBoxLayout()
        self.main_layout.addLayout(button_layout)

        load_button = QPushButton("Load from JSON")
        load_button.clicked.connect(self.load_settings)
        button_layout.addWidget(load_button)

        save_button = QPushButton("Save to JSON")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)

    def create_ui_from_dataclass(self, dc_instance: Any, parent_layout: QVBoxLayout, base_key: str):
        """Recursively generates UI elements for a dataclass instance."""
        for f in fields(dc_instance):
            key = f"{base_key}.{f.name}"
            value = getattr(dc_instance, f.name)
            tooltip = f.metadata.get("tooltip", f.name)

            if is_dataclass(value):
                group_box = QGroupBox(f.name)
                group_box.setToolTip(tooltip)
                group_box_layout = QVBoxLayout(group_box)
                parent_layout.addWidget(group_box)
                self.create_ui_from_dataclass(value, group_box_layout, key)
            else:
                h_layout = QHBoxLayout()
                label = QLabel(f"{f.name}:")
                label.setToolTip(tooltip)
                h_layout.addWidget(label)

                widget = self.create_widget_for_value(value, tooltip)
                self.widget_map[key] = widget
                h_layout.addWidget(widget, 1) # Give widget more horizontal space
                parent_layout.addLayout(h_layout)

    def create_widget_for_value(self, value: Any, tooltip: str) -> QWidget:
        """Creates an appropriate widget for a given data type."""
        widget: QWidget
        if isinstance(value, bool):
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
            self.populate_tree_from_dict(widget, value)
            widget.expandAll()
            widget.setMinimumHeight(200) # Give tree widgets some default space
        else: # Default to string
            widget = QLineEdit(str(value))

        widget.setToolTip(tooltip)
        return widget

    def populate_tree_from_dict(self, tree_widget: QTreeWidget, data: Dict):
        """Populates a QTreeWidget from a dictionary."""
        tree_widget.clear()
        for key, value in data.items():
            parent_item = QTreeWidgetItem(tree_widget, [key, ""])
            self._add_tree_items(parent_item, value)

    def _add_tree_items(self, parent_item: QTreeWidgetItem, value: Any):
        """Recursive helper to add items to the tree."""
        if isinstance(value, dict):
            parent_item.setText(1, "") # Parent node has no value
            for key, val in value.items():
                child_item = QTreeWidgetItem(parent_item, [key, ""])
                self._add_tree_items(child_item, val)
        elif isinstance(value, list):
            parent_item.setText(1, str(value))
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsEditable)
        else:
            parent_item.setText(1, str(value))
            parent_item.setFlags(parent_item.flags() | Qt.ItemIsEditable)

    def save_settings(self):
        """Saves the current GUI state to a JSON file."""
        try:
            updated_settings = self.rebuild_dataclass_from_ui()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON Files (*.json)")

            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(asdict(updated_settings), f, indent=4)
                QMessageBox.information(self, "Success", f"Settings saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def load_settings(self):
        """Loads settings from a JSON file and updates the GUI."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Create a new MasterSettings instance from the loaded data
            # NOTE: This assumes the JSON structure matches the dataclass structure
            def create_from_dict(cls, data_dict):
                field_names = {f.name for f in fields(cls)}
                filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
                
                for f in fields(cls):
                    if is_dataclass(f.type) and f.name in filtered_data:
                        filtered_data[f.name] = create_from_dict(f.type, filtered_data[f.name])
                
                return cls(**filtered_data)

            self.settings_obj = create_from_dict(MasterSettings, data)

            # Clear old UI and rebuild
            # Clean up existing widgets in the layout
            while self.settings_layout.count():
                child = self.settings_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.widget_map.clear()
            self.create_ui_from_dataclass(self.settings_obj, self.settings_layout, "MasterSettings")
            QMessageBox.information(self, "Success", f"Settings loaded from {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")

    def rebuild_dataclass_from_ui(self) -> MasterSettings:
        """Reconstructs the MasterSettings object from the current UI values."""
        new_data = {}
        for key, widget in self.widget_map.items():
            path = key.split('.')[1:] # Remove "MasterSettings." prefix
            current_level = new_data

            for i, part in enumerate(path):
                if i == len(path) - 1:
                    current_level[part] = self.get_value_from_widget(widget)
                else:
                    current_level = current_level.setdefault(part, {})

        # Use the loaded data to create a new dataclass instance
        # This is a simple way to reconstruct; a more robust solution might
        # recursively create dataclass instances.
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


    def get_value_from_widget(self, widget: QWidget) -> Any:
        """Retrieves the value from a widget, converting it to the correct type."""
        if isinstance(widget, QComboBox):
            return widget.currentText() == "True"
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QDoubleSpinBox):
            return widget.value()
        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QTreeWidget):
            return self.get_dict_from_tree(widget)
        return None

    def get_dict_from_tree(self, tree: QTreeWidget) -> Dict:
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
            # Try to evaluate as a literal (handles lists, numbers, booleans)
            return json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            # If it fails, return it as a plain string
            return value_str


app = QApplication(sys.argv)

initial_settings = MasterSettings()

editor = SettingsEditor(settings=initial_settings)
editor.show()

sys.exit(app.exec())
