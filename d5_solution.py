"""Team 4 - Hash Collisions and the Birthday Problem (D5).
Part 1: exact probability P(k) of at least one collision and the threshold k*.
Part 2: the same algorithm for 20-bit and 24-bit outputs.
Part 3: verification tests from our verification plan (D3).
Part 4: simulation with random integers and with truncated SHA-256.
"""
import hashlib
import itertools
import math
import random
import time
from fractions import Fraction
def threshold(N):
    """Return k* and the list of P(k) for k = 1, ..., k*.
    q is the probability that all k outputs are different. When the k-th
    input is added, it must avoid the k - 1 values already taken, so q is
    multiplied by 1 - (k - 1)/N. We stop at the first k with P(k) >= 0.5.
    """
    q, k, probs = 1.0, 1, [0.0]  # P(1) = 0
    while 1 - q < 0.5:
        k += 1
        q *= 1 - (k - 1) / N
        probs.append(1 - q)
    return k, probs
def exact_P(N, k):
    """P(k) as an exact fraction, so that rounding cannot change the answer."""
    q = Fraction(1)
    for i in range(k):
        q *= Fraction(N - i, N)
    return 1 - q

# ---------------- Part 1: 16-bit hash ----------------
N = 2 ** 16
k_star, probs = threshold(N)
print("k* for N = 65,536:", k_star)
for k in (k_star - 2, k_star - 1, k_star, k_star + 1):
    print(f"  P({k}) = {float(exact_P(N, k)):.5f}")
print("  exact P(k*-1) < 1/2:", exact_P(N, k_star - 1) < Fraction(1, 2))
print("  exact P(k*)  >= 1/2:", exact_P(N, k_star) >= Fraction(1, 2))
print("  2^(n/2) = 256, sqrt(2N ln 2) =", round(math.sqrt(2 * N * math.log(2)), 2))

# ---------------- Part 2: other output sizes ----------------
for n in (16, 20, 24):
    ks, _ = threshold(2 ** n)
    approx = math.sqrt(2 * 2 ** n * math.log(2))
    print(f"n = {n}: k* = {ks}, 2^(n/2) = {2 ** (n // 2)}, "
          f"approx = {approx:.1f}, ratio = {ks / 2 ** (n / 2):.4f}")
print("SHA-256 estimate: 1.1774 * 2^128 =", f"{math.sqrt(2 * math.log(2)) * 2 ** 128:.2e}")

# ---------------- Part 3: verification tests ----------------
cases = list(itertools.product(range(4), repeat=3))  # N = 4, k = 3
with_collision = sum(1 for c in cases if len(set(c)) < 3)
print("N = 4, k = 3:", len(cases), "cases,", with_collision, "with a collision,",
      "formula gives", exact_P(4, 3))
print("Birthday problem (N = 365): k* =", threshold(365)[0])
print("P(1) =", exact_P(N, 1), " P(2) =", exact_P(N, 2))
q, increasing = 1.0, True
for k in range(2, N + 2):
    new_q = q * (1 - (k - 1) / N)
    increasing = increasing and new_q <= q
    q = new_q
print("P(k) never decreases up to k = 65,537:", increasing, " P(65,537) =", 1 - q)

# ---------------- Part 4: simulation ----------------
T = 10_000
K_VALUES = [100, 200] + list(range(250, 351, 10)) + [400, 500]
rng = random.Random(2026)  # fixed seed
def random_outputs(k, t):
    return [rng.randrange(N) for _ in range(k)]
def sha_outputs(k, t):
    """First 16 bits of SHA-256 of k distinct strings (new strings every trial)."""
    return [int.from_bytes(hashlib.sha256(f"k{k}-t{t}-i{i}".encode()).digest()[:2], byteorder="big")
            for i in range(k)]
def estimate(k, generator):
    hits = sum(1 for t in range(T) if len(set(generator(k, t))) < k)
    return hits / T
print(f"\n{'k':>4} {'exact':>8} {'random':>8} {'SHA-256':>8} {'max diff':>9}")
worst = 0.0
start = time.time()
for k in K_VALUES:
    p = float(exact_P(N, k))
    r, s = estimate(k, random_outputs), estimate(k, sha_outputs)
    diff = max(abs(r - p), abs(s - p))
    worst = max(worst, diff)
    print(f"{k:>4} {p:8.4f} {r:8.4f} {s:8.4f} {diff:9.4f}")
print(f"largest difference: {worst:.4f} (limit 3 SE = 0.015)")
print(f"simulation time: {time.time() - start:.1f} s")
