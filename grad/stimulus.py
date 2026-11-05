"""pyvsc stimulus for the graduate-extension analysis.

These classes exist to measure a distribution and derive a corner bound.
They are not the team's crv/ layer; analyze.py takes any class with the same
fields (wr_en, rd_en, wr_data, and the non-random count and phase).

PhasedTxn sweeps the FIFO: in FILL it favors writes, in DRAIN it favors
reads, and the phase flips when the reference queue reaches full or empty.
At the two ends both requests are 50/50, so all four request bins stay
likely there.

Each enable comes from a uniform roll. solve_order makes pyvsc pick the roll
before the enable. Without it the pinned pyvsc picks the 1-bit enable first
and pulls the realized rate toward 0.5 (0.37 measured for a nominal 0.30).
"""
import vsc

DEPTH = 8
FILL, DRAIN = 0, 1

# Percent chance of each enable, by (phase, band). Interior is 1..DEPTH-1.
FILL_WRITE = 75
END_WRITE = 50
END_READ = 50


def rates(fill_write=FILL_WRITE, end_write=END_WRITE, end_read=END_READ):
    """Nominal (P(wr_en), P(rd_en)) for every reachable (count, phase)."""
    a = fill_write / 100
    table = {}
    for c in range(DEPTH + 1):
        for phase in (FILL, DRAIN):
            if c == 0 or c == DEPTH:
                table[c, phase] = (end_write / 100, end_read / 100)
            elif phase == FILL:
                table[c, phase] = (a, 1 - a)
            else:
                table[c, phase] = (1 - a, a)
    return table


def next_phase(phase, count):
    """Update from the reference count after the edge, never from a DUT flag."""
    if count == DEPTH:
        return DRAIN
    if count == 0:
        return FILL
    return phase


@vsc.randobj
class PhasedTxn:
    def __init__(self, fill_write=FILL_WRITE, end_write=END_WRITE,
                 end_read=END_READ):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(8)
        self.roll_w = vsc.rand_uint8_t()
        self.roll_r = vsc.rand_uint8_t()
        self.count = vsc.uint8_t(0)       # fed from the reference queue
        self.phase = vsc.uint8_t(FILL)    # fed from next_phase()
        self.fill_write = vsc.uint8_t(fill_write)
        self.end_write = vsc.uint8_t(end_write)
        self.end_read = vsc.uint8_t(end_read)
        self.thr_w = vsc.rand_uint8_t()
        self.thr_r = vsc.rand_uint8_t()

    @vsc.constraint
    def c_rolls(self):
        self.roll_w < 100
        self.roll_r < 100
        vsc.solve_order([self.roll_w, self.roll_r], [self.wr_en, self.rd_en])

    @vsc.constraint
    def c_thresholds(self):
        # thr_* are fully determined by the state; they are rand only so
        # one pair of implications below covers every band.
        with vsc.if_then((self.count == 0) | (self.count == DEPTH)):
            self.thr_w == self.end_write
            self.thr_r == self.end_read
        with vsc.else_if(self.phase == FILL):
            self.thr_w == self.fill_write
            self.thr_r == 100 - self.fill_write
        with vsc.else_then:
            self.thr_w == 100 - self.fill_write
            self.thr_r == self.fill_write

    @vsc.constraint
    def c_enables(self):
        with vsc.implies(self.roll_w < self.thr_w):
            self.wr_en == 1
        with vsc.implies(self.roll_w >= self.thr_w):
            self.wr_en == 0
        with vsc.implies(self.roll_r < self.thr_r):
            self.rd_en == 1
        with vsc.implies(self.roll_r >= self.thr_r):
            self.rd_en == 0


@vsc.randobj
class UniformTxn:
    """Unshaped baseline: every field uniform, count and phase ignored."""

    def __init__(self):
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(8)
        self.count = vsc.uint8_t(0)
        self.phase = vsc.uint8_t(FILL)


STIMULI = {"phased": PhasedTxn, "uniform": UniformTxn}
