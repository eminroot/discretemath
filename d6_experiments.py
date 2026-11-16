"""Team 4 - Hash Collisions and the Birthday Problem (D6).
Part 5: the simulation from D5 repeated with five seeds and three generators:
        random integers, truncated SHA-256 of labels such as "s2027-k300-t15-i7",
        and truncated SHA-256 of random 7-character codes in the format of FIN codes.
Part 6: k = 301 and k = 302 with 500,000 trials each, to see the threshold directly.
Part 7: P(k) for 10 million inputs and different output sizes (real-life scenario).
Part 8: graph of P(k) for k = 1, ..., 600 together with the simulated points.
The independent runs are sent to different processor cores to save time.
"""
import hashlib
import json
import math
import random
import string
import time
from fractions import Fraction
from multiprocessing import Pool

N = 2 ** 16
T = 10_000
K_VALUES = [100, 200] + list(range(250, 351, 10)) + [400, 500]
SEEDS = [2026, 2027, 2028, 2029, 2030]
BIG_T = 500_000
ALPHABET = string.digits + string.ascii_uppercase  # 36 symbols, like FIN codes


def exact_P(N, k):
    """P(k) as an exact fraction (same function as in D5)."""
    q = Fraction(1)
    for i in range(k):
        q *= Fraction(N - i, N)
    return 1 - q


def first16(text):
    """First 16 bits of SHA-256 of a string, as a number from 0 to 65,535."""
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:2], byteorder="big")


def random_outputs(rng, seed, k, t):
    return [rng.randrange(N) for _ in range(k)]


def sha_label_outputs(rng, seed, k, t):
    """SHA-256 of k different labels; the seed is part of the label."""
    return [first16(f"s{seed}-k{k}-t{t}-i{i}") for i in range(k)]


def fin_codes(rng, k):
    """k different random 7-character codes made of digits and capital letters."""
    codes = set()
    while len(codes) < k:
        codes.add("".join(rng.choices(ALPHABET, k=7)))
    return codes


def sha_fin_outputs(rng, seed, k, t):
    return [first16(code) for code in fin_codes(rng, k)]


GENERATORS = {"random": random_outputs, "sha_label": sha_label_outputs, "sha_fin": sha_fin_outputs}


def estimate(k, trials, generator, rng, seed):
    hits = sum(1 for t in range(trials) if len(set(generator(rng, seed, k, t))) < k)
    return hits / trials


def run_seed(seed):
    """Part 5 for one seed: every generator and every k, T = 10,000 trials each."""
    rng = random.Random(seed)
    results = {}
    for name, generator in GENERATORS.items():
        results[name] = [estimate(k, T, generator, rng, seed) for k in K_VALUES]
    return seed, results


def run_threshold(task):
    """Part 6: one generator at one k with 500,000 trials."""
    name, k = task
    rng = random.Random(f"{name}-{k}")  # a different fixed seed for every run
    return name, k, estimate(k, BIG_T, GENERATORS[name], rng, 0)


def p_ten_million(n, k=10_000_000):
    """P(k) for an n-bit hash, from the product formula in log form."""
    N = 2 ** n
    if k > N:
        return 1.0  # pigeonhole principle
    log_q = sum(math.log1p(-i / N) for i in range(k))
    return -math.expm1(log_q)


def draw_figure(means):
    """Part 8: exact P(k) for k = 1, ..., 600 and the mean simulated estimate of each generator."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ks, q, curve = list(range(1, 601)), 1.0, []
    for k in ks:
        q *= 1 - (k - 1) / N
        curve.append(1 - q)
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11, "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    ax.plot(ks, curve, color="black", linewidth=1.4, label="Exact $P(k)$")
    ax.scatter(K_VALUES, [means[k]["random"] for k in K_VALUES], s=22, color="#1f5f99",
               zorder=3, label="Random integers")
    ax.scatter(K_VALUES, [means[k]["sha_fin"] for k in K_VALUES], s=26, marker="^",
               facecolors="none", edgecolors="#c0392b", zorder=3, label="SHA-256 of FIN-format codes")
    ax.axhline(0.5, color="grey", linestyle="--", linewidth=0.8)
    ax.axvline(256, color="grey", linestyle=":", linewidth=0.8)
    ax.axvline(302, color="grey", linestyle="-.", linewidth=0.8)
    ax.text(250, 0.9, "$2^{n/2}$ = 256", ha="right", fontsize=10)
    ax.text(308, 0.9, "$k^*$ = 302", ha="left", fontsize=10)
    ax.set_xlabel("Number of inputs $k$")
    ax.set_ylabel("P(at least one collision)")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    fig.tight_layout()
    fig.savefig("figure1_pk.png", dpi=300)


if __name__ == "__main__":
    start = time.time()
    exact = {k: float(exact_P(N, k)) for k in K_VALUES + [301, 302]}
    with Pool(9) as pool:
        part6 = pool.map_async(run_threshold, [(g, k) for g in ("random", "sha_fin") for k in (301, 302)])
        part5 = dict(pool.map(run_seed, SEEDS))
        part6 = part6.get()

    # ---------------- Part 5: five seeds ----------------
    print(f"Part 5: {len(SEEDS)} seeds x {len(K_VALUES)} values of k x {len(GENERATORS)} generators, T = {T:,}")
    all_z = []
    for name in GENERATORS:
        z_scores, worst = [], (0.0, None, None)
        for seed in SEEDS:
            for k, est in zip(K_VALUES, part5[seed][name]):
                p = exact[k]
                se = math.sqrt(p * (1 - p) / T)
                z_scores.append(abs(est - p) / se)
                if abs(est - p) > worst[0]:
                    worst = (abs(est - p), seed, k)
        all_z += z_scores
        m = len(z_scores)
        within = [sum(z <= c for z in z_scores) for c in (1, 2, 3)]
        print(f"  {name:>9}: {m} estimates, within 1/2/3 SE: {within[0]}/{within[1]}/{within[2]}, "
              f"largest difference {worst[0]:.4f} (seed {worst[1]}, k = {worst[2]})")
    m = len(all_z)
    within = [sum(z <= c for z in all_z) for c in (1, 2, 3)]
    print(f"  all: {m} estimates, within 1 SE: {within[0]} ({within[0] / m:.1%}, expected 68.3%), "
          f"2 SE: {within[1]} ({within[1] / m:.1%}, expected 95.4%), "
          f"3 SE: {within[2]} ({within[2] / m:.1%}, expected 99.7%)")
    print(f"\n{'k':>4} {'exact':>8}" + "".join(f" {name + ' mean':>15}" for name in GENERATORS))
    means = {}
    for i, k in enumerate(K_VALUES):
        row = [sum(part5[s][name][i] for s in SEEDS) / len(SEEDS) for name in GENERATORS]
        means[k] = dict(zip(GENERATORS, row))
        print(f"{k:>4} {exact[k]:8.4f}" + "".join(f" {v:15.4f}" for v in row))

    # ---------------- Part 6: k = 301 and k = 302 ----------------
    print(f"\nPart 6: {BIG_T:,} trials for each k")
    for name, k, est in sorted(part6):
        p = exact[k]
        se = math.sqrt(est * (1 - est) / BIG_T)
        print(f"  {name:>7}, k = {k}: estimate {est:.5f}, exact {p:.5f}, SE {se:.5f}, "
              f"(estimate - exact)/SE = {(est - p) / se:+.2f}, (estimate - 0.5)/SE = {(est - 0.5) / se:+.2f}")

    # ---------------- Part 7: 10 million inputs ----------------
    print("\nPart 7: P(collision) for 10,000,000 inputs")
    for n in (16, 20, 24, 32, 48, 64, 128, 256):
        print(f"  n = {n:>3}: P = {p_ten_million(n):.3e}")
    n_min = next(n for n in range(1, 257) if p_ten_million(n) < 1e-6)
    print(f"  smallest n with P < one in a million: {n_min}")

    # ---------------- Part 8: graph ----------------
    draw_figure(means)

    with open("d6_results.json", "w") as f:
        json.dump({"exact": exact, "part5": part5, "part6": part6, "means": means}, f, indent=1)
    print(f"\ntotal time: {time.time() - start:.1f} s")
