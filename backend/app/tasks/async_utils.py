"""Async utility helper for Celery sync task runners."""
from __future__ import annotations

import asyncio
import threading
from typing import Coroutine, TypeVar

T = TypeVar('T')

_local = threading.local()

def run_async(coro: Coroutine[None, None, T]) -> T:
    """Run an async coroutine inside a thread-persistent event loop.
    
    This keeps the loop open, preserving SQLAlchemy's connection pool
    and preventing event loop closed errors.
    """
    if not hasattr(_local, "loop") or _local.loop.is_closed():
        _local.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_local.loop)
    return _local.loop.run_until_complete(coro)
