import sys
import os

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from tkinter_app.main_window import MainWindow

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main() 