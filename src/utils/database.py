"""Simple sqlite3-based history storage."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

from .config import config_path


def db_path() -> Path:
    p = config_path().with_name("vidfetch.db")
    return p


def init_db() -> None:
    p = db_path()
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_download(url: str, title: str, status: str) -> int:
    """Add a new download record."""
    conn = sqlite3.connect(db_path())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO downloads (url, title, status) VALUES (?, ?, ?)",
        (url, title, status)
    )
    d_id = cur.lastrowid
    conn.commit()
    conn.close()
    return d_id if d_id else -1


def update_download_status(download_id: int, status: str) -> None:
    """Update status of a download."""
    conn = sqlite3.connect(db_path())
    cur = conn.cursor()
    cur.execute(
        "UPDATE downloads SET status = ? WHERE id = ?",
        (status, download_id)
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent download history."""
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM downloads ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]