"""Security & Trust thread (vplan S1): what an empty FIFO shows on rd_data.

The spec defines a read while empty (it is ignored) but leaves rd_data
undefined while empty. Undefined behavior is where data can leak: an empty
FIFO might still show a word that a reset was supposed to discard.

Each read request seen while the FIFO is empty is covered by situation and
request:

    after_reset   no accepted write since a reset
    after_drain   reads emptied the FIFO
    x  read alone, or read racing a write (simultaneous)

Each one also records whether rd_data shows a word that was written before
the latest reset and not since. Memory starts as X, so such a word can only
be left over from before the reset. The spec allows this, so it is counted,
not failed. FIFO_TRUST_STRICT=1 turns it into an assertion.
"""
import os

from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db

CONTEXTS = ["after_reset", "after_drain"]


def _make_sampler(name):
    @CoverPoint(f"{name}.context", xf=lambda context, wr: context, bins=CONTEXTS)
    @CoverPoint(f"{name}.request", xf=lambda context, wr: wr, bins=[0, 1],
                bins_labels=["read", "simultaneous"])
    @CoverCross(f"{name}.context_x_request",
                items=[f"{name}.context", f"{name}.request"])
    def sample(context, wr):
        pass

    return sample


class TrustObserver:
    def __init__(self, log, name="fifo.trust"):
        self.log = log
        self.name = name
        self.sample = _make_sampler(name)
        self.strict = os.environ.get("FIFO_TRUST_STRICT") == "1"
        self.written_before_reset = set()
        self.written_since_reset = set()
        self.context = None
        self.requests = 0
        self.exposed = 0

    def __call__(self, kind, before, after):
        if kind == "reset":
            self.written_before_reset |= self.written_since_reset
            self.written_since_reset = set()
            self.context = "after_reset"
            return

        if before["empty"] and before["rd_en"] and self.context:
            self.sample(self.context, before["wr_en"])
            self.requests += 1
            shown = before["rd_data_raw"]
            if (shown in self.written_before_reset
                    and shown not in self.written_since_reset):
                self.exposed += 1
                message = (f"S1: empty FIFO shows 0x{shown:02x} ({self.context}), "
                           "a word written only before the latest reset")
                assert not self.strict, message
                if self.exposed <= 3:
                    self.log.info(message)

        if before["wr_en"] and not before["full"]:
            self.written_since_reset.add(before["wr_data"])
            self.context = None
        if after["empty"] and not before["empty"]:
            self.context = "after_drain"

    def report(self):
        self.log.info(f"S1: {self.requests} empty read requests covered, "
                      f"{self.exposed} showed a word from before the latest reset")

    def require_closed(self):
        cross = coverage_db[f"{self.name}.context_x_request"]
        missing = [str(key) for key, hits in cross.detailed_coverage.items()
                   if not hits]
        assert not missing, f"{self.name}: missing bins {', '.join(missing)}"
