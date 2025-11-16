"""Simple background simulation loop used to drive the agentic dashboard."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, Optional

from ..core.config import settings
from ..core import supabase as supabase_module


@dataclass
class SimulationSnapshot:
    """Structured payload describing the current simulation status."""

    is_running: bool
    current_tick: int
    total_ticks: int
    tick_interval_seconds: int
    simulated_time: str
    last_tick_time: Optional[str]
    started_at: Optional[str]
    estimated_completion: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SimulationEngine:
    """Drives a lightweight 15-minute tick simulation for demos."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task] = None
        self._broadcast: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None

        self.is_running: bool = False
        self.current_tick: int = 0
        self.total_ticks: int = settings.SIMULATION_TOTAL_TICKS
        self.tick_interval_seconds: int = settings.SIMULATION_TICK_SECONDS
        self._simulated_time: datetime = datetime.utcnow()
        self._started_at: Optional[datetime] = None
        self._last_tick_time: Optional[datetime] = None

    def set_broadcaster(
        self, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        self._broadcast = callback

    async def start(self) -> SimulationSnapshot:
        async with self._lock:
            if self.is_running:
                return self.snapshot
            self.is_running = True
            self._started_at = datetime.utcnow()
            if not self._task or self._task.done():
                self._task = asyncio.create_task(self._run_loop())
        return self.snapshot

    async def stop(self) -> SimulationSnapshot:
        async with self._lock:
            self.is_running = False
            if self._task and not self._task.done():
                self._task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._task
        return self.snapshot

    async def step(self) -> SimulationSnapshot:
        await self._process_tick()
        return self.snapshot

    async def _run_loop(self) -> None:
        try:
            while self.is_running:
                await asyncio.sleep(self.tick_interval_seconds)
                await self._process_tick()
        except asyncio.CancelledError:
            pass

    async def _process_tick(self) -> None:
        self.current_tick = (self.current_tick + 1) % (self.total_ticks + 1)
        if self.current_tick == 0:
            # new simulated day
            self._simulated_time = datetime.utcnow()
        else:
            self._simulated_time += timedelta(minutes=15)

        self._last_tick_time = datetime.utcnow()
        payload = self.snapshot.as_dict()

        await self._persist(payload)
        if self._broadcast:
            await self._broadcast({"type": "simulation_update", "payload": payload})

    async def _persist(self, payload: Dict[str, Any]) -> None:
        if not supabase_module.is_supabase_configured():
            return
        supabase = supabase_module.get_supabase_client()
        try:
            record = {
                "id": settings.SIMULATION_STATUS_ROW_ID,
                "is_running": payload["is_running"],
                "current_tick": payload["current_tick"],
                "total_ticks": payload["total_ticks"],
                "tick_interval_seconds": payload["tick_interval_seconds"],
                "current_time": payload["simulated_time"],
                "last_tick_time": payload["last_tick_time"],
                "started_at": payload["started_at"],
                "estimated_completion": payload["estimated_completion"],
                "updated_at": datetime.utcnow().isoformat(),
            }
            supabase.table("simulation_status").upsert(record).execute()
        except Exception as exc:  # pragma: no cover - best effort persistence
            print(f"Error persisting simulation status: {exc}")

    @property
    def snapshot(self) -> SimulationSnapshot:
        est_completion: Optional[str] = None
        if self._started_at:
            remaining_ticks = max(self.total_ticks - self.current_tick, 0)
            estimate = self._last_tick_time or self._started_at
            est_completion = (
                estimate + timedelta(seconds=remaining_ticks * self.tick_interval_seconds)
            ).isoformat()

        return SimulationSnapshot(
            is_running=self.is_running,
            current_tick=self.current_tick,
            total_ticks=self.total_ticks,
            tick_interval_seconds=self.tick_interval_seconds,
            simulated_time=self._simulated_time.isoformat(),
            last_tick_time=self._last_tick_time.isoformat() if self._last_tick_time else None,
            started_at=self._started_at.isoformat() if self._started_at else None,
            estimated_completion=est_completion,
        )


simulation_engine = SimulationEngine()
