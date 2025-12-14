
import sys
import asyncio
import pytest
from PyQt6.QtCore import QCoreApplication, QTimer
from unittest.mock import MagicMock, patch

from src.core.queue_manager import QueueManager

# Mock downloader to avoid real network calls
class MockDownloader:
    async def download(self, url, out_dir=None, progress_callback=None, ytdlp_opts=None):
        if progress_callback:
            progress_callback({"status": "downloading", "downloaded_bytes": 50, "total_bytes": 100})
        await asyncio.sleep(0.1)
        if progress_callback:
            progress_callback({"status": "finished", "downloaded_bytes": 100, "total_bytes": 100})

@pytest.fixture
def app():
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication(sys.argv)
    return app

def test_queue_manager_flow(app):
    """Test that QueueManager processes a task and emits signals."""
    
    with patch("src.core.queue_manager.YTDLPDownloader", side_effect=MockDownloader):
        qm = QueueManager(concurrency=1)
        
        # Track signals
        signals_received = {
            "added": False,
            "progress": False,
            "completed": False
        }
        
        def on_added(tid, url):
            signals_received["added"] = True
            
        def on_progress(tid, status, percent, data):
            if percent > 0:
                signals_received["progress"] = True
                
        def on_completed(tid):
            signals_received["completed"] = True
            app.quit() # Stop the event loop

        def on_error(tid, msg):
            print(f"Task Error: {msg}")
            
        qm.task_added.connect(on_added)
        qm.task_updated.connect(on_progress)
        qm.task_completed.connect(on_completed)
        qm.task_error.connect(on_error)
        
        qm.start()
        qm.add_task("http://test.url")
        
        # Timeout safety
        QTimer.singleShot(2000, app.quit)
        
        app.exec()
        
        qm.stop()
        
        assert signals_received["added"], "Task Added signal missing"
        assert signals_received["progress"], "Task Progress signal missing"
        assert signals_received["completed"], "Task Completed signal missing"
