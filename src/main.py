"""Entry point for VidFetch - launches the PyQt6 GUI."""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# Add src to path so relative imports work
SRC = Path(__file__).parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gui.main_window import MainWindow
from utils.database import init_db


def main() -> None:
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
