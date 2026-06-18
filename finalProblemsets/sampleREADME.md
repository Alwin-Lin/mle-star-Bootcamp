# Verdict Loop

![Python](https://img.shields.io/badge/python-3.11-blue) ![Status](https://img.shields.io/badge/status-coursework-green)

An agentic solver for competitive programming problems. It hands a problem statement to an LLM, runs the generated program against hidden tests, reads the verdict, and lets the model try again — looping until it gets an **AC** or runs out of attempts.

> *Team Nullptr · Competitive Programming Track, Week 8*

## What it does

Given only a problem statement (no test cases), Verdict Loop drives an LLM through a feedback loop: it generates a complete Python program, runs it against the hidden LiveBench test cases, and feeds the verdict — including which case failed — back into the next attempt. The whole point is the **retry**: a single generation often fails, but a loop that reads its own mistakes recovers on most problems within a few tries.

## Quickstart

```bash
# 1. clone and install
git clone https://github.com/team-nullptr/verdict-loop.git
cd verdict-loop
pip install -r requirements.txt

# 2. cache the LiveBench dataset once (needs a connection)
python data/filter.py --download

# 3. set your LLM key and model
export LLM_API_KEY="sk-..."
export MODEL="claude-sonnet-4"

# 4. solve one problem
python solve.py --problem data/samples/two_sum_hard.json --verbose
```

> **Heads up:** after the first download, run offline so HuggingFace doesn't time out (`ConnectionError: ReadTimeout`):
> ```bash
> export HF_DATASETS_OFFLINE=1
> export HF_HUB_OFFLINE=1
> ```

## How it works

The loop lives in `pipeline/loop.py`:

```
read problem  →  generate program  →  run vs hidden tests  →  read verdict
                        ▲                                          │
                        └──────────── retry (if not AC) ───────────┘
```

1. **Generate** — the statement goes into a prompt template (`prompts.py`); the model returns a full program. We extract **only** the ```python fence (`extract.py`) so any chatter the model adds can't break compilation.
2. **Run** — `runner.py` executes the program against each hidden case in a subprocess with a timeout, normalizing trailing whitespace before comparing.
3. **Verdict** — AC / WA / TLE / RE, plus the first failing case (expected vs got).
4. **Retry** — on a non-AC verdict we add the **failing case and a one-line diff of what we changed last time** to the prompt, so the model doesn't re-propose the same fix. Capped at **5 attempts**.

The pipeline is verbose by design. Every iteration logs a plan, a diff, and a verdict so we (and the graders) can see what it's thinking:

```
iter 1  plan  binary-search the answer · O(n log n)
iter 1  run   WA on case 3  (exp 14, got 13)
iter 2  diff  fix off-by-one in hi bound
iter 2  run   AC  (12/12 cases)
```

## Evaluation

We grade against LiveBench's `coding_generation` tasks. Each problem ships with hidden test cases the model never sees.

- **All-or-nothing:** a problem counts as solved only if the program passes *every* case.
- **Capped retries:** ≤ 5 attempts per problem; we record attempts-to-first-AC.
- **Held-out check:** one case per problem is withheld from the loop and only run at the end. If a solver passes the shown cases but fails the held-out one, it's memorizing the trace, not solving — so all reported numbers are on the **held-out** set.
- **Interactive problems are filtered** before evaluation (see Limitations).

Reproduce our numbers:

```bash
python eval.py --split held_out --out results/held_out.json
python eval.py --report results/held_out.json
```

## Results

On the 25-problem held-out set:

| Metric | Held-out | Shown-only (for comparison) |
|---|---|---|
| Solve rate | **18 / 25 (72%)** | 22 / 25 (88%) |
| Avg. attempts to first AC | 2.3 | 1.9 |
| Solved on first try | 9 / 25 | 14 / 25 |

The 16-point gap between shown and held-out is real overfitting on a few problems — the loop occasionally tuned its output to the cases it could see. We treat the **72%** as our honest number.

**A failure we couldn't crack — Problem #14 (range-sum queries):** the model produced an O(n²) scan that was correct but always TLE'd. The loop read each TLE as "try again" and regenerated nearly the same program, never reducing complexity. Fixing this would mean feeding the **time limit and input bounds** into the retry prompt so TLE reads as "go faster," not "retry." We ran out of time to add it.

## Limitations & known issues

- **Interactive problems are unsupported and filtered out.** They need a live two-way judge (read N → print → flush → read verdict → answer); our static stdin/stdout runner can't grade them, and exact-match would reject valid alternate answers anyway.
- **Overfitting on visible cases** still happens on a minority of problems (see Results). The held-out check catches it but the loop doesn't yet prevent it.
- **TLE handling is weak** — the retry prompt doesn't pass complexity constraints, so "too slow" failures often stall (Problem #14).
- **Output formatting** is the most common silent WA: a stray trailing space or missing final newline. We normalize per line in the runner, but a stricter judge could still differ.

## Repo layout

```
.
├── solve.py            # single-problem agentic loop (entry point)
├── eval.py             # batch eval over a split + reporting
├── pipeline/
│   ├── loop.py         # generate → run → verdict → retry
│   ├── prompts.py      # prompt templates
│   ├── runner.py       # sandboxed execution + verdict
│   └── extract.py      # pulls code from the ```python fence
├── data/
│   ├── filter.py       # downloads dataset, drops interactive problems
│   └── samples/        # a few problems for quick testing
├── results/
│   └── held_out.json   # our reported run
├── requirements.txt
├── .gitignore          # excludes the HF cache, results/, and the API key
└── README.md
```