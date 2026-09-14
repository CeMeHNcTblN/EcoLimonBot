"""Простое JSON-хранилище пользовательских камер.

Формат cameras.json:
{
    "<chat_id>": {
        "cam_name": "url",
        ...
    },
    ...
}
"""
import json
import os
import logging
from typing import Dict

from config import CAMERAS_FILE

log = logging.getLogger(__name__)


def _load() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(CAMERAS_FILE):
        return {}
    try:
        with open(CAMERAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Не удалось прочитать %s: %s", CAMERAS_FILE, e)
        return {}


def _save(data: Dict[str, Dict[str, str]]) -> None:
    with open(CAMERAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_cameras(chat_id: int) -> Dict[str, str]:
    """Возвращает словарь {name: url} для конкретного чата."""
    return _load().get(str(chat_id), {})


def add_camera(chat_id: int, name: str, url: str) -> None:
    data = _load()
    data.setdefault(str(chat_id), {})[name] = url
    _save(data)


def remove_camera(chat_id: int, name: str) -> bool:
    data = _load()
    cams = data.get(str(chat_id), {})
    if name not in cams:
        return False
    del cams[name]
    _save(data)
    return True
