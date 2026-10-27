"""Pre-edge occupancy x requested operation coverage for the FIFO."""
from pathlib import Path

from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db


def make_sampler(name, depth=8):
    """Use a distinct name for each directed, reset, or random campaign."""
    @CoverPoint(f"{name}.occupancy", xf=lambda count, wr, rd: count,
                bins=list(range(depth + 1)))
    @CoverPoint(f"{name}.request", xf=lambda count, wr, rd: (wr, rd),
                bins=[(0, 0), (1, 0), (0, 1), (1, 1)],
                bins_labels=["idle", "write", "read", "simultaneous"])
    @CoverCross(f"{name}.occupancy_x_request",
                items=[f"{name}.occupancy", f"{name}.request"])
    def sample(count, wr, rd):
        pass

    return sample


def require_closed(name):
    cross = coverage_db[f"{name}.occupancy_x_request"]
    missing = [str(key) for key, hits in cross.detailed_coverage.items() if not hits]
    assert not missing, f"{name}: missing bins {', '.join(missing)}"


def export_coverage(path, logger):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    coverage_db.export_to_yaml(str(path))
    coverage_db.report_coverage(logger)
