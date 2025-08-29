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
        import tkinter as tk
from tkinter import ttk
from Dakar import Dakar

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
        self.dakar = Dakar(self.settings)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.widget_map = self.ui_builder.build_ui(self.settings, self.main_frame)
        self._connect_dependent_widgets()

        self.functions_frame = ttk.LabelFrame(self, text="Dakar Functions")
        self.functions_frame.pack(fill=tk.X, padx=10, pady=10)

        self.selected_function = tk.StringVar()
        
        functions = [
            "combine_csv",
            "crop_FM_classify_top_bottom_from_excel",
            "crop_FM_check_background_fm",
            "plot_compare_FM_summary",
            "plot_FM_summary"
        ]

        for func in functions:
            rb = ttk.Radiobutton(self.functions_frame, text=func, value=func, variable=self.selected_function)
            rb.pack(anchor=tk.W, padx=10)

        self.run_button = tk.Button(self.functions_frame, text="Run Function", command=self.run_dakar_function)
        self.run_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.load_button = tk.Button(self.button_frame, text="Load Settings", command=self.load_settings)
        self.load_button.pack(side=tk.RIGHT)

    def run_dakar_function(self):
        selected_function_name = self.selected_function.get()
        if not selected_function_name:
            print("No function selected.")
            return

        # Save current settings from UI before running function
        self.save_settings()
        # Reload settings to ensure the dakar instance has the latest values
        self.settings = self.settings_service.load_from_json("python/tkinter_app/settings.json")
        self.dakar = Dakar(self.settings)

        if hasattr(self.dakar, selected_function_name):
            method_to_call = getattr(self.dakar, selected_function_name)
            print(f"Running {selected_function_name}...")
            try:
                method_to_call()
                print(f"Successfully finished running {selected_function_name}.")
            except Exception as e:
                print(f"An error occurred while running {selected_function_name}: {e}")
        else:
            print(f"Function {selected_function_name} not found in Dakar class.")

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
        self._connect_dependent_widgets()
        print("Settings loaded successfully.")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
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