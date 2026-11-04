"""Distribution, corner bound, and coverage/mutation correlation.

    PYTHONPATH=lib:grad python grad/analyze.py
    PYTHONPATH=lib:grad python grad/analyze.py --trial phased 10042

Reads grad/results/regression*.{csv,json} from run_regression.py and writes
grad/results/analysis.json plus the figures in grad/figures/. --trial reruns
one Monte Carlo trial by itself and prints its outcome and stream hash.
"""
import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import vsc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models.fifo_model import FifoModel
from stimulus import (DEPTH, FILL, DRAIN, PhasedTxn, UniformTxn, next_phase,
                      rates)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
REQUESTS = [(0, 0), (1, 0), (0, 1), (1, 1)]
LABELS = ["idle", "write", "read", "simultaneous"]
STATES = [(0, FILL)] + [(c, p) for c in range(1, DEPTH) for p in (FILL, DRAIN)] \
         + [(DEPTH, DRAIN)]
INDEX = {s: i for i, s in enumerate(STATES)}
CORNER = "full with rd_en"
P_TARGET, N_TARGET = 0.999, 6 * DEPTH
MC_SEEDS, MC_BASE = 3000, 10_000


@vsc.randobj
class UnorderedTxn(PhasedTxn):
    """PhasedTxn without solve_order: the same text, the solver's default."""

    @vsc.constraint
    def c_rolls(self):
        self.roll_w < 100
        self.roll_r < 100


MC_STIMULI = {"phased": PhasedTxn, "unordered": UnorderedTxn,
              "uniform": UniformTxn}


def measure(cls, draws, seed=2026, **kw):
    """Realized P(request) at every reachable (count, phase)."""
    random.seed(seed)
    txn = cls(**kw)
    table = {}
    for c, phase in STATES:
        txn.count, txn.phase = c, phase
        hits = [0] * 4
        for _ in range(draws):
            txn.randomize()
            hits[REQUESTS.index((int(txn.wr_en), int(txn.rd_en)))] += 1
        table[c, phase] = [h / draws for h in hits]
    return table


def nominal(**kw):
    table = {}
    for s, (pw, pr) in rates(**kw).items():
        if s in INDEX:
            table[s] = [(1 - pw) * (1 - pr), pw * (1 - pr), (1 - pw) * pr, pw * pr]
    return table


def chain(table, absorb_corner=False):
    """Transition matrix; with absorb_corner, state n is 'corner reached'."""
    n = len(STATES)
    P = np.zeros((n + 1, n + 1))
    P[n, n] = 1.0
    for (c, phase), probs in table.items():
        i = INDEX[c, phase]
        for (w, r), p in zip(REQUESTS, probs):
            if absorb_corner and c == DEPTH and r:
                P[i, n] += p
                continue
            nxt = c + (w and c < DEPTH) - (r and c > 0)
            P[i, INDEX[nxt, next_phase(phase, nxt)]] += p
    return P if absorb_corner else P[:n, :n]


def occupancy(dist):
    occ = np.zeros(DEPTH + 1)
    for (c, _), p in zip(STATES, dist):
        occ[c] += p
    return occ


def stationary(table):
    P = chain(table)
    vals, vecs = np.linalg.eig(P.T)
    pi = np.real(vecs[:, np.argmin(abs(vals - 1))])
    return pi / pi.sum()


def corner_curve(table, n_max):
    """Exact P(corner within N draws from reset), N = 0..n_max."""
    P = chain(table, absorb_corner=True)
    v = np.zeros(len(P))
    v[INDEX[0, FILL]] = 1.0
    out = [0.0]
    for _ in range(n_max):
        v = v @ P
        out.append(v[-1])
    return np.array(out)


def first_n(curve, p):
    hit = np.nonzero(curve >= p)[0]
    return int(hit[0]) if len(hit) else None


def expected_fill_time(a, end_write):
    """E[draws to first reach full from reset] in the FILL phase.

    Birth-death chain: up u = a^2 and down d = (1-a)^2 inside, up u0 at 0.
    m_k = E[time from k to k+1] obeys m_0 = 1/u0, m_k = (1 + d m_{k-1}) / u.
    """
    u, d = a * a, (1 - a) ** 2
    m = 1 / end_write
    total = m
    for _ in range(1, DEPTH):
        m = (1 + d * m) / u
        total += m
    return total


def mc_trial(cls, n, seed):
    """One seeded trial: (draw that hit the corner or None, stream hash).

    A pyvsc object seeds its own generator from the stdlib one on its first
    randomize() and ignores random.seed() after that, so every trial builds a
    new object after seeding.
    """
    random.seed(seed)
    txn = cls()
    model, phase = FifoModel(8, DEPTH), FILL
    stream, hit = [], None
    for draw in range(n):
        txn.count, txn.phase = model.count, phase
        txn.randomize()
        request = (int(txn.wr_en), int(txn.rd_en), int(txn.wr_data))
        stream.append(request)
        if model.count == DEPTH and request[1]:
            hit = draw
            break
        model.step(request[0], request[2], request[1])
        phase = next_phase(phase, model.count)
    return hit, hashlib.sha256(repr(stream).encode()).hexdigest()[:16]


def monte_carlo(cls, n, seeds):
    """Per-seed results of trials MC_BASE .. MC_BASE + seeds - 1."""
    return {MC_BASE + i: mc_trial(cls, n, MC_BASE + i) for i in range(seeds)}


def wilson(p, n, z=1.96):
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x, y):
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def load_regression():
    rows = list(csv.DictReader(open(RESULTS / "regression.csv")))
    for r in rows:
        for k, v in r.items():
            if k not in ("stim", "stream"):
                r[k] = int(v)
    bins = {tuple(b["point"]): b["x1"] for b in
            json.load(open(RESULTS / "regression_bins.json"))}
    return rows, bins


def bin_hits(x1, occ, req):
    return x1[str((occ, req))]


def main():
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    out = {}

    # 1. Realized rates.
    tables = {
        "phased (nominal)": nominal(),
        "phased (measured)": measure(PhasedTxn, 2000),
        "unordered (measured)": measure(UnorderedTxn, 2000),
        "uniform (measured)": measure(UniformTxn, 2000),
    }
    out["rates"] = {name: {f"{c},{'FD'[p]}": [round(x, 4) for x in probs]
                           for (c, p), probs in t.items()}
                    for name, t in tables.items()}

    # 2. Occupancy: chain prediction vs. RTL histogram from the regression.
    rows, bins = load_regression()
    n_long = max(r["cycles"] for r in rows)
    observed = {}
    for stim in ("phased", "uniform"):
        occ = np.zeros(DEPTH + 1)
        for (s, n, _), x1 in bins.items():
            if s == stim and n == n_long:
                for key, hits in x1.items():
                    occ[int(key.strip("()").split(",")[0])] += hits
        observed[stim] = occ / occ.sum()
    flat = np.full(DEPTH + 1, 1 / (DEPTH + 1))
    hist = {
        "phased chain": occupancy(stationary(tables["phased (measured)"])),
        "phased RTL": observed["phased"],
        "uniform chain": occupancy(stationary(tables["uniform (measured)"])),
        "uniform RTL": observed["uniform"],
    }
    tv = lambda p, q: 0.5 * float(abs(p - q).sum())
    out["occupancy"] = {k: [round(x, 4) for x in v] for k, v in hist.items()}
    out["occupancy_cycles"] = n_long
    out["tv"] = {
        "phased RTL vs phased chain": tv(hist["phased RTL"], hist["phased chain"]),
        "uniform RTL vs uniform chain": tv(hist["uniform RTL"], hist["uniform chain"]),
        "phased chain vs flat": tv(hist["phased chain"], flat),
        "uniform chain vs flat": tv(hist["uniform chain"], flat),
        "phased chain vs uniform chain": tv(hist["phased chain"], hist["uniform chain"]),
    }

    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    x = np.arange(DEPTH + 1)
    ax.bar(x - 0.2, hist["phased RTL"], 0.4, label="phased, RTL", color="#3b6ea5")
    ax.bar(x + 0.2, hist["uniform RTL"], 0.4, label="uniform, RTL", color="#c0c0c0")
    ax.plot(x - 0.2, hist["phased chain"], "o", color="#1b3a5c", ms=4,
            label="phased, chain $\\pi$")
    ax.plot(x + 0.2, hist["uniform chain"], "s", color="#555555", ms=4,
            label="uniform, chain $\\pi$")
    ax.axhline(1 / (DEPTH + 1), ls="--", lw=0.8, color="k", label="flat 1/9")
    ax.set_xlabel("pre-edge occupancy")
    ax.set_ylabel("fraction of cycles")
    ax.set_xticks(x)
    ax.legend(fontsize=7, ncol=3, loc="upper center")
    ax.set_ylim(0, 0.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "occupancy.pdf")

    # 3. Corner: full with a read in the same cycle.
    curves = {name: corner_curve(t, 1024) for name, t in tables.items()}
    out["corner"] = {name: {"N_for_p": {str(p): first_n(c, p) for p in (0.9, 0.99, 0.999)},
                            f"P_within_{N_TARGET}": round(float(c[N_TARGET]), 4)}
                     for name, c in curves.items()}

    # Derive the smallest fill write rate that clears P_TARGET in N_TARGET.
    derivation = []
    for a in range(60, 91):
        c = corner_curve(nominal(fill_write=a), N_TARGET)
        derivation.append({"fill_write": a, f"P_within_{N_TARGET}": round(float(c[-1]), 4),
                           "E_fill": round(expected_fill_time(a / 100, 0.5), 2)})
    out["derivation"] = derivation
    out["derived_fill_write"] = next(d["fill_write"] for d in derivation
                                     if d[f"P_within_{N_TARGET}"] >= P_TARGET)

    mc = {}
    for name, cls in MC_STIMULI.items():
        trials = monte_carlo(cls, N_TARGET, MC_SEEDS)
        p = sum(hit is not None for hit, _ in trials.values()) / MC_SEEDS
        mc[name] = {"p": p, "ci95": [round(v, 4) for v in wilson(p, MC_SEEDS)],
                    "sample": {s: trials[s] for s in (MC_BASE, MC_BASE + 42,
                                                      MC_BASE + MC_SEEDS - 1)}}
    out["monte_carlo"] = {"N": N_TARGET, "seeds": MC_SEEDS,
                          "first_seed": MC_BASE, **mc}

    # Regression check: did each RTL run hit the corner bins?
    reg_corner = {}
    for stim in ("phased", "uniform"):
        for n in sorted({r["cycles"] for r in rows}):
            pts = [x1 for (s, m, _), x1 in bins.items() if s == stim and m == n]
            got = sum(1 for x1 in pts if bin_hits(x1, DEPTH, "read")
                      or bin_hits(x1, DEPTH, "simultaneous"))
            reg_corner[f"{stim},{n}"] = [got, len(pts)]
    out["regression_corner"] = reg_corner

    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    styles = {"phased (measured)": ("#3b6ea5", "-"), "phased (nominal)": ("#3b6ea5", ":"),
              "unordered (measured)": ("#d08c2b", "-"), "uniform (measured)": ("#777777", "-")}
    for name, (col, ls) in styles.items():
        ax.plot(np.arange(257), curves[name][:257], ls, color=col, label=name)
    ax.axhline(P_TARGET, lw=0.6, color="k")
    ax.axvline(N_TARGET, lw=0.6, color="k")
    ax.set_xlabel("draws from reset, N")
    ax.set_ylabel("P(full with rd_en by N)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "corner.pdf")

    # 4. Coverage vs. found/total.
    cov = [r["bins_hit"] for r in rows]
    found = [r["found"] for r in rows]
    out["correlation"] = {
        "points": len(rows),
        "spearman_all": round(spearman(cov, found), 3),
        "pearson_all": round(float(np.corrcoef(cov, found)[0, 1]), 3),
        "spearman_by_cycles": {},
    }
    for n in sorted({r["cycles"] for r in rows}):
        sub = [r for r in rows if r["cycles"] == n]
        c, f = [r["bins_hit"] for r in sub], [r["found"] for r in sub]
        rho = spearman(c, f) if len(set(c)) > 1 and len(set(f)) > 1 else None
        out["correlation"]["spearman_by_cycles"][n] = rho
    table = {}
    for stim in ("phased", "uniform"):
        for n in sorted({r["cycles"] for r in rows}):
            sub = [r for r in rows if r["stim"] == stim and r["cycles"] == n]
            table[f"{stim},{n}"] = {
                "bins_mean": round(sum(r["bins_hit"] for r in sub) / len(sub), 1),
                "found_mean": round(sum(r["found"] for r in sub) / len(sub), 2),
                "closed": sum(r["bins_hit"] == 36 for r in sub),
                "eight": sum(r["found"] == 8 for r in sub), "runs": len(sub)}
    out["by_point"] = table

    # Per mutant: is detection explained by a bin it needs being hit?
    needs = {
        "ignore_full": [(DEPTH, "write"), (DEPTH, "simultaneous")],
        "ignore_empty": [(0, "read"), (0, "simultaneous")],
        "full_offbyone": [(DEPTH - 1, l) for l in LABELS],
        "empty_offbyone": [(1, l) for l in LABELS],
        "count_wr_dec": [(c, "write") for c in range(DEPTH)],
    }
    per_mutant = {}
    for mid, need in needs.items():
        grid = {"hit,found": 0, "hit,missed": 0, "miss,found": 0, "miss,missed": 0}
        for r in rows:
            x1 = bins[r["stim"], r["cycles"], r["seed"]]
            hit = any(bin_hits(x1, o, l) for o, l in need)
            grid[f"{'hit' if hit else 'miss'},{'found' if r[mid] else 'missed'}"] += 1
        per_mutant[mid] = grid
    per_mutant["closed X1"] = {
        mid: f"{sum(r[mid] for r in rows if r['bins_hit'] == 36)}/"
             f"{sum(1 for r in rows if r['bins_hit'] == 36)}"
        for mid in ("rd_data_wrptr", "mem_corrupt", "wrptr_wrap_early")}
    out["per_mutant"] = per_mutant

    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    rng = np.random.default_rng(0)
    for stim, col, mk in (("phased", "#3b6ea5", "o"), ("uniform", "#777777", "s")):
        sub = [r for r in rows if r["stim"] == stim]
        ax.scatter([r["bins_hit"] + rng.uniform(-0.25, 0.25) for r in sub],
                   [r["found"] + rng.uniform(-0.12, 0.12) for r in sub],
                   s=[8 + 3 * math.log2(r["cycles"]) ** 1.5 for r in sub],
                   c=col, marker=mk, alpha=0.7, label=stim)
    ax.set_xlabel("X1 bins hit (of 36)")
    ax.set_ylabel("released found (of 8)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "coverage_vs_found.pdf")

    json.dump(out, open(RESULTS / "analysis.json", "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("tv", "corner", "derivation",
                      "derived_fill_write", "monte_carlo", "correlation")},
                     indent=1, default=float))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--trial"]:
        name, seed = sys.argv[2], int(sys.argv[3])
        hit, digest = mc_trial(MC_STIMULI[name], N_TARGET, seed)
        print(f"stim={name} seed={seed} hit_at={hit} stream={digest}")
    else:
        main()
