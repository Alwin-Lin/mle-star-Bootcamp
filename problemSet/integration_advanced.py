# ============================================================
# integration_advanced.py — WEEK 7 MILESTONE 4: INTEGRATION
# ============================================================
# Full integration. For each problem in SUITE:
#
#   1. CODER       → initial solution
#   2. BENCHMARK   → score it
#   3. If score < 1.0 AND solution has block markers:
#         REFINER  → 2 rounds × 3 variants per round
#      Else if score < 1.0:
#         RETRY    → 2 attempts with TLE/WA feedback
#   4. Record final score, phase used, duration
#
# At the end: write integration_report.json (machine) and
# integration_report.txt (human). Both are your deliverables.
#
# Usage:
#   python integration_advanced.py
#
# Expected runtime: 15–25 minutes for 9 problems with Gemma 4 rate
# limits. Run with patience.
# ============================================================

import time

from pipeline import (
    PROBLEMS, BLOCK_MARKER,
    coder, refine, retry_loop, save_report,
)

SUITE = [1, 2, 3, 4, 5, 6, 7, 8, 9]
# Include 10 here when peer-authored problem is loaded:
# SUITE = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


# ── The integration ───────────────────────────────────────────

def integrate_one(problem_id: int) -> dict:
    title = PROBLEMS[problem_id]["title"]
    print(f"\n  {'─' * 56}")
    print(f"  Problem {problem_id}: {title}")
    print(f"  {'─' * 56}")

    t_start = time.time()

    # Phase 1: Coder
    initial = coder(problem_id)
    print(f"    Coder       → {initial['score']:.2f}  "
          f"({initial['passed']}/{initial['total']})")

    if initial["score"] >= 1.0:
        return {
            "problem_id":       problem_id,
            "title":            title,
            "initial_score":    initial["score"],
            "final_score":      initial["score"],
            "phase_used":       "none",
            "duration_seconds": time.time() - t_start,
        }

    # Phase 2: Refiner or Retry
    has_blocks = len(BLOCK_MARKER.findall(initial["code"])) >= 2

    if has_blocks:
        print("    Refiner     → starting (multi-block detected)")
        result = refine(problem_id, initial["code"], initial["score"])
        phase  = "refiner"
    else:
        print("    Retry       → starting (single-block)")
        result = retry_loop(problem_id, initial["code"], initial["score"])
        phase  = "retry"

    print(f"    {phase.capitalize():<11} → {result['score']:.2f}")

    return {
        "problem_id":       problem_id,
        "title":            title,
        "initial_score":    initial["score"],
        "final_score":      result["score"],
        "phase_used":       phase,
        "duration_seconds": time.time() - t_start,
    }


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(f"  INTEGRATION — running on problems {SUITE}")
    print(f"  Expected runtime: ~{len(SUITE) * 2.5:.0f} min")
    print("=" * 60)

    results = [integrate_one(pid) for pid in SUITE]
    save_report(results, SUITE)
