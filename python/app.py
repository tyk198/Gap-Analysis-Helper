import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.settings_service import SettingsService
from app.main_window import MainWindow

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    # Set the application icon
    app.setWindowIcon(QIcon('python/app/icon.ico'))
    
    settings_service = SettingsService()
    initial_settings = settings_service.load_from_json('python/app/settings.json')

    editor = MainWindow(settings=initial_settings)
    editor.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()