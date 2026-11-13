"""Per-cycle glue shared by directed and random FIFO tests.

    requests -> driver -> FIFO -> monitor -> scoreboard (+ coverage sampler)

The scoreboard and samplers are passed in, so a test chooses its own
checker and coverage phase. A scoreboard needs `model` (a FifoModel),
`step(wr_en, rd_en, wr_data)`, and `check(sample)`. Each callable in
`observers` is called as `observer(kind, before, after)` after every cycle,
with kind "cycle" or "reset".

Set FIFO_TRACE=N to log the monitor samples for the first N cycles.
"""
import os

import cocotb
from cocotb.clock import Clock
from cocotb.utils import get_sim_time

from fifo_driver import FifoDriver
from fifo_monitor import FifoMonitor

INPUTS = ("rst_n", "wr_en", "rd_en", "wr_data")


class FifoEnv:
    def __init__(self, dut, scoreboard, sample_traffic=None, sample_reset=None):
        self.dut = dut
        self.driver = FifoDriver(dut)
        self.monitor = FifoMonitor(dut)
        self.scoreboard = scoreboard
        # Coverage callbacks: (pre-edge reference count, wr_en, rd_en).
        self.sample_traffic = sample_traffic
        self.sample_reset = sample_reset
        self.observers = []
        self.cycles = 0
        self.trace = int(os.environ.get("FIFO_TRACE", "0"))

    async def start(self, period_ns=10):
        """Start the clock and apply the initial reset.

        There is no initialized state before the first reset, so it is not
        checked or sampled for coverage.
        """
        self.dut.clk.value = 0
        self.driver.init()
        cocotb.start_soon(Clock(self.dut.clk, period_ns, units="ns").start())
        await self.driver.reset()
        self.scoreboard.model.reset()
        self.scoreboard.check(self.monitor.sample())

    async def cycle(self, wr_en=0, rd_en=0, wr_data=0):
        before = await self._drive(1, wr_en, rd_en, wr_data)
        # Check the head being consumed before updating the model.
        self.scoreboard.check(before)
        if self.sample_traffic:
            self.sample_traffic(self.scoreboard.model.count,
                                before["wr_en"], before["rd_en"])
        self.scoreboard.step(before["wr_en"], before["rd_en"], before["wr_data"])
        after = self.monitor.sample()
        self.scoreboard.check(after)
        self._finish("cycle", before, after)
        return before, after

    async def reset(self, wr_en=0, rd_en=0, wr_data=0):
        before = await self._drive(0, wr_en, rd_en, wr_data)
        # Reset is synchronous, so the old state must hold before the edge.
        self.scoreboard.check(before)
        if self.sample_reset:
            self.sample_reset(self.scoreboard.model.count,
                              before["wr_en"], before["rd_en"])
        self.scoreboard.model.reset()
        after = self.monitor.sample()
        self.scoreboard.check(after)
        self._finish("reset", before, after)
        return before, after

    async def _drive(self, rst_n, wr_en, rd_en, wr_data):
        apply = self.driver.cycle if rst_n else self.driver.reset
        before_edge = cocotb.start_soon(self.monitor.before_edge())
        await apply(wr_en, rd_en, wr_data)
        before = await before_edge
        # The scoreboard steps on sampled inputs, so they must be the request.
        requested = dict(zip(INPUTS, (rst_n, wr_en, rd_en, wr_data)))
        for name, value in requested.items():
            assert before[name] == value, \
                f"{name}: drove {value}, monitor saw {before[name]}"
        self.cycles += 1
        return before

    def _finish(self, kind, before, after):
        for observer in self.observers:
            observer(kind, before, after)
        self._log(before, after)

    def _log(self, before, after):
        if self.cycles <= self.trace:
            self.dut._log.info(f"cycle {self.cycles}, after-edge sample at "
                               f"{get_sim_time('ns')} ns: before={before} "
                               f"after={after}")
