import tkinter as tk
from tkinter import ttk

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

        self.settings = self.settings_service.load_from_json("python/app/tkinter/settings.json")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.widget_map = self.ui_builder.build_ui(self.settings, self.main_frame)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.load_button = tk.Button(self.button_frame, text="Load Settings", command=self.load_settings)
        self.load_button.pack(side=tk.RIGHT)

    def save_settings(self):
        updated_settings = self.settings_service.build_dataclass_from_ui(self.widget_map)
        self.settings_service.save_to_json(updated_settings)
        print("Settings saved successfully.")

    def load_settings(self):
        self.settings = self.settings_service.load_from_json("python/app/tkinter/settings.json")
        # Rebuild the UI with the new settings
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.widget_map = self.ui_builder.build_ui(self.settings, self.main_frame)
        print("Settings loaded successfully.")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
