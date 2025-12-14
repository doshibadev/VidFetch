"""Configuration helpers for VidFetch (JSON-based)."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import appdirs


@dataclass
class Settings:
    download_dir: str
    parallel_downloads: int = 2
    default_quality: str = "1080p"
    minimize_to_tray: bool = False


def config_path() -> Path:
    d = Path(appdirs.user_config_dir("vidfetch", "vidfetch"))
    d.mkdir(parents=True, exist_ok=True)
    return d / "settings.json"


def load_settings() -> Settings:
    path = config_path()
    if not path.exists():
        s = Settings(download_dir=str(Path.cwd() / "downloads"))
        save_settings(s)
        return s
    data = json.loads(path.read_text(encoding="utf-8"))
    return Settings(**data)


def save_settings(s: Settings) -> None:
    path = config_path()
    path.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")
