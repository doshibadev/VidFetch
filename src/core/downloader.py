"""Downloader core using yt-dlp with a simple async wrapper."""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, Optional

import yt_dlp


ProgressCallback = Callable[[Dict[str, Any]], None]


class YTDLPDownloader:
    """Thin async wrapper around yt-dlp's Python API."""

    def __init__(self, ydl_opts: Optional[Dict[str, Any]] = None) -> None:
        self.ydl_opts = ydl_opts or {}

    def _make_opts(self, out_dir: Optional[str] = None, progress_callback: Optional[ProgressCallback] = None) -> Dict[str, Any]:
        opts = dict(self.ydl_opts)
        if out_dir:
            opts.setdefault("outtmpl", f"{out_dir}/%(title)s.%(ext)s")

        if progress_callback is not None:
            def _hook(d: Dict[str, Any]) -> None:
                try:
                    progress_callback(d)
                except Exception:
                    # Do not allow hook exceptions to break downloads
                    pass

            opts["progress_hooks"] = [_hook]

        return opts

    def _extract_info(self, url: str) -> Dict[str, Any]:
        with yt_dlp.YoutubeDL({"skip_download": True}) as ydl:
            return ydl.extract_info(url, download=False)

    async def extract_info(self, url: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self._extract_info, url)

    def _download(self, url: str, out_dir: Optional[str], progress_callback: Optional[ProgressCallback], ytdlp_opts: Optional[Dict[str, Any]]) -> None:
        opts = self._make_opts(out_dir=out_dir, progress_callback=progress_callback)
        if ytdlp_opts:
            opts.update(ytdlp_opts)
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    async def download(self, url: str, out_dir: Optional[str] = None, progress_callback: Optional[ProgressCallback] = None, ytdlp_opts: Optional[Dict[str, Any]] = None) -> None:
        await asyncio.to_thread(self._download, url, out_dir, progress_callback, ytdlp_opts)
