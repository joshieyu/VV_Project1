"""Pin-level FIFO driver. It is the only layer that assigns DUT inputs."""
from cocotb.triggers import RisingEdge, FallingEdge, Timer


class FifoDriver:
    """Apply one request per clock.

    Inputs change on the falling edge, half a period before the rising edge
    that consumes them. Each call returns 1 ns after that rising edge, when
    the registered outputs have settled and can be sampled.
    """

    def __init__(self, dut):
        self.dut = dut

    def init(self):
        """Hold reset with idle requests until the first driven cycle."""
        self.dut.rst_n.value = 0
        self.dut.wr_en.value = 0
        self.dut.rd_en.value = 0
        self.dut.wr_data.value = 0

    async def reset(self, wr_en=0, rd_en=0, wr_data=0):
        await self._apply(0, wr_en, rd_en, wr_data)

    async def cycle(self, wr_en=0, rd_en=0, wr_data=0):
        await self._apply(1, wr_en, rd_en, wr_data)

    async def _apply(self, rst_n, wr_en, rd_en, wr_data):
        await FallingEdge(self.dut.clk)
        self.dut.rst_n.value = rst_n
        self.dut.wr_en.value = wr_en
        self.dut.rd_en.value = rd_en
        self.dut.wr_data.value = wr_data
        await RisingEdge(self.dut.clk)
        await Timer(1, units="ns")
