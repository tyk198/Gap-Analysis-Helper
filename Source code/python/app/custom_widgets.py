import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QFrame, QLabel
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
        if self.selection_mode == 'folder':
            path = QFileDialog.getExistingDirectory(self, "Select Folder", self.line_edit.text())
        else:  # 'file'
            path, _ = QFileDialog.getOpenFileName(self, "Select File", self.line_edit.text())
        
        if path:
            self.line_edit.setText(path)

    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, text: str):
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
        self.tree.setMinimumHeight(300) # Set a larger minimum height
        layout.addWidget(self.tree)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.repopulate_tree)
        layout.addWidget(self.refresh_button)

    def set_data_path(self, path: str, selections: dict):
        self._data_path = path
        self.populate_tree(selections)

    def repopulate_tree(self):
        current_selections = self.get_selected_as_dict()
        self.populate_tree(current_selections)

    def populate_tree(self, selections: dict):
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

                subfolders = [d for d in sorted(os.listdir(folder_path)) if os.path.isdir(os.path.join(folder_path, d))]
                if not subfolders:
                    all_children_selected = False

                for subfolder_name in subfolders:
                    child_item = QTreeWidgetItem(parent_item, [subfolder_name])
                    child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                    if subfolder_name in selected_subfolders:
                        child_item.setCheckState(0, Qt.Checked)
                        has_selected_child = True
                    else:
                        child_item.setCheckState(0, Qt.Unchecked)
                        all_children_selected = False
                
                if has_selected_child:
                    if all_children_selected:
                        parent_item.setCheckState(0, Qt.Checked)
                    else:
                        parent_item.setCheckState(0, Qt.PartiallyChecked)

        self._is_populating = False

    def get_selected_as_dict(self) -> dict:
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
        if self._is_populating or column != 0:
            return
        
        self._is_populating = True
        if item.childCount() > 0:
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, item.checkState(0))

        parent = item.parent()
        if parent:
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

class CollapsibleSection(QWidget):
    """A custom collapsible widget with a header and content area."""
    def __init__(self, title: str = "", color: str = "transparent", parent: QWidget = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("collapsible_header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(4, 4, 4, 4)

        self.toggle_button = QLabel("▼")
        self.toggle_button.setStyleSheet("color: #505050;") # Lighter color for the triangle
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")

        header_layout.addWidget(self.toggle_button)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.content_area = QWidget()
        self.content_area.setObjectName("collapsible_content")
        self._content_layout = QVBoxLayout(self.content_area)
        self._content_layout.setContentsMargins(10, 5, 10, 10)

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_area)

        self.header.mousePressEvent = self._toggle_collapsed
        self.is_collapsed = False

        self.setStyleSheet(f"""
            #collapsible_content {{
                background-color: {color};
                border: 1px solid #D0D0D0;
                border-top: none;
            }}
            #collapsible_header {{
                border: 1px solid #D0D0D0;
            }}
        """)

    def _toggle_collapsed(self, event):
        self.is_collapsed = not self.is_collapsed
        self.content_area.setVisible(not self.is_collapsed)
        self.toggle_button.setText("▶" if self.is_collapsed else "▼")

    def contentLayout(self) -> QVBoxLayout:
        return self._content_layout
