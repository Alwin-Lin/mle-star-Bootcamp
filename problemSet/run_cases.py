# ============================================================
# run_cases.py — TEST HARNESS (updated for Week 7)
# ============================================================
# Same harness as Weeks 5–6: measures time + memory, classifies as
# AC / TLE / MLE / WA / RE.
#
# New: dispatches to problem 9 (is_balanced).
# Problem 10 uses a metadata-driven dispatcher (see below) so the
# peer-authored problem just needs to specify its function name.
#
# Usage:
#   python run_cases.py <problem_id>
# ============================================================

import sys
import json
import time
import pathlib
import tracemalloc
import importlib
import traceback

CODE_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from problem_set import PROBLEMS


# Static dispatch for problems 1–9 (function names are fixed)
_DISPATCH = {
    1: "tram_distance",
    2: "manage_inventory",
    3: "decode_message",
    4: "compression_score",
    5: "frequency_tag",
    6: "first_occurrence_only",
    7: "log_triage",
    8: "robot_walk",
    9: "is_balanced",
}


def _call_solution(sol, problem_id: int, args: dict):
    """Look up the function name and call it.

    For problems 1–9, the function name is hard-coded.
    For problem 10 (peer-authored), the function name is taken from the
    problem's 'function_name' field if present.
    """
    if problem_id in _DISPATCH:
        fn_name = _DISPATCH[problem_id]
    else:
        # Peer-authored problem 10 — get function name from problem metadata
        fn_name = PROBLEMS[problem_id].get("function_name")
        if not fn_name:
            raise ValueError(
                f"Problem {problem_id} has no function_name in its metadata"
            )

    fn = getattr(sol, fn_name, None)
    if fn is None:
        raise AttributeError(
            f"solution.py does not define function '{fn_name}'"
        )

    return fn(**args)


def _input_size_label(args: dict) -> str:
    for key, val in args.items():
        if isinstance(val, (list, str)):
            return f"{key} len={len(val)}"
        if isinstance(val, int):
            return f"{key}={val}"
    return str(args)[:80]


def run_cases(problem_id: int) -> dict:
    cases  = PROBLEMS[problem_id]["hidden_cases"]
    total  = len(cases)
    passed = 0
    failures = []

    try:
        import solution as sol
        importlib.reload(sol)
    except Exception:
        return {
            "score": 0.0, "passed": 0, "total": total,
            "failures": [{
                "case": "import", "reason": "RE",
                "got": f"Import error:\n{traceback.format_exc()}"
            }]
        }

    for i, case_tuple in enumerate(cases, start=1):
        args, expected, time_limit_ms, memory_limit_mb = case_tuple

        tracemalloc.start()
        t0 = time.perf_counter()
        result = None
        error_msg = None

        try:
            result = _call_solution(sol, problem_id, args)
        except Exception:
            error_msg = traceback.format_exc()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mb = peak / (1024 * 1024)

        if error_msg:
            reason = "RE"
        elif result != expected:
            reason = "WA"
        elif elapsed_ms > time_limit_ms:
            reason = "TLE"
        elif peak_mb > memory_limit_mb:
            reason = "MLE"
        else:
            reason = "AC"

        if reason == "AC":
            passed += 1
        else:
            entry = {
                "case":       i,
                "reason":     reason,
                "time_ms":    round(elapsed_ms, 1),
                "limit_ms":   time_limit_ms,
                "memory_mb":  round(peak_mb, 2),
                "limit_mb":   memory_limit_mb,
                "input_size": _input_size_label(args),
            }
            if reason == "WA":
                raw = str(args)
                entry["input"] = (
                    args if len(raw) < 200
                    else f"(large — {_input_size_label(args)})"
                )
                entry["expected"] = (
                    expected if len(str(expected)) < 100
                    else f"(large, first 50: {str(expected)[:50]})"
                )
                entry["got"] = repr(result)[:200]
            if reason == "RE":
                entry["got"] = error_msg[-500:]
            failures.append(entry)

    return {
        "score":    round(passed / total, 2),
        "passed":   passed,
        "total":    total,
        "failures": failures,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python run_cases.py <problem_id>"}))
        sys.exit(1)
    try:
        problem_id = int(sys.argv[1])
    except ValueError:
        print(json.dumps({"error": "problem_id must be an integer"}))
        sys.exit(1)
    result = run_cases(problem_id)
    print(json.dumps(result))
