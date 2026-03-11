"""Tests pour engine.core.time_manager."""

import time
from engine.core.time_manager import TimeManager


class TestTimeManager:
    def test_dt_initial_zero(self):
        tm = TimeManager()
        assert tm.dt == 0.0

    def test_tick_returns_positive(self):
        tm = TimeManager()
        time.sleep(0.01)
        dt = tm.tick()
        assert dt > 0

    def test_ticks_accumulate(self):
        tm = TimeManager()
        time.sleep(0.01)
        tm.tick()
        t1 = tm.ticks
        time.sleep(0.01)
        tm.tick()
        t2 = tm.ticks
        assert t2 > t1

    def test_dt_property(self):
        tm = TimeManager()
        time.sleep(0.01)
        dt = tm.tick()
        assert tm.dt == dt
