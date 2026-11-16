# discretemath

Source code for the MATH 301 (Fundamentals of Discrete Mathematics) team project of Team 4 at Baku Higher Oil School:
**Hash Collisions and the Birthday Problem**.

Team: Emin Bakhishli, Amil Alasgarov, Kanan Garayzade, Vusal Huseynov.

The question: how many inputs does a 16-bit hash (N = 65,536 possible outputs) need before the probability of at
least one collision reaches 0.5? The exact answer is k* = 302.

## Files

| File | What it does |
| ---- | ------------ |
| `d5_solution.py` | Parts 1 to 4 (D5): exact P(k) with the recurrence relation, k* with exact fractions, 20-bit and 24-bit outputs, the verification tests, and the simulation with random integers and truncated SHA-256 (T = 10,000). |
| `d6_experiments.py` | Parts 5 to 8 (D6): the simulation with five seeds and three generators (random integers, SHA-256 of labels, SHA-256 of random FIN-format codes), k = 301 and k = 302 with 500,000 trials, P(collision) for 10 million inputs, and the graph of P(k). |
| `d5_output.txt`, `d6_output.txt` | The output of the two programs. |
| `d6_results.json` | The raw simulation estimates from `d6_experiments.py`. |
| `figure1_pk.png` | Figure 1 of the report. |

## How to run

Python 3.9 or newer. `d5_solution.py` uses only the standard library. `d6_experiments.py` also needs matplotlib
for the graph (`pip install matplotlib`).

```
python d5_solution.py
python d6_experiments.py
```

`d5_solution.py` takes about 2 to 3 minutes. `d6_experiments.py` runs the independent simulations on several
processor cores and takes about 10 minutes. Both use fixed seeds, so they print the same numbers every time.
