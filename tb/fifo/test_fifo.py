# requests -> driver -> FIFO -> monitor -> scoreboard (FifoModel)
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from models.fifo_model import FifoModel
from fifo_coverage import make_sampler, export_coverage, require_closed


class FifoDriver:
    def __init__(self, dut):
        self.dut = dut

    async def reset(self, wr_en=0, rd_en=0, wr_data=0):
        await FallingEdge(self.dut.clk)
        self.dut.rst_n.value = 0
        self.dut.wr_en.value = wr_en
        self.dut.rd_en.value = rd_en
        self.dut.wr_data.value = wr_data
        await RisingEdge(self.dut.clk)
        await Timer(1, units="ns")

    async def cycle(self, wr_en=0, rd_en=0, wr_data=0):
        await FallingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        self.dut.wr_en.value = wr_en
        self.dut.rd_en.value = rd_en
        self.dut.wr_data.value = wr_data
        await RisingEdge(self.dut.clk)
        await Timer(1, units="ns")


class FifoMonitor:
    def __init__(self, dut):
        self.dut = dut

    async def before_edge(self):
        await FallingEdge(self.dut.clk)
        await Timer(1, units="ns")
        return self.sample()

    def sample(self):
        empty = int(self.dut.empty.value)
        return {
            "count": int(self.dut.count.value),
            "full": int(self.dut.full.value),
            "empty": empty,
            "rd_data": int(self.dut.rd_data.value) if not empty else None,
        }


class FifoScoreboard:
    def __init__(self):
        self.model = FifoModel(8, 8)

    def step(self, wr_en, rd_en, wr_data):
        self.model.step(wr_en, wr_data, rd_en)

    def check(self, actual):
        assert actual["count"] == self.model.count, \
            f"count: got {actual['count']}, expected {self.model.count}"
        assert actual["full"] == self.model.full, \
            f"full: got {actual['full']}, expected {self.model.full}"
        assert actual["empty"] == self.model.empty, \
            f"empty: got {actual['empty']}, expected {self.model.empty}"
        if not self.model.empty:
            assert actual["rd_data"] == self.model.head, \
                f"rd_data: got {actual['rd_data']}, expected {self.model.head}"


@cocotb.test()
async def test_fifo(dut):
    dut.clk.value = 0
    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    driver = FifoDriver(dut)
    monitor = FifoMonitor(dut)
    scoreboard = FifoScoreboard()
    sample_directed = make_sampler("fifo.directed")
    sample_reset = make_sampler("fifo.reset")
    sample_traffic = sample_directed

    async def cycle(wr_en=0, rd_en=0, wr_data=0):
        # Check the head being consumed before updating the model.
        before_edge = cocotb.start_soon(monitor.before_edge())
        await driver.cycle(wr_en, rd_en, wr_data)
        scoreboard.check(await before_edge)
        sample_traffic(scoreboard.model.count, wr_en, rd_en)
        scoreboard.step(wr_en, rd_en, wr_data)
        scoreboard.check(monitor.sample())

    async def reset(wr_en=0, rd_en=0, wr_data=0):
        before_edge = cocotb.start_soon(monitor.before_edge())
        await driver.reset(wr_en, rd_en, wr_data)
        # Reset is synchronous, so the old state must hold before the edge.
        scoreboard.check(await before_edge)
        sample_reset(scoreboard.model.count, wr_en, rd_en)
        scoreboard.model.reset()
        scoreboard.check(monitor.sample())

    await driver.reset()
    scoreboard.model.reset()
    scoreboard.check(monitor.sample())

    await cycle()
    await cycle(0, 1)  # read while empty
    await cycle(1, 1, 0xa5)  # empty: only the write is accepted
    await cycle(0, 1)

    # Reset must win over all request combinations at every occupancy.
    for level in range(9):
        for wr_en, rd_en in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            for i in range(level):
                await cycle(1, 0, 0x40 + i)
            await reset(wr_en, rd_en, 0xff)
            await cycle(1, 0, 0xa5)
            await cycle(0, 1)

    # Fill and drain repeatedly so both pointers wrap.
    for round_num in range(3):
        for i in range(8):
            await cycle(1, 0, round_num * 16 + i)
        await cycle()
        await cycle(1, 0, 0xee)  # full: this write must be dropped
        await cycle(1, 1, 0xdd)  # full: only the read is accepted
        for _ in range(7):
            await cycle(0, 1)
        await cycle(0, 1)

    # Both requests at each non-empty, non-full count.
    for level in range(1, 8):
        for i in range(level):
            await cycle(1, 0, i)
        for i in range(16):
            await cycle(1, 1, 0x80 + i)
        for _ in range(level):
            await cycle(0, 1)

    rng = random.Random(4701)
    sample_traffic = make_sampler("fifo.hw4_seed_4701")
    for _ in range(500):
        await cycle(rng.randrange(2), rng.randrange(2), rng.randrange(256))

    # Drain anything left so the last stored values also get checked.
    sample_traffic = sample_directed
    for _ in range(8):
        await cycle(0, 1)
    await cycle()

    # Reset with data still in the queue, then use it again.
    sample_traffic = sample_directed
    for value in [0, 0xff, 0x55]:
        await cycle(1, 0, value)
    await reset()
    await cycle(1, 0, 0xaa)
    await cycle(0, 1)

    # Two-request sequences at every occupancy and circular head position.
    requests = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for offset in range(8):
        for level in range(9):
            for first in requests:
                for second in requests:
                    await reset()
                    for i in range(offset):
                        await cycle(1, 0, i)
                        await cycle(0, 1)
                    for i in range(level):
                        await cycle(1, 0, (offset * 31 + i * 17) & 0xff)
                    await cycle(*first, 0xa5)
                    await cycle(*second, 0x5a)
                    for _ in range(8):
                        await cycle(0, 1)

    # Every byte value with simultaneous requests at every count and slot.
    for level in range(9):
        await reset()
        for i in range(level):
            await cycle(1, 0, i)
        for value in range(256):
            for _ in range(8):
                await cycle(1, 1, value)
                if level == 0:
                    await cycle(0, 1)
                elif level == 8:
                    await cycle(1, 0, value ^ 0xff)
        for _ in range(8):
            await cycle(0, 1)

    # Sustained blocked requests must not disturb pointers or stored data.
    for _ in range(32):
        await cycle(0, 1)
    for value in range(8):
        await cycle(1, 0, 0x80 + value)
    for value in range(32):
        await cycle(1, 0, value)
    for _ in range(8):
        await cycle(0, 1)

    for seed in [4702, 4703, 4704]:
        rng = random.Random(seed)
        sample_traffic = make_sampler(f"fifo.hw4_seed_{seed}")
        for _ in range(2048):
            await cycle(rng.randrange(2), rng.randrange(2), rng.randrange(256))
        sample_traffic = sample_directed
        for _ in range(8):
            await cycle(0, 1)

    export_coverage(Path(__file__).resolve().parents[2] / "artifacts/coverage.yml",
                    dut._log.info)
    require_closed("fifo.directed")
    require_closed("fifo.reset")
