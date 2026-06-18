# ============================================================
# pipeline.py — shared pipeline utilities
# ============================================================
# All helpers shared by integration_starter.py and
# integration_advanced.py live here: LLM access, the grading
# harness, the Coder / Refiner / Retry phases, and the report
# writers.  Each integration script imports from this module and
# adds only its own integrate_one() strategy and __main__ block.
# ============================================================

import os
import re
import sys
import json
import time
import datetime
import pathlib
import subprocess
import google.generativeai as genai

CODE_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from problem_set import PROBLEMS, get_prompt  # noqa: F401 (re-exported)

# ── Configuration ─────────────────────────────────────────────
API_KEY       = os.environ.get("GEMINI_API_KEY", "YOUR_KEY_HERE")
MODEL         = "gemma-4-27b-it"
SLEEP_SECS    = 4
NUM_VARIANTS  = 3
REFINE_ROUNDS = 2
MAX_RETRIES   = 2

REPORT_JSON_FILE = str(CODE_DIR / "integration_report.json")
REPORT_TEXT_FILE = str(CODE_DIR / "integration_report.txt")
SOLUTION_FILE    = str(CODE_DIR / "solution.py")

genai.configure(api_key=API_KEY)
_llm = genai.GenerativeModel(MODEL)

BLOCK_MARKER = re.compile(r"#\s*──\s*BLOCK:\s*(\w+)\s*──")


# ── LLM and harness helpers ───────────────────────────────────

def ask_llm(prompt: str) -> str:
    return _llm.generate_content(prompt).text


def extract_code(raw: str) -> str:
    match = re.search(r"```python\s*(.*?)```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(def \w+\(.*)", raw, re.DOTALL)
    return match.group(1).strip() if match else ""


def run_and_score(problem_id: int) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(CODE_DIR / "run_cases.py"), str(problem_id)],
            capture_output=True, text=True, timeout=120,
        )
        return json.loads(proc.stdout)
    except Exception as e:
        return {"score": 0.0, "passed": 0, "total": 10,
                "failures": [{"case": "harness", "reason": "RE", "got": str(e)}]}


def split_blocks(code: str) -> dict:
    blocks = {"_preamble": ""}
    current_name = "_preamble"
    current_lines = []
    for line in code.split("\n"):
        match = BLOCK_MARKER.search(line)
        if match:
            blocks[current_name] = "\n".join(current_lines)
            current_name = match.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)
    blocks[current_name] = "\n".join(current_lines)
    return blocks


def join_blocks(blocks: dict) -> str:
    pieces = [blocks.get("_preamble", "")]
    for name, content in blocks.items():
        if name == "_preamble":
            continue
        pieces.append(content)
    return "\n".join(pieces)


def stub_block(name: str, content: str) -> str:
    lines = content.split("\n")
    marker = lines[0]
    indent = "    "
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = line[: len(line) - len(stripped)]
            break
    return f"{marker}\n{indent}pass  # ablated"


def build_feedback(data: dict) -> str:
    failures = data.get("failures", [])
    tle = [f for f in failures if f.get("reason") == "TLE"]
    wa  = [f for f in failures if f.get("reason") == "WA"]
    parts = []
    if tle:
        timing = "\n".join(
            f"  Case {f['case']}: {f.get('input_size', '?')}, "
            f"took {f['time_ms']} ms (limit {f['limit_ms']} ms)"
            for f in tle[:3]
        )
        parts.append(
            f"TIME LIMIT EXCEEDED on {len(tle)} case(s). "
            f"Your answers were CORRECT but too slow:\n{timing}\n"
            f"Your approach is likely O(n²). Use a faster algorithm or "
            f"data structure (dict/set lookup, single-pass)."
        )
    if wa:
        wa_lines = "\n".join(
            f"  Case {f['case']}: expected {f.get('expected')}, "
            f"got {f.get('got')}"
            for f in wa[:3]
        )
        parts.append(f"WRONG ANSWER on {len(wa)} case(s):\n{wa_lines}")
    return "\n\n".join(parts) if parts else "Unknown failure."


# ── PHASE 1: Coder ────────────────────────────────────────────

def coder(problem_id: int) -> dict:
    """Get an initial solution from the LLM."""
    raw  = ask_llm(get_prompt(problem_id))
    code = extract_code(raw)
    if not code:
        return {"code": "", "score": 0.0, "passed": 0, "total": 0}
    with open(SOLUTION_FILE, "w") as f:
        f.write(code)
    data = run_and_score(problem_id)
    return {
        "code":   code,
        "score":  data["score"],
        "passed": data["passed"],
        "total":  data["total"],
    }


# ── PHASE 2: Refiner (for multi-block solutions) ──────────────

def refine(problem_id: int, initial_code: str, initial_score: float) -> dict:
    """Run the ablation+refinement loop."""
    blocks = split_blocks(initial_code)
    block_names = [n for n in blocks if n != "_preamble"]

    if len(block_names) < 2:
        return {
            "code":    initial_code,
            "score":   initial_score,
            "skipped": True,
            "reason":  "single-block",
        }

    best_blocks = dict(blocks)
    best_score  = initial_score

    for round_num in range(1, REFINE_ROUNDS + 1):
        impacts = {}
        for name in block_names:
            ablated = dict(best_blocks)
            ablated[name] = stub_block(name, best_blocks[name])
            with open(SOLUTION_FILE, "w") as f:
                f.write(join_blocks(ablated))
            data = run_and_score(problem_id)
            impacts[name] = best_score - data["score"]
            time.sleep(1)

        ranked = sorted(impacts, key=lambda n: (-impacts[n], n))
        target = ranked[(round_num - 1) % len(ranked)]

        with open(SOLUTION_FILE, "w") as f:
            f.write(join_blocks(best_blocks))

        current_code = join_blocks(best_blocks)
        for i in range(1, NUM_VARIANTS + 1):
            prompt = (
                f"You are refining one component of a competitive "
                f"programming solution.\n\n"
                f"PROBLEM: {PROBLEMS[problem_id]['title']}\n"
                f"{PROBLEMS[problem_id]['description']}\n\n"
                f"CURRENT FULL SOLUTION:\n```python\n{current_code}\n```\n\n"
                f"YOUR TASK:\n"
                f"Rewrite ONLY the block labeled `# ── BLOCK: {target} ──`. "
                f"Keep the marker line. Do not modify other blocks.\n\n"
                f"OUTPUT: a single ```python block with just the new block "
                f"contents, starting with the marker line."
            )
            raw  = ask_llm(prompt)
            code = extract_code(raw)
            if not code:
                time.sleep(SLEEP_SECS)
                continue

            new_parts = split_blocks(code)
            if target not in new_parts:
                time.sleep(SLEEP_SECS)
                continue

            candidate = dict(best_blocks)
            candidate[target] = new_parts[target]
            with open(SOLUTION_FILE, "w") as f:
                f.write(join_blocks(candidate))
            data = run_and_score(problem_id)
            if data["score"] > best_score:
                best_score  = data["score"]
                best_blocks = candidate
            time.sleep(SLEEP_SECS)

        if best_score == 1.0:
            break

    with open(SOLUTION_FILE, "w") as f:
        f.write(join_blocks(best_blocks))

    return {
        "code":    join_blocks(best_blocks),
        "score":   best_score,
        "skipped": False,
    }


# ── PHASE 2b: Retry loop (for single-block solutions) ─────────

def retry_loop(problem_id: int, initial_code: str,
               initial_score: float) -> dict:
    """Whole-solution retry with TLE/WA feedback."""
    best_code, best_score = initial_code, initial_score

    for attempt in range(MAX_RETRIES):
        with open(SOLUTION_FILE, "w") as f:
            f.write(best_code)
        data = run_and_score(problem_id)
        if data["score"] == 1.0:
            return {"code": best_code, "score": 1.0, "skipped": False}

        feedback = build_feedback(data)
        prompt = get_prompt(problem_id) + (
            f"\n\nPREVIOUS ATTEMPT HAD ISSUES:\n{feedback}\n\n"
            "Output the corrected function in a single ```python block."
        )
        raw  = ask_llm(prompt)
        code = extract_code(raw)
        if not code:
            time.sleep(SLEEP_SECS)
            continue

        with open(SOLUTION_FILE, "w") as f:
            f.write(code)
        data = run_and_score(problem_id)
        if data["score"] > best_score:
            best_score = data["score"]
            best_code  = code
        time.sleep(SLEEP_SECS)

    return {"code": best_code, "score": best_score, "skipped": False}


# ── Report builders ───────────────────────────────────────────

def build_report_text(results: list) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append("  INTEGRATION REPORT — MLE-STAR Milestone 4")
    lines.append(f"  Generated: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"  Model: {MODEL}")
    lines.append("=" * 68)
    lines.append("")
    lines.append(f"  {'#':<3}  {'Problem':<22}  {'Coder':>6}  →  {'Final':>6}  "
                 f"{'Δ':>6}  {'Phase':<10}  {'Time':>6}")
    lines.append("  " + "-" * 64)

    for r in results:
        delta = r["final_score"] - r["initial_score"]
        delta_str = f"+{delta:.2f}" if delta > 0.005 else (
            "  0.00" if abs(delta) < 0.005 else f"{delta:+.2f}"
        )
        lines.append(
            f"  P{r['problem_id']:<2}  {r['title']:<22}  "
            f"{r['initial_score']:>5.2f}   →  {r['final_score']:>5.2f}  "
            f"{delta_str:>6}  {r['phase_used']:<10}  "
            f"{r['duration_seconds']:>5.0f}s"
        )

    lines.append("  " + "-" * 64)

    agg_init  = sum(r["initial_score"] for r in results) / len(results)
    agg_final = sum(r["final_score"] for r in results) / len(results)
    perfect   = sum(1 for r in results if r["final_score"] == 1.0)
    total_t   = sum(r["duration_seconds"] for r in results)

    lines.append("")
    lines.append(f"  Aggregate:        {agg_init:.3f}  →  {agg_final:.3f}")
    lines.append(f"  Problems at 1.00: {perfect} / {len(results)}")
    lines.append(f"  Total runtime:    {total_t:.0f}s ({total_t / 60:.1f} min)")
    lines.append("=" * 68)
    return "\n".join(lines)


def save_report(results: list, suite: list) -> None:
    agg_init  = sum(r["initial_score"] for r in results) / len(results)
    agg_final = sum(r["final_score"] for r in results) / len(results)
    perfect   = sum(1 for r in results if r["final_score"] == 1.0)

    report_json = {
        "suite":             suite,
        "results":           results,
        "aggregate_initial": round(agg_init, 3),
        "aggregate_final":   round(agg_final, 3),
        "perfect_count":     perfect,
        "total_problems":    len(results),
        "model":             MODEL,
        "timestamp":         datetime.datetime.now().isoformat(timespec="seconds"),
    }
    with open(REPORT_JSON_FILE, "w") as f:
        json.dump(report_json, f, indent=2)

    text = build_report_text(results)
    print("\n\n" + text)
    with open(REPORT_TEXT_FILE, "w") as f:
        f.write(text)

    print(f"\n  Saved → {REPORT_JSON_FILE}")
    print(f"  Saved → {REPORT_TEXT_FILE}")
