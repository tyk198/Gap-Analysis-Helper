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

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.widget_map = self.ui_builder.build_ui(self.settings, self.scrollable_frame)
        self._convert_state_fields_to_dropdowns()  # Convert before/after state fields to dropdowns
        self._connect_dependent_widgets()

        s = ttk.Style()
        s.configure('Dark.TLabelframe.Label', background='#D0D0D0')
        
        # Find the Dakar Settings frame to add the Save button
        for child in self.scrollable_frame.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Dakar Settings":
                self.save_button = tk.Button(child, text="Save Settings", command=self.save_settings)
                self.save_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=5)

        self.functions_frame = ttk.LabelFrame(self.scrollable_frame, text="Dakar Functions", style='Dark.TLabelframe')
        self.functions_frame.pack(fill=tk.X, padx=10, pady=10)

        self.selected_function = tk.StringVar()
        
        functions = [
            "combine_csv",
            "crop_FM_classify_top_bottom_from_excel",
            "crop_FM_check_background_fm",
            "plot_compare_FM_summary",
            "plot_FM_summary"
        ]
        
        radio_button_frame = tk.Frame(self.functions_frame)
        radio_button_frame.pack(side=tk.LEFT, anchor=tk.NW, padx=10)

        for func in functions:
            rb = ttk.Radiobutton(radio_button_frame, text=func, value=func, variable=self.selected_function)
            rb.pack(anchor=tk.W)

        self.run_button = tk.Button(self.functions_frame, text="Run Function", command=self.run_dakar_function)
        self.run_button.pack(side=tk.RIGHT, padx=5, pady=5, anchor=tk.SE)

    def _convert_state_fields_to_dropdowns(self):
        """Replace existing before/after state fields with dropdowns using the same geometry manager."""
        for key in ["MasterSettings.Dakar.before_state", "MasterSettings.Dakar.after_state"]:
            if key in self.widget_map:
                original_widget = self.widget_map[key]
                manager = original_widget.winfo_manager()
                if manager == "grid":
                    geom_info = original_widget.grid_info()
                elif manager == "pack":
                    geom_info = original_widget.pack_info()
                else:
                    geom_info = {}
                parent = original_widget.master
                # Destroy original widget
                original_widget.destroy()
                # Create new dropdown (ttk.Combobox)
                combo = ttk.Combobox(parent, state="readonly")
                # Use same geometry manager
                if manager == "grid":
                    combo.grid(**geom_info)
                elif manager == "pack":
                    combo.pack(**geom_info)
                self.widget_map[key] = combo
        # Update dropdown options and set initial values
        self.update_state_dropdowns()

    def update_state_dropdowns(self):
        """Update dropdown values based on foil selections and set initial values from settings."""
        foils_selector = self.widget_map.get("MasterSettings.Dakar.foils_to_plot")
        if foils_selector:
            selections = foils_selector.get_selected_as_dict()
            # Only include states with at least one checked subfolder
            available_states = [state for state, subfolders in selections.items() if subfolders]
            # Map keys to settings values
            key_to_setting = {
                "MasterSettings.Dakar.before_state": self.settings.Dakar.before_state,
                "MasterSettings.Dakar.after_state": self.settings.Dakar.after_state
            }
            for key in ["MasterSettings.Dakar.before_state", "MasterSettings.Dakar.after_state"]:
                if key in self.widget_map:
                    current_value = key_to_setting.get(key, "")
                    self.widget_map[key]['values'] = available_states
                    # Set the dropdown to the loaded setting value if valid, otherwise clear
                    if current_value in available_states:
                        self.widget_map[key].set(current_value)
                    else:
                        self.widget_map[key].set("")
        else:
            # If no foils_selector, clear dropdowns
            for key in ["MasterSettings.Dakar.before_state", "MasterSettings.Dakar.after_state"]:
                if key in self.widget_map:
                    self.widget_map[key]['values'] = []
                    self.widget_map[key].set("")

    def run_dakar_function(self):
        selected_function_name = self.selected_function.get()
        if not selected_function_name:
            print("No function selected.")
            return

        # Save current settings from UI before running the function
        self.save_settings()
        self.settings = self.settings_service.load_from_json("python/tkinter_app/settings.json")
        self.dakar = Dakar(self.settings)

        if hasattr(self.dakar, selected_function_name):
            method_to_call = getattr(self.dakar, selected_function_name)
            print(f"Running {selected_function_name}...")
            try:
                if selected_function_name == "plot_compare_FM_summary":
                    before_state = self.widget_map["MasterSettings.Dakar.before_state"].get()
                    after_state = self.widget_map["MasterSettings.Dakar.after_state"].get()
                    if not before_state or not after_state:
                        print("Please select both before and after states.")
                        return
                    # Call without passing arguments since method uses settings directly
                    method_to_call()
                else:
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
            foils_selector.on_selection_change = self.update_state_dropdowns
            foils_selector.set_data_path(initial_path, initial_selections)

            data_path_widget.command = lambda path: foils_selector.set_data_path(path, {})

    def save_settings(self):
        updated_settings = self.settings_service.build_dataclass_from_ui(self.widget_map)
        self.settings_service.save_to_json(updated_settings)
        print("Settings saved successfully.")

    def load_settings(self):
        self.settings = self.settings_service.load_from_json("python/tkinter_app/settings.json")
        # Rebuild the UI with the new settings
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.widget_map = self.ui_builder.build_ui(self.settings, self.scrollable_frame)
        self._connect_dependent_widgets()
        print("Settings loaded successfully.")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()