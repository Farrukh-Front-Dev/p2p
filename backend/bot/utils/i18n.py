"""Ko'p tillilik (i18n) yuklash va olish."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

DEFAULT_LANG = "uz"
SUPPORTED_LANGS = ("uz", "ru", "en")

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"


@cache
def _load_locale(lang: str) -> dict[str, str]:
    path = _LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = _LOCALES_DIR / f"{DEFAULT_LANG}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Tarjima qaytaradi. Topilmasa default tilga, keyin kalitning o'ziga qaytadi."""
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    locale = _load_locale(lang)
    text = locale.get(key)
    if text is None:
        text = _load_locale(DEFAULT_LANG).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def get_translator(lang: str):
    """Berilgan til uchun tarjima funksiyasini qaytaradi."""

    def _translator(key: str, **kwargs) -> str:
        return t(key, lang, **kwargs)

    return _translator
