import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QFileDialog, QMessageBox
)

from .settings import MasterSettings
from .settings_service import SettingsService
from .ui_builder import SettingsUIBuilder
from .custom_widgets import PathSelectorWidget, FoilsSelectorWidget

class MainWindow(QMainWindow):
    """The main application window for the Settings Editor."""

    def __init__(self, settings: MasterSettings):
        super().__init__()
        self.settings_obj = settings
        self.settings_service = SettingsService()
        self.ui_builder = SettingsUIBuilder()
        self.widget_map = {}

        self.setWindowTitle("Settings Editor")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.scroll_area.setWidget(self.settings_container)

        self._build_ui()
        self._setup_buttons()

    def _build_ui(self):
        """Clears the existing UI and rebuilds it from the current settings object."""
        while self.settings_layout.count():
            child = self.settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    nested_child = child.layout().takeAt(0)
                    if nested_child.widget():
                        nested_child.widget().deleteLater()

        self.widget_map = self.ui_builder.build_ui(self.settings_obj, self.settings_layout)
        self._connect_dependent_widgets()

    def _setup_buttons(self):
        """Creates and configures the Save and Load buttons."""
        button_layout = QHBoxLayout()
        self.main_layout.addLayout(button_layout)

        load_button = QPushButton("Load from JSON")
        load_button.clicked.connect(self._load_settings)
        button_layout.addWidget(load_button)

        save_button = QPushButton("Save to JSON")
        save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(save_button)

    def _connect_dependent_widgets(self):
        """Connects widgets whose state depends on other widgets."""
        data_path_widget = self.widget_map.get("MasterSettings.Dakar.data")
        foils_selector = self.widget_map.get("MasterSettings.Dakar.foils_to_plot")

        if isinstance(data_path_widget, PathSelectorWidget) and isinstance(foils_selector, FoilsSelectorWidget):
            initial_path = data_path_widget.text()
            initial_selections = self.settings_obj.Dakar.foils_to_plot
            foils_selector.set_data_path(initial_path, initial_selections)

            data_path_widget.line_edit.textChanged.connect(
                lambda text: foils_selector.set_data_path(text, {})
            )

    def _load_settings(self):
        """Loads settings from a JSON file and updates the GUI."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            self.settings_obj = self.settings_service.load_from_json(file_path)
            self._build_ui()
            QMessageBox.information(self, "Success", f"Settings loaded from {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")

    def _save_settings(self):
        """Saves the current GUI state to a hardcoded JSON file."""
        try:
            updated_settings = self.settings_service.build_dataclass_from_ui(self.widget_map)
            self.settings_service.save_to_json(updated_settings)
            self.settings_obj = updated_settings
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")