import os
import tkinter as tk
from tkinter import ttk, filedialog

class PathSelectorWidget(tk.Frame):
    """A widget with an entry and a button to select a file or folder."""
    def __init__(self, parent, selection_mode: str = 'file', icon_only: bool = False, command=None):
        super().__init__(parent)
        self.selection_mode = selection_mode
        self.command = command

        self.path_var = tk.StringVar()
        self.path_var.trace_add("write", self._on_path_change)

        self.entry = tk.Entry(self, textvariable=self.path_var)
        self.button = tk.Button(self, text="...", command=self.open_dialog)

        if not icon_only:
            self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.button.pack(side=tk.LEFT)

    def open_dialog(self):
        if self.selection_mode == 'folder':
            path = filedialog.askdirectory(initialdir=self.get())
        else:  # 'file'
            path = filedialog.askopenfilename(initialdir=self.get())
        
        if path:
            self.set(path)

    def get(self) -> str:
        return self.path_var.get()

    def set(self, text: str):
        self.path_var.set(text)

    def _on_path_change(self, *args):
        if self.command:
            self.command(self.get())

class FoilsSelectorWidget(tk.Frame):
    """A tree-based widget to select folders and subfolders."""
    def __init__(self, parent, checked_char="\u2713", unchecked_char=""):
        super().__init__(parent)
        self._data_path = ""
        self._is_populating = False
        self.checked_char = checked_char
        self.unchecked_char = unchecked_char

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            text = self.tree.item(item_id, "text")
            if text.startswith(f"[{self.unchecked_char}] "):
                self.tree.item(item_id, text=f"[{self.checked_char}] " + text[4:])
            elif text.startswith(f"[{self.checked_char}] "):
                self.tree.item(item_id, text=f"[{self.unchecked_char}] " + text[4:])

    def set_data_path(self, path: str, selections: dict):
        self._data_path = path
        self.populate_tree(selections)

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            text = self.tree.item(item_id, "text")
            unchecked_prefix = f"[{self.unchecked_char}] "
            checked_prefix = f"[{self.checked_char}] "
            if text.startswith(unchecked_prefix):
                self.tree.item(item_id, text=checked_prefix + text[len(unchecked_prefix):])
            elif text.startswith(checked_prefix):
                self.tree.item(item_id, text=unchecked_prefix + text[len(checked_prefix):])

    def populate_tree(self, selections: dict):
        self._is_populating = True
        self.tree.delete(*self.tree.get_children())
        if not self._data_path or not os.path.isdir(self._data_path):
            self._is_populating = False
            return

        unchecked_prefix = f"[{self.unchecked_char}] "
        checked_prefix = f"[{self.checked_char}] "

        for folder_name in sorted(os.listdir(self._data_path)):
            folder_path = os.path.join(self._data_path, folder_name)
            if os.path.isdir(folder_path):
                parent_item = self.tree.insert("", tk.END, text=folder_name, open=True)

                selected_subfolders = selections.get(folder_name, [])
                
                subfolders = [d for d in sorted(os.listdir(folder_path)) if os.path.isdir(os.path.join(folder_path, d))]
                
                for subfolder_name in subfolders:
                    if subfolder_name in selected_subfolders:
                        self.tree.insert(parent_item, tk.END, text=checked_prefix + subfolder_name)
                    else:
                        self.tree.insert(parent_item, tk.END, text=unchecked_prefix + subfolder_name)
        
        self._is_populating = False

    def get_selected_as_dict(self) -> dict:
        selections = {}
        for parent_item in self.tree.get_children():
            parent_name = self.tree.item(parent_item, "text")
            selected_subfolders = []
            for child_item in self.tree.get_children(parent_item):
                text = self.tree.item(child_item, "text")
                checked_prefix = f"[{self.checked_char}] "
                if text.startswith(checked_prefix):
                    selected_subfolders.append(text[len(checked_prefix):])
            if selected_subfolders:
                selections[parent_name] = selected_subfolders
        return selections

    def get_selected_as_dict(self) -> dict:
        selections = {}
        for parent_item in self.tree.get_children():
            parent_name = self.tree.item(parent_item, "text")
            selected_subfolders = []
            for child_item in self.tree.get_children(parent_item):
                text = self.tree.item(child_item, "text")
                if text.startswith(f"[{self.checked_char}]"):
                    selected_subfolders.append(text[4:])
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
