import builtins

import pytest


def test_extract_info_calls_yt_dlp(monkeypatch):
    called = {}

    class DummyYDL:
        def __init__(self, opts=None):
            called['opts'] = opts

        def extract_info(self, url, download=False):
            called['url'] = url
            called['download'] = download
            return {'title': 'dummy'}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr('yt_dlp.YoutubeDL', DummyYDL)

    from core.downloader import YTDLPDownloader

    d = YTDLPDownloader()
    info = d._extract_info('https://youtube.com/watch?v=abc')
    assert info['title'] == 'dummy'
    assert called['url'].endswith('abc')
