"""Kyle's dated Check the Machine experiment for vplan F2-F5/X1.

Run explicitly with MODULE=test_coverage_probe; the normal suite is unchanged.
Only the selected probe cycles are sampled. Setup/reset/drain still use the
same driver, monitor and queue checks, but are outside this sampling phase.
"""
import json
from pathlib import Path

import cocotb
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db

from fifo_coverage import make_sampler
from fifo_env import FifoEnv
from test_fifo import FifoScoreboard

REQUESTS = [(0, 0), (1, 0), (0, 1), (1, 1)]


def make_compact_sampler():
    @CoverPoint("probe.compact.band",
                xf=lambda count, wr, rd: "empty" if count == 0 else
                "full" if count == 8 else "interior",
                bins=["empty", "interior", "full"])
    @CoverPoint("probe.compact.request", xf=lambda count, wr, rd: (wr, rd),
                bins=REQUESTS, bins_labels=["idle", "write", "read", "simultaneous"])
    @CoverCross("probe.compact.cross",
                items=["probe.compact.band", "probe.compact.request"])
    def sample(count, wr, rd):
        pass

    return sample


def snapshot(name):
    cross = coverage_db[name]
    return {"hit": cross.coverage, "total": cross.size,
            "missing": sorted(repr(k) for k, hits in cross.detailed_coverage.items()
                              if not hits)}


@cocotb.test()
async def compare_compact_and_exact_coverage(dut):
    env = FifoEnv(dut, FifoScoreboard())
    compact = make_compact_sampler()
    exact_sparse = make_sampler("probe.exact_sparse")
    exact_complete = make_sampler("probe.exact_complete")
    await env.start()

    async def run_probes(occupancies, samplers):
        observations = []

        def sample(count, wr, rd):
            observations.append([count, wr, rd])
            for sampler in samplers:
                sampler(count, wr, rd)

        for count in occupancies:
            for wr, rd in REQUESTS:
                env.sample_traffic = None
                await env.reset()
                for value in range(count):
                    await env.cycle(1, 0, value)
                assert env.scoreboard.model.count == count
                env.sample_traffic = sample
                await env.cycle(wr, rd, 0xa5)
                env.sample_traffic = None
                while env.scoreboard.model.count:
                    await env.cycle(0, 1)
        assert observations == [[count, wr, rd] for count in occupancies
                                for wr, rd in REQUESTS]
        return observations

    sparse = await run_probes([0, 1, 8], [compact, exact_sparse])
    compact_result = snapshot("probe.compact.cross")
    sparse_result = snapshot("probe.exact_sparse.occupancy_x_request")
    complete = await run_probes(range(9), [exact_complete])
    complete_result = snapshot("probe.exact_complete.occupancy_x_request")

    output = Path(__file__).resolve().parents[2] / "artifacts/check_machine"
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps({
        "sampling": "probe cycles only; setup/reset/drain excluded",
        "sparse_observations": sparse, "compact": compact_result,
        "exact_sparse": sparse_result, "complete_observations": complete,
        "exact_complete": complete_result,
    }, indent=2) + "\n")
    coverage_db.export_to_yaml(str(output / "coverage.yml"))
    dut._log.info("Compact %s/%s; exact sparse %s/%s; exact complete %s/%s",
                 compact_result["hit"], compact_result["total"],
                 sparse_result["hit"], sparse_result["total"],
                 complete_result["hit"], complete_result["total"])
    assert compact_result["hit"] == compact_result["total"] == 12
    assert sparse_result["hit"] == 12 and sparse_result["total"] == 36
    assert len(sparse_result["missing"]) == 24
    assert complete_result["hit"] == complete_result["total"] == 36
