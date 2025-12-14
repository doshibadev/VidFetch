"""Widget for displaying download history."""
from typing import List, Dict, Any

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QLineEdit
)

from utils.database import get_history


class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_data = []  # Cache data for filtering
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")
        self.search_input.textChanged.connect(self._on_search_changed)
        toolbar.addWidget(self.search_input)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Status", "URL", "Title"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        """Reload history from database."""
        self._history_data = get_history(limit=100)
        self._update_table(self._history_data)

    def _on_search_changed(self, text: str) -> None:
        """Filter the displayed history."""
        text = text.lower()
        if not text:
            self._update_table(self._history_data)
            return

        filtered = [
            row for row in self._history_data
            if text in row["title"].lower() or text in row["url"].lower()
        ]
        self._update_table(filtered)

    def _update_table(self, data: List[Dict[str, Any]]) -> None:
        self.table.setRowCount(len(data))
        self.table.setSortingEnabled(False) # Disable sorting while updating

        for row_idx, item in enumerate(data):
            date_str = str(item["created_at"])
            status = item["status"] or "Unknown"
            url = item["url"]
            title = item["title"] or ""

            self.table.setItem(row_idx, 0, QTableWidgetItem(date_str))
            self.table.setItem(row_idx, 1, QTableWidgetItem(status))
            self.table.setItem(row_idx, 2, QTableWidgetItem(url))
            self.table.setItem(row_idx, 3, QTableWidgetItem(title))

        self.table.setSortingEnabled(True)
