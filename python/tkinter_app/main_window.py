import tkinter as tk

from .settings import MasterSettings
from .settings_service import SettingsService
from .ui_builder import SettingsUIBuilder

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gap Analysis Helper")
        self.geometry("800x600")

        self.settings_service = SettingsService()
        self.ui_builder = SettingsUIBuilder()

        self.settings = self.settings_service.load_from_json("python/tkinter_app/settings.json")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.widget_map = self.ui_builder.build_ui(self.settings, self.main_frame)
        self._connect_dependent_widgets()

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.load_button = tk.Button(self.button_frame, text="Load Settings", command=self.load_settings)
        self.load_button.pack(side=tk.RIGHT)

    def _connect_dependent_widgets(self):
        data_path_widget = self.widget_map.get("MasterSettings.Dakar.data")
        foils_selector = self.widget_map.get("MasterSettings.Dakar.foils_to_plot")

        if data_path_widget and foils_selector:
            initial_path = data_path_widget.get()
            initial_selections = self.settings.Dakar.foils_to_plot
            foils_selector.set_data_path(initial_path, initial_selections)

            data_path_widget.command = lambda path: foils_selector.set_data_path(path, {})

    def save_settings(self):
        updated_settings = self.settings_service.build_dataclass_from_ui(self.widget_map)
        self.settings_service.save_to_json(updated_settings)
        print("Settings saved successfully.")

    def load_settings(self):
        self.settings = self.settings_service.load_from_json("python/tkinter_app/settings.json")
        # Rebuild the UI with the new settings
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.widget_map = self.ui_builder.build_ui(self.settings, self.main_frame)
        print("Settings loaded successfully.")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
