"""Pin-level FIFO monitor. It reads DUT pins and never drives them.

Every sample is a dict with the inputs that reached the DUT and its outputs:

    rst_n, wr_en, rd_en, wr_data   inputs as seen at the pins
    count, full, empty             status outputs
    rd_data                        FWFT head, or None while empty (undefined)
    rd_data_raw                    the rd_data pin even while empty, or None
                                   if it is X/Z (used by fifo_trust only)
"""
from cocotb.triggers import FallingEdge, Timer


class FifoMonitor:
    def __init__(self, dut):
        self.dut = dut

    async def before_edge(self):
        """Sample 1 ns after the falling edge: this cycle's inputs, old state."""
        await FallingEdge(self.dut.clk)
        await Timer(1, units="ns")
        return self.sample()

    def sample(self):
        empty = int(self.dut.empty.value)
        raw = self.dut.rd_data.value
        return {
            "rst_n": int(self.dut.rst_n.value),
            "wr_en": int(self.dut.wr_en.value),
            "rd_en": int(self.dut.rd_en.value),
            "wr_data": int(self.dut.wr_data.value),
            "count": int(self.dut.count.value),
            "full": int(self.dut.full.value),
            "empty": empty,
            "rd_data": int(raw) if not empty else None,
            "rd_data_raw": int(raw) if raw.is_resolvable else None,
        }
