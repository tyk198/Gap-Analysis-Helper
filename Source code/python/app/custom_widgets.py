from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog

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
