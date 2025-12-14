"""Placeholders for a progress widget to show per-download progress."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar


class ProgressWidget(QWidget):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.progress = QProgressBar()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.progress)

    def set_progress(self, percent: int) -> None:
        self.progress.setValue(percent)
