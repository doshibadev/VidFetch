"""Main window with queue management, progress tracking, and settings."""
import asyncio
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QDialog,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QGroupBox,
    QSystemTrayIcon,
    QMenu,
    QStyle,
)
from PyQt6.QtGui import QAction, QIcon

from core.queue_manager import QueueManager
from gui.history_widget import HistoryWidget
from utils.config import load_settings, save_settings


class DownloadItemWidget(QWidget):
    """Compact row showing one download's progress."""

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.status = "queued"
        self.percent = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Show title or URL
        self.title_label = QLabel(self._truncate(url, 50))
        layout.addWidget(self.title_label, stretch=1)

        # Status badge
        self.status_label = QLabel("Queued")
        self.status_label.setMaximumWidth(120)  # Increased for error msgs
        layout.addWidget(self.status_label)

        # Percent
        self.percent_label = QLabel("0%")
        self.percent_label.setMaximumWidth(40)
        layout.addWidget(self.percent_label)

    def set_status(self, status: str, percent: int = 0) -> None:
        self.status = status
        self.percent = percent
        self.status_label.setText(status)
        self.percent_label.setText(f"{percent}%")

    @staticmethod
    def _truncate(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 3] + "..."


class SettingsDialog(QDialog):
    """Settings dialog for VidFetch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - VidFetch")
        self.resize(500, 300)

        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Download Directory:"))
        self.dir_input = QLineEdit(self.settings.download_dir)
        dir_layout.addWidget(self.dir_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        # Parallel downloads
        par_layout = QHBoxLayout()
        par_layout.addWidget(QLabel("Parallel Downloads:"))
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setMinimum(1)
        self.parallel_spin.setMaximum(10)
        self.parallel_spin.setValue(self.settings.parallel_downloads)
        par_layout.addWidget(self.parallel_spin)
        par_layout.addStretch()
        layout.addLayout(par_layout)

        # Default quality
        qual_layout = QHBoxLayout()
        qual_layout.addWidget(QLabel("Default Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["4K", "1080p", "720p", "480p", "360p"])
        idx = self.quality_combo.findText(self.settings.default_quality)
        if idx >= 0:
            self.quality_combo.setCurrentIndex(idx)
        qual_layout.addWidget(self.quality_combo)
        qual_layout.addStretch()
        layout.addLayout(qual_layout)

        # Minimize to tray
        self.tray_chk = QCheckBox("Minimize to Tray on Close")
        self.tray_chk.setChecked(self.settings.minimize_to_tray)
        layout.addWidget(self.tray_chk)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _on_browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if d:
            self.dir_input.setText(d)

    def _on_save(self) -> None:
        self.settings.download_dir = self.dir_input.text()
        self.settings.parallel_downloads = self.parallel_spin.value()
        self.settings.default_quality = self.quality_combo.currentText()
        self.settings.minimize_to_tray = self.tray_chk.isChecked()
        save_settings(self.settings)
        self.accept()


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VidFetch - YouTube Media Downloader")
        self.resize(900, 600)

        self.settings = load_settings()
        # Map Task ID -> Widget
        self._downloads: Dict[str, DownloadItemWidget] = {}
        
        # Initialize QueueManager
        self.qm = QueueManager(concurrency=self.settings.parallel_downloads)
        self.qm.task_added.connect(self._on_task_added)
        self.qm.task_updated.connect(self._on_task_updated)
        self.qm.task_completed.connect(self._on_task_completed)
        self.qm.task_error.connect(self._on_task_error)
        
        self.qm.start()

        self._build_ui()
        self._setup_tray()

    def _setup_tray(self):
        """Initialize system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a standard icon as placeholder
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.tray_icon.setIcon(icon)
        
        # Tray Menu
        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self._force_quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def _force_quit(self):
        """Actually quit the application."""
        self.qm.stop()
        self.tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event):
        """Handle window close."""
        if self.settings.minimize_to_tray:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "VidFetch",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.qm.stop()
            super().closeEvent(event)


    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Downloader
        downloader_tab = QWidget()
        self._build_downloader_tab(downloader_tab)
        self.tabs.addTab(downloader_tab, "Downloader")

        # Tab 2: History
        self.history_tab = HistoryWidget()
        self.tabs.addTab(self.history_tab, "History")
        
        # Refresh history when tab is selected
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _build_downloader_tab(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)

        # Input section
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste video URL or playlist link..."
        )
        input_row.addWidget(self.url_input)
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self._on_download_clicked)
        input_row.addWidget(self.download_btn)
        layout.addLayout(input_row)

        # Options Section
        opts_group = QGroupBox("Download Options")
        opts_layout = QHBoxLayout(opts_group)
        
        self.audio_only_chk = QCheckBox("Audio Only (MP3)")
        opts_layout.addWidget(self.audio_only_chk)
        
        self.subs_chk = QCheckBox("Download Subtitles")
        opts_layout.addWidget(self.subs_chk)
        
        self.thumb_chk = QCheckBox("Download Thumbnail")
        opts_layout.addWidget(self.thumb_chk)
        
        opts_layout.addStretch()
        layout.addWidget(opts_group)

        # Batch/paste section
        batch_label = QLabel("Or paste multiple URLs (one per line):")
        layout.addWidget(batch_label)
        self.batch_input = QTextEdit()
        self.batch_input.setMaximumHeight(80)
        self.batch_input.setPlaceholderText("https://youtube.com/watch?v=...")
        layout.addWidget(self.batch_input)

        batch_btn_layout = QHBoxLayout()
        add_batch_btn = QPushButton("Add All to Queue")
        add_batch_btn.clicked.connect(self._on_batch_clicked)
        batch_btn_layout.addWidget(add_batch_btn)
        batch_btn_layout.addStretch()
        layout.addLayout(batch_btn_layout)

        # Downloads list
        layout.addWidget(QLabel("Downloads:"))
        self.download_list = QListWidget()
        self.download_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.download_list)

        # Control buttons
        ctrl_layout = QHBoxLayout()
        self.pause_btn = QPushButton("Pause Queue")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        ctrl_layout.addWidget(self.pause_btn)

        self.resume_btn = QPushButton("Resume Queue")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self._on_resume_clicked)
        ctrl_layout.addWidget(self.resume_btn)

        self.cancel_btn = QPushButton("Cancel Selected")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        ctrl_layout.addWidget(self.cancel_btn)

        ctrl_layout.addStretch()

        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self._on_settings)
        ctrl_layout.addWidget(settings_btn)

        layout.addLayout(ctrl_layout)

    def _on_tab_changed(self, index: int) -> None:
        if index == 1:  # History tab
            self.history_tab.refresh()

    def _on_selection_changed(self) -> None:
        has_selection = len(self.download_list.selectedItems()) > 0
        self.cancel_btn.setEnabled(has_selection)
        
    def _on_pause_clicked(self) -> None:
        self.qm.pause()
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(True)
        self.pause_btn.setText("Paused")
        
    def _on_resume_clicked(self) -> None:
        self.qm.resume()
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)
        self.pause_btn.setText("Pause Queue")

    def _on_cancel_clicked(self) -> None:
        items = self.download_list.selectedItems()
        if not items:
            return
        
        for item in items:
            task_id = item.data(Qt.ItemDataRole.UserRole)
            if task_id:
                self.qm.cancel_task(task_id)

    def _on_download_clicked(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            return

        self._add_download(url)
        self.url_input.clear()

    def _on_batch_clicked(self) -> None:
        batch_text = self.batch_input.toPlainText().strip()
        if not batch_text:
            return

        urls = [u.strip() for u in batch_text.split("\n") if u.strip()]
        for url in urls:
            self._add_download(url)

        self.batch_input.clear()

    def _add_download(self, url: str) -> None:
        # Build yt-dlp options based on UI
        ytdlp_opts = {}
        
        if self.audio_only_chk.isChecked():
            ytdlp_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # Video quality logic could go here
            pass
            
        if self.subs_chk.isChecked():
            ytdlp_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'all'], # Default to English/Auto
            })
            
        if self.thumb_chk.isChecked():
            ytdlp_opts['writethumbnail'] = True

        # Pass settings to the task
        opts = {
            "out_dir": self.settings.download_dir,
            "quality": self.settings.default_quality,
            "ytdlp_opts": ytdlp_opts
        }
        self.qm.add_task(url, opts)

    # --- Signal Handlers ---

    def _on_task_added(self, task_id: str, url: str) -> None:
        widget = DownloadItemWidget(url, self)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, task_id)
        self.download_list.addItem(item)
        self.download_list.setItemWidget(item, widget)

        self._downloads[task_id] = widget

    def _on_task_updated(self, task_id: str, status: str, percent: int, data: dict) -> None:
        if task_id in self._downloads:
            self._downloads[task_id].set_status(status, percent)

    def _on_task_completed(self, task_id: str) -> None:
        if task_id in self._downloads:
            self._downloads[task_id].set_status("Completed", 100)

    def _on_task_error(self, task_id: str, msg: str) -> None:
        if task_id in self._downloads:
            # Truncate error message if too long
            short_msg = (msg[:25] + '..') if len(msg) > 25 else msg
            self._downloads[task_id].set_status(f"Error: {short_msg}", 0)
            self._downloads[task_id].setToolTip(msg)

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = load_settings()
            # Update concurrency on the fly
            self.qm.update_concurrency(self.settings.parallel_downloads)
