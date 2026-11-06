"""Public-demo abuse/cost controls (ARCHITECTURE.md #2.1 / #6).

A session wraps one live-mic or test-scenario run: it enforces a hard
wall-clock cap and gives the server a single kill switch per session.
"""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict

MAX_SESSION_SECONDS = 120
MAX_CONCURRENT_SESSIONS_PER_IP = 2

# ponytail: in-process dict, fine for one demo instance; swap for Redis if this ever runs multi-process.
_sessions_per_ip: dict[str, int] = defaultdict(int)


class SessionLimitExceeded(Exception):
    pass


class KitchenSession:
    def __init__(self, session_id: str, client_ip: str) -> None:
        if _sessions_per_ip[client_ip] >= MAX_CONCURRENT_SESSIONS_PER_IP:
            raise SessionLimitExceeded(f"{client_ip} already has {MAX_CONCURRENT_SESSIONS_PER_IP} active sessions")
        self.session_id = session_id
        self.client_ip = client_ip
        self._started_at = time.monotonic()
        self._killed = False
        _sessions_per_ip[client_ip] += 1

    def seconds_remaining(self) -> float:
        return max(0.0, MAX_SESSION_SECONDS - (time.monotonic() - self._started_at))

    def expired(self) -> bool:
        return self._killed or self.seconds_remaining() <= 0

    def kill(self) -> None:
        """Single entry point to tear down a session — ARCHITECTURE.md's 'easy kill switch'."""
        self._killed = True

    def close(self) -> None:
        if not self._killed:
            self._killed = True
        if _sessions_per_ip[self.client_ip] > 0:
            _sessions_per_ip[self.client_ip] -= 1

    async def watchdog(self) -> None:
        """Await this alongside the pipeline task; returns when the session should stop."""
        while not self.expired():
            await asyncio.sleep(1)
