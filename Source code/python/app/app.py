import sys
from PySide6.QtWidgets import QApplication

from settings import MasterSettings
from main_window import MainWindow

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Create the initial settings object from the defaults in settings.py
    initial_settings = MasterSettings()

    # Create and show the main window
    editor = MainWindow(settings=initial_settings)
    editor.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()