# ============================================================
# integration_starter.py — WEEK 7 MILESTONE 4: INTEGRATION
# ============================================================
# What this script does:
#
#   For each problem in the suite:
#     1. CODER      — get an initial solution from the LLM
#     2. BENCHMARK  — score it on hidden cases
#     3. REFINER    — if score < 1.0, run refinement to improve it
#     4. RE-BENCHMARK — score the refined version
#
#   Then: produce a single REPORT showing what happened, problem
#   by problem. The report is your deliverable.
#
# Fill in the THREE TODOs at the bottom. The Coder, Benchmarker, and
# Refiner helpers are imported from pipeline.py and ready to use.
#
# Why this matters:
#   Up until now, your Coder/Benchmarker/Refiner have been three
#   separate scripts. Today they become ONE system. The lesson is
#   composition — how do these pieces pass state to each other?
#   What is the final artifact? That artifact is the report.
# ============================================================

import time

from pipeline import (
    PROBLEMS, BLOCK_MARKER,
    coder, refine, retry_loop, save_report,
)

# Which problems to run. Add 10 once your peer-authored problem is loaded.
SUITE = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def integrate_one(problem_id: int) -> dict:
    """
    Run the full pipeline on one problem.

    The result dict you return becomes one row in the final report.
    """
    title = PROBLEMS[problem_id]["title"]
    print(f"\n  Problem {problem_id}: {title}")

    t_start = time.time()

    # TODO 1 ──────────────────────────────────────────────────
    # Run the Coder phase. Call coder(problem_id) and store the
    # result. Print the initial score so the TA can see progress.
    #
    # initial = coder(problem_id)
    # print(f"    Coder:     {initial['score']:.2f}")
    #
    # YOUR CODE HERE

    # TODO 2 ──────────────────────────────────────────────────
    # If initial['score'] < 1.0, run the Refiner OR the retry loop:
    #   - If the initial code has block markers, call refine(...)
    #   - Otherwise, call retry_loop(...)
    #
    # Tip: count BLOCK_MARKER matches in initial['code'].
    # If >= 2 markers found → refine. Otherwise → retry_loop.
    #
    # Print the final score after this phase.
    #
    # YOUR CODE HERE

    # TODO 3 ──────────────────────────────────────────────────
    # Return a dict containing AT LEAST these fields:
    #   - problem_id
    #   - title
    #   - initial_score
    #   - final_score
    #   - phase_used         ("refiner" or "retry" or "none")
    #   - duration_seconds   (use time.time() - t_start)
    #
    # YOUR CODE HERE

    return {}   # ← replace with your result dict


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(f"  INTEGRATION — running on problems {SUITE}")
    print("=" * 60)

    all_results = []
    for pid in SUITE:
        result = integrate_one(pid)
        if result:   # TODO students fill this in
            all_results.append(result)

    if all_results:
        save_report(all_results, SUITE)
    else:
        print("\n  No results to report. Fill in the TODOs in integrate_one().")
