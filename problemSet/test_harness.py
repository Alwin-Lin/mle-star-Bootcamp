# ============================================================
# test_harness.py — offline regression test for the grading harness
# ============================================================
# Validates run_cases.run_cases() without any network access.
# Tests: correct solution → score 1.0, wrong solution → WA/RE.
#
# Usage:
#   python test_harness.py
# ============================================================

import pathlib
import sys

CODE_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

import run_cases  # noqa: E402


def _write_solution(code: str) -> None:
    (CODE_DIR / "solution.py").write_text(code, encoding="utf-8")


def _cleanup() -> None:
    sol = CODE_DIR / "solution.py"
    if sol.exists():
        sol.unlink()


def test_correct_solution_scores_1() -> None:
    # Problem 1 (Tram Stops) — verified correct against all 10 cases.
    _write_solution("""\
def tram_distance(n, trips):
    total = 0
    for board, exit_ in trips:
        if exit_ >= board:
            total += exit_ - board
        else:
            total += (n - board) + exit_
    return total
""")
    result = run_cases.run_cases(1)
    assert result["score"] == 1.0, (
        f"Expected score 1.0 for correct tram_distance, got {result['score']}.\n"
        f"Failures: {result.get('failures')}"
    )


def test_wrong_solution_gets_wa_or_re() -> None:
    _write_solution("""\
def tram_distance(n, trips):
    return -999
""")
    result = run_cases.run_cases(1)
    reasons = {f["reason"] for f in result.get("failures", [])}
    assert "WA" in reasons or "RE" in reasons, (
        f"Expected WA or RE verdict for wrong solution, got: {result}"
    )


if __name__ == "__main__":
    try:
        test_correct_solution_scores_1()
        print("PASS  correct solution -> score 1.0")

        test_wrong_solution_gets_wa_or_re()
        print("PASS  wrong solution   -> WA/RE")

        print("\nAll harness tests passed.")
    finally:
        _cleanup()
