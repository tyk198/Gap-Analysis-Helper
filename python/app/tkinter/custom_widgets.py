import os
import tkinter as tk
from tkinter import ttk, filedialog

class PathSelectorWidget(tk.Frame):
    """A widget with an entry and a button to select a file or folder."""
    def __init__(self, parent, selection_mode: str = 'file', icon_only: bool = False):
        super().__init__(parent)
        self.selection_mode = selection_mode

        self.entry = tk.Entry(self)
        self.button = tk.Button(self, text="...", command=self.open_dialog)

        if not icon_only:
            self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.button.pack(side=tk.LEFT)

    def open_dialog(self):
        if self.selection_mode == 'folder':
            path = filedialog.askdirectory(initialdir=self.entry.get())
        else:  # 'file'
            path = filedialog.askopenfilename(initialdir=self.entry.get())
        
        if path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)

    def get(self) -> str:
        return self.entry.get()

    def set(self, text: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

class FoilsSelectorWidget(tk.Frame):
    """A tree-based widget to select folders and subfolders."""
    def __init__(self, parent):
        super().__init__(parent)
        self._data_path = ""
        self._is_populating = False

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def set_data_path(self, path: str, selections: dict):
        self._data_path = path
        self.populate_tree(selections)

    def populate_tree(self, selections: dict):
        self._is_populating = True
        self.tree.delete(*self.tree.get_children())
        if not self._data_path or not os.path.isdir(self._data_path):
            self._is_populating = False
            return

        for folder_name in sorted(os.listdir(self._data_path)):
            folder_path = os.path.join(self._data_path, folder_name)
            if os.path.isdir(folder_path):
                parent_item = self.tree.insert("", tk.END, text=folder_name, open=True)

                selected_subfolders = selections.get(folder_name, [])
                
                subfolders = [d for d in sorted(os.listdir(folder_path)) if os.path.isdir(os.path.join(folder_path, d))]
                
                for subfolder_name in subfolders:
                    self.tree.insert(parent_item, tk.END, text=subfolder_name, tags=("check",))

        self._is_populating = False

    def get_selected_as_dict(self) -> dict:
        selections = {}
        for parent_item in self.tree.get_children():
            parent_name = self.tree.item(parent_item, "text")
            selected_subfolders = []
            for child_item in self.tree.get_children(parent_item):
                # This is a simplified version. Tkinter Treeview doesn't have built-in checkboxes.
                # A more complex implementation would be needed to handle checkboxes.
                pass
            if selected_subfolders:
                selections[parent_name] = selected_subfolders
        return selections

class CollapsibleSection(tk.Frame):
    """A custom collapsible widget with a header and content area."""
    def __init__(self, parent, title: str = "", color: str = "transparent"):
        super().__init__(parent, borderwidth=1, relief="solid")

        self.header = tk.Frame(self, bg="#D0D0D0")
        self.header.pack(fill=tk.X)

        self.toggle_button = tk.Label(self.header, text="▼", bg="#D0D0D0")
        self.toggle_button.pack(side=tk.LEFT)

        self.title_label = tk.Label(self.header, text=title, font=("TkDefaultFont", 10, "bold"), bg="#D0D0D0")
        self.title_label.pack(side=tk.LEFT)

        self.content_area = tk.Frame(self)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        self.header.bind("<Button-1>", self._toggle_collapsed)
        self.toggle_button.bind("<Button-1>", self._toggle_collapsed)
        self.title_label.bind("<Button-1>", self._toggle_collapsed)
        self.is_collapsed = False

    def _toggle_collapsed(self, event):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.content_area.pack_forget()
            self.toggle_button.config(text="▶")
        else:
            self.content_area.pack(fill=tk.BOTH, expand=True)
            self.toggle_button.config(text="▼")

    def contentLayout(self) -> tk.Frame:
        return self.content_area
