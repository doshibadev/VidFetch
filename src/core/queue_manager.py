"""Async queue manager with PyQt6 integration."""
import asyncio
import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from .downloader import YTDLPDownloader
from utils.database import add_download, update_download_status


@dataclass
class DownloadTask:
    url: str
    options: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "queued"
    progress: int = 0
    db_id: Optional[int] = None
    cancelled: bool = False


class AsyncWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self, queue_manager):
        super().__init__()
        self._qm = queue_manager
        self._loop = None

    def run(self):
        """Entry point for the QThread."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._qm._process_queue())
        except Exception as e:
            logging.error(f"Worker loop error: {e}")
        finally:
            if self._loop:
                self._loop.close()
            self.finished.emit()

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)


class QueueManager(QObject):
    """Manages download queue and communicates via Signals."""

    # Signals
    task_added = pyqtSignal(str, str)  # task_id, url
    task_updated = pyqtSignal(str, str, int, dict)  # task_id, status, percent, extra_data
    task_completed = pyqtSignal(str)  # task_id
    task_error = pyqtSignal(str, str)  # task_id, error_message

    def __init__(self, concurrency: int = 2) -> None:
        super().__init__()
        self.concurrency = concurrency
        self._queue: Optional[asyncio.Queue] = None
        self._active_tasks: Dict[str, DownloadTask] = {}
        self._pending_tasks: list[DownloadTask] = []
        
        # State
        self._paused = asyncio.Event()
        self._paused.set()  # Set means "Running" (not paused)
        
        # Thread management
        self._thread = QThread()
        self._worker = AsyncWorker(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._stop_event = asyncio.Event()

    def start(self) -> None:
        """Start the background worker thread."""
        if not self._thread.isRunning():
            self._thread.start()
            
    def pause(self) -> None:
        """Pause processing of NEW tasks."""
        if self._worker._loop:
            self._worker._loop.call_soon_threadsafe(self._paused.clear)

    def resume(self) -> None:
        """Resume processing of tasks."""
        if self._worker._loop:
            self._worker._loop.call_soon_threadsafe(self._paused.set)

    def stop(self) -> None:
        """Stop the background worker."""
        if self._thread.isRunning():
            self._worker.stop()
            self._thread.quit()
            self._thread.wait()

    def add_task(self, url: str, options: Dict[str, Any] = None) -> str:
        """Add a task to the queue. Thread-safe."""
        if options is None:
            options = {}
            
        task = DownloadTask(url=url, options=options)
        self._active_tasks[task.id] = task
        
        if self._worker._loop and self._worker._loop.is_running() and self._queue:
             self._worker._loop.call_soon_threadsafe(
                 self._queue.put_nowait, task
             )
        else:
             self._pending_tasks.append(task)

        self.task_added.emit(task.id, task.url)
        return task.id

    def cancel_task(self, task_id: str) -> None:
        """Mark a task as cancelled."""
        if task_id in self._active_tasks:
            self._active_tasks[task_id].cancelled = True
            # If it's still in the queue (not started), we can't easily remove it from asyncio.Queue
            # But the consumer checks the flag.

    async def _process_queue(self):
        """Main async loop running in the worker thread."""
        self._queue = asyncio.Queue()
        
        # Drain pending
        for t in self._pending_tasks:
            self._queue.put_nowait(t)
        self._pending_tasks.clear()
        
        self._stop_event.clear()
        self._paused.set()
        
        # Start consumers
        consumers = [asyncio.create_task(self._consumer(i)) for i in range(self.concurrency)]
        
        # Keep the loop alive until stop is called
        while not self._stop_event.is_set():
             await asyncio.sleep(0.1)

        for c in consumers:
            c.cancel()
        
    async def _consumer(self, worker_id: int):
        downloader = YTDLPDownloader()
        
        while True:
            # Wait if paused
            await self._paused.wait()
            
            task: DownloadTask = await self._queue.get()
            
            # Check cancellation before starting
            if task.cancelled:
                if task.db_id:
                     update_download_status(task.db_id, "cancelled")
                self.task_error.emit(task.id, "Cancelled by user")
                self._queue.task_done()
                continue

            try:
                # Log to DB
                task.db_id = add_download(task.url, task.url, "downloading")
                
                self.task_updated.emit(task.id, "downloading", 0, {})
                
                def progress_cb(status: dict):
                    if task.cancelled:
                        raise Exception("Cancelled by user")
                    # Bridge async callback to Qt Signal
                    self._on_progress(task.id, status)

                # Execute download
                out_dir = task.options.get("out_dir", ".")
                # Merge user options with defaults
                ytdlp_opts = task.options.get("ytdlp_opts", {})
                
                await downloader.download(
                    task.url, 
                    out_dir=out_dir,
                    progress_callback=progress_cb,
                    ytdlp_opts=ytdlp_opts
                )
                
                update_download_status(task.db_id, "completed")
                self.task_completed.emit(task.id)
                
            except Exception as e:
                status_str = "cancelled" if "Cancelled" in str(e) else "error"
                if task.db_id:
                    update_download_status(task.db_id, status_str)
                self.task_error.emit(task.id, str(e))
            finally:
                self._queue.task_done()

    def _on_progress(self, task_id: str, status: dict):
        """Callback from downloader, mapped to Signal."""
        # Calculate percentage
        downloaded = status.get("downloaded_bytes", 0)
        total = status.get("total_bytes", 1) or 1
        percent = int(100 * downloaded / total)
        
        s_str = status.get("status", "downloading")
        
        self.task_updated.emit(task_id, s_str, percent, status)

    def update_concurrency(self, n: int):
        self.concurrency = n
        # Logic to resize workers would go here