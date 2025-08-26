import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, 
    QTreeWidget, QTreeWidgetItem
)

class PathSelectorWidget(QWidget):
    """A widget with a line edit and a button to select a file or folder."""
    def __init__(self, selection_mode: str = 'file', parent: QWidget = None):
        super().__init__(parent)
        self.selection_mode = selection_mode

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = QLineEdit()
        self.button = QPushButton("...")
        self.button.setFixedWidth(30)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.open_dialog)

    def open_dialog(self):
        """Opens a file or folder dialog and sets the line edit's text."""
        if self.selection_mode == 'folder':
            path = QFileDialog.getExistingDirectory(self, "Select Folder", self.line_edit.text())
        else:  # 'file'
            path, _ = QFileDialog.getOpenFileName(self, "Select File", self.line_edit.text())
        
        if path:
            self.line_edit.setText(path)

    def text(self) -> str:
        """Gets the text from the line edit."""
        return self.line_edit.text()

    def setText(self, text: str):
        """Sets the text of the line edit."""
        self.line_edit.setText(text)


class FoilsSelectorWidget(QWidget):
    """A tree-based widget to select folders and subfolders."""
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._data_path = ""
        self._is_populating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Folders"])
        self.tree.itemChanged.connect(self._handle_item_changed)
        layout.addWidget(self.tree)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.repopulate_tree)
        layout.addWidget(self.refresh_button)

    def set_data_path(self, path: str, selections: dict):
        """Sets the root path for folders and populates the tree."""
        self._data_path = path
        self.populate_tree(selections)

    def repopulate_tree(self):
        """Repopulates the tree using the current path and selections."""
        current_selections = self.get_selected_as_dict()
        self.populate_tree(current_selections)

    def populate_tree(self, selections: dict):
        """Populates the tree from the data path and applies selections."""
        self._is_populating = True
        self.tree.clear()
        if not self._data_path or not os.path.isdir(self._data_path):
            self._is_populating = False
            return

        for folder_name in sorted(os.listdir(self._data_path)):
            folder_path = os.path.join(self._data_path, folder_name)
            if os.path.isdir(folder_path):
                parent_item = QTreeWidgetItem(self.tree, [folder_name])
                parent_item.setFlags(parent_item.flags() | Qt.ItemIsUserCheckable)
                parent_item.setCheckState(0, Qt.Unchecked)

                selected_subfolders = selections.get(folder_name, [])
                has_selected_child = False
                all_children_selected = True

                for subfolder_name in sorted(os.listdir(folder_path)):
                    subfolder_path = os.path.join(folder_path, subfolder_name)
                    if os.path.isdir(subfolder_path):
                        child_item = QTreeWidgetItem(parent_item, [subfolder_name])
                        child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                        if subfolder_name in selected_subfolders:
                            child_item.setCheckState(0, Qt.Checked)
                            has_selected_child = True
                        else:
                            child_item.setCheckState(0, Qt.Unchecked)
                            all_children_selected = False
                
                if has_selected_child:
                    if all_children_selected and parent_item.childCount() > 0:
                        parent_item.setCheckState(0, Qt.Checked)
                    else:
                        parent_item.setCheckState(0, Qt.PartiallyChecked)

        self._is_populating = False

    def get_selected_as_dict(self) -> dict:
        """Returns the selected items as a dictionary."""
        selections = {}
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            parent_item = root.child(i)
            if parent_item.checkState(0) != Qt.Unchecked:
                selected_subfolders = []
                for j in range(parent_item.childCount()):
                    child_item = parent_item.child(j)
                    if child_item.checkState(0) == Qt.Checked:
                        selected_subfolders.append(child_item.text(0))
                if selected_subfolders:
                    selections[parent_item.text(0)] = selected_subfolders
        return selections

    def _handle_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handles check state changes for parent/child items."""
        if self._is_populating or column != 0:
            return

        # Update children if parent is checked/unchecked
        if item.childCount() > 0:
            self._is_populating = True
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, item.checkState(0))
            self._is_populating = False

        # Update parent if child is checked/unchecked
        parent = item.parent()
        if parent:
            self._is_populating = True
            checked_count = 0
            for i in range(parent.childCount()):
                if parent.child(i).checkState(0) == Qt.Checked:
                    checked_count += 1
            
            if checked_count == 0:
                parent.setCheckState(0, Qt.Unchecked)
            elif checked_count == parent.childCount():
                parent.setCheckState(0, Qt.Checked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)
            self._is_populating = False