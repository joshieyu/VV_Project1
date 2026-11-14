"""Project 1 constrained-random FIFO transactions (pyvsc).

The only randomized DUT inputs are wr_en, rd_en and wr_data. Auxiliary
random rolls implement explicit conditional rates; count/phase/mode are
NON-random state provided by the reference-queue testbench.

No request pair is illegal under dut/specs/fifo.md: at full a write is
ignored, and at empty a read is ignored. All 4 combinations remain reachable.
"""
import vsc

DEPTH = 8
FILL = 0
DRAIN = 1
UNIFORM = 0
TUNED = 1


def next_phase(phase, count):
    """Change direction ONLY when the reference model hits a boundary."""
    if count == DEPTH:
        return DRAIN
    if count == 0:
        return FILL
    return phase


@vsc.randobj
class FifoTransaction:
    """Generate FIFO requests; mode='uniform' is the untuned baseline.

    Nominal enable rates, conditional on known pre-edge model state:
       uniform: any count, each enable P=0.50, independent
       tuned:   count in {0, 8}: both P=0.50, independent
                interior, FILL: P(wr)=0.75, P(rd)=0.25
                interior, DRAIN: P(wr)=0.25, P(rd)=0.75

    The `solve_order` matters on course-pinned pyvsc: it makes the 0..99
    rolls solve BEFORE 1-bit enables. Nominal rates are not results: measure
    the generated distribution in the simulator before citing them.
    """

    def __init__(self, mode="tuned"):
        if mode not in ("uniform", "tuned"):
            raise ValueError(f"unknown mode {mode!r}")
        self.wr_en = vsc.rand_bit_t(1)
        self.rd_en = vsc.rand_bit_t(1)
        self.wr_data = vsc.rand_bit_t(8)

        self.roll_w = vsc.rand_uint8_t()
        self.roll_r = vsc.rand_uint8_t()
        self.thr_w = vsc.rand_uint8_t()
        self.thr_r = vsc.rand_uint8_t()

        self.count = vsc.uint8_t(0)       # non-random, from scoreboard.model
        self.phase = vsc.uint8_t(FILL)    # non-random, updated after each edge
        self.mode = vsc.uint8_t(UNIFORM if mode == "uniform" else TUNED)

    @vsc.constraint
    def c_rolls(self):
        self.roll_w < 100
        self.roll_r < 100
        vsc.solve_order([self.roll_w, self.roll_r], [self.wr_en, self.rd_en])

    @vsc.constraint
    def c_thresholds(self):
        with vsc.if_then(self.mode == UNIFORM):
            self.thr_w == 50
            self.thr_r == 50
        with vsc.else_if((self.count == 0) | (self.count == DEPTH)):
            self.thr_w == 50
            self.thr_r == 50
        with vsc.else_if(self.phase == FILL):
            self.thr_w == 75
            self.thr_r == 25
        with vsc.else_then:
            self.thr_w == 25
            self.thr_r == 75

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
