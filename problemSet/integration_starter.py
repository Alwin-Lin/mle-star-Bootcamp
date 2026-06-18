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
# Refiner helper functions are already imported and ready to use.
#
# Why this matters:
#   Up until now, your Coder/Benchmarker/Refiner have been three
#   separate scripts. Today they become ONE system. The lesson is
#   composition — how do these pieces pass state to each other?
#   What is the final artifact? That artifact is the report.
# ============================================================

import os
import re
import json
import time
import datetime
import subprocess
import google.generativeai as genai

from problem_set import PROBLEMS, get_prompt

# ── Configuration ─────────────────────────────────────────────
API_KEY      = os.environ.get("GEMINI_API_KEY", "YOUR_KEY_HERE")
MODEL        = "gemma-4-27b-it"
SLEEP_SECS   = 4
NUM_VARIANTS = 3
REFINE_ROUNDS = 2

# Which problems to run. Change to include problem 10 when you have
# your peer-authored problem.
SUITE = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Output files
REPORT_JSON_FILE = "integration_report.json"
REPORT_TEXT_FILE = "integration_report.txt"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL)

BLOCK_MARKER = re.compile(r"#\s*──\s*BLOCK:\s*(\w+)\s*──")


# ── Building blocks (provided — don't change these) ───────────

def ask_llm(prompt: str) -> str:
    return model.generate_content(prompt).text


def extract_code(raw: str) -> str:
    match = re.search(r"```python\s*(.*?)```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"(def \w+\(.*)", raw, re.DOTALL)
    return match.group(1).strip() if match else ""


def run_and_score(problem_id: int) -> dict:
    try:
        proc = subprocess.run(
            ["python", "run_cases.py", str(problem_id)],
            capture_output=True, text=True, timeout=120
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
    """Build a feedback message for the LLM based on failure types."""
    failures = data.get("failures", [])
    tle = [f for f in failures if f.get("reason") == "TLE"]
    wa  = [f for f in failures if f.get("reason") == "WA"]
    parts = []
    if tle:
        timing = "\n".join(
            f"  Case {f['case']}: {f['input_size']}, took {f['time_ms']} ms "
            f"(limit {f['limit_ms']} ms)"
            for f in tle[:3]
        )
        parts.append(f"TIME LIMIT EXCEEDED:\n{timing}\nUse a faster approach.")
    if wa:
        wa_lines = "\n".join(
            f"  Case {f['case']}: expected {f.get('expected')}, got {f.get('got')}"
            for f in wa[:3]
        )
        parts.append(f"WRONG ANSWER:\n{wa_lines}")
    return "\n\n".join(parts) if parts else "Unknown failure."


# ── PHASE 1: CODER ────────────────────────────────────────────

def coder(problem_id: int) -> dict:
    """Generate the initial solution. Returns {'code': str, 'score': float}."""
    raw  = ask_llm(get_prompt(problem_id))
    code = extract_code(raw)
    if not code:
        return {"code": "", "score": 0.0, "passed": 0, "total": 0}

    with open("solution.py", "w") as f:
        f.write(code)
    data = run_and_score(problem_id)
    return {
        "code":   code,
        "score":  data["score"],
        "passed": data["passed"],
        "total":  data["total"],
    }


# ── PHASE 2: REFINER ─────────────────────────────────────────

def refine(problem_id: int, initial_code: str, initial_score: float) -> dict:
    """
    Run the refiner on a problem. Returns the best code/score found.

    Skipped if the initial code has fewer than 2 blocks (refiner needs
    component boundaries to work with).
    """
    blocks = split_blocks(initial_code)
    block_names = [n for n in blocks if n != "_preamble"]

    if len(block_names) < 2:
        return {
            "code":    initial_code,
            "score":   initial_score,
            "skipped": True,
            "reason":  "single-block solution",
        }

    best_blocks = dict(blocks)
    best_score  = initial_score

    for round_num in range(1, REFINE_ROUNDS + 1):
        # Phase A — pick the target block (simple round-robin since
        # ablation often ties; see Week 6 notes)
        impacts = {}
        for name in block_names:
            ablated = dict(best_blocks)
            ablated[name] = stub_block(name, best_blocks[name])
            with open("solution.py", "w") as f:
                f.write(join_blocks(ablated))
            data = run_and_score(problem_id)
            impacts[name] = best_score - data["score"]
            time.sleep(1)

        target = sorted(impacts, key=lambda n: (-impacts[n], n))[
            (round_num - 1) % len(block_names)
        ]

        # Restore baseline
        with open("solution.py", "w") as f:
            f.write(join_blocks(best_blocks))

        # Phase B — generate K variants of the target block
        current_code = join_blocks(best_blocks)
        for i in range(1, NUM_VARIANTS + 1):
            prompt = (
                f"Refine ONE block of this solution.\n\n"
                f"PROBLEM: {PROBLEMS[problem_id]['title']}\n"
                f"{PROBLEMS[problem_id]['description']}\n\n"
                f"CURRENT SOLUTION:\n```python\n{current_code}\n```\n\n"
                f"Rewrite ONLY the `# ── BLOCK: {target} ──` block. "
                f"Output one ```python block with just the new block, "
                f"starting with its marker line."
            )
            raw  = ask_llm(prompt)
            code = extract_code(raw)
            new_parts = split_blocks(code)
            if target not in new_parts:
                time.sleep(SLEEP_SECS)
                continue

            candidate = dict(best_blocks)
            candidate[target] = new_parts[target]
            with open("solution.py", "w") as f:
                f.write(join_blocks(candidate))
            data = run_and_score(problem_id)
            if data["score"] > best_score:
                best_score  = data["score"]
                best_blocks = candidate
            time.sleep(SLEEP_SECS)

        if best_score == 1.0:
            break

    # Restore best version to disk
    with open("solution.py", "w") as f:
        f.write(join_blocks(best_blocks))

    return {
        "code":    join_blocks(best_blocks),
        "score":   best_score,
        "skipped": False,
    }


# ── PHASE 3: PER-PROBLEM RETRY (for single-block problems) ────

def retry_loop(problem_id: int, initial_code: str, initial_score: float,
                max_retries: int = 2) -> dict:
    """Simple feedback-retry loop for problems where the refiner is skipped."""
    best_code, best_score = initial_code, initial_score
    feedback = None

    for attempt in range(max_retries):
        # Get failures to build feedback from
        with open("solution.py", "w") as f:
            f.write(best_code)
        data = run_and_score(problem_id)
        if data["score"] == 1.0:
            return {"code": best_code, "score": 1.0, "skipped": False}

        feedback = build_feedback(data)
        prompt = get_prompt(problem_id) + (
            f"\n\nPREVIOUS ATTEMPT HAD ISSUES:\n{feedback}\n\n"
            "Output the corrected function in a ```python block."
        )
        raw = ask_llm(prompt)
        code = extract_code(raw)
        if not code:
            time.sleep(SLEEP_SECS)
            continue

        with open("solution.py", "w") as f:
            f.write(code)
        data = run_and_score(problem_id)
        if data["score"] > best_score:
            best_score = data["score"]
            best_code  = code
        time.sleep(SLEEP_SECS)

    return {"code": best_code, "score": best_score, "skipped": False}


# ════════════════════════════════════════════════════════════════
# INTEGRATION — THIS IS WHAT YOU IMPLEMENT
# ════════════════════════════════════════════════════════════════

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


# ── Report generation (provided) ──────────────────────────────

def build_report_text(results: list) -> str:
    """Format the results list as a human-readable text report."""
    lines = []
    lines.append("=" * 68)
    lines.append("  INTEGRATION REPORT — MLE-STAR Milestone 4")
    lines.append(f"  Generated: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"  Model: {MODEL}")
    lines.append("=" * 68)
    lines.append("")
    lines.append(f"  {'#':<3}  {'Problem':<22}  {'Coder':>6}  →  {'Final':>6}  "
                 f"{'Phase':<10}  {'Time':>6}")
    lines.append("  " + "-" * 64)
    for r in results:
        delta = r["final_score"] - r["initial_score"]
        delta_str = f"+{delta:.2f}" if delta > 0 else f" {delta:.2f}"
        lines.append(
            f"  P{r['problem_id']:<2}  {r['title']:<22}  "
            f"{r['initial_score']:>5.2f}   →  {r['final_score']:>5.2f} "
            f"{delta_str:>6}  {r['phase_used']:<10}  "
            f"{r['duration_seconds']:>5.0f}s"
        )
    lines.append("  " + "-" * 64)

    aggregate_initial = sum(r["initial_score"] for r in results) / len(results)
    aggregate_final   = sum(r["final_score"] for r in results) / len(results)
    perfect = sum(1 for r in results if r["final_score"] == 1.0)

    lines.append("")
    lines.append(f"  Aggregate (initial → final): "
                 f"{aggregate_initial:.2f} → {aggregate_final:.2f}")
    lines.append(f"  Problems at 1.00: {perfect} / {len(results)}")
    lines.append("=" * 68)
    return "\n".join(lines)


def save_report(results: list) -> None:
    """Save both JSON (for grading) and text (for humans) versions."""
    aggregate_final = sum(r["final_score"] for r in results) / len(results)
    perfect_count   = sum(1 for r in results if r["final_score"] == 1.0)

    report_json = {
        "suite":             SUITE,
        "results":           results,
        "aggregate_initial": round(
            sum(r["initial_score"] for r in results) / len(results), 3),
        "aggregate_final":   round(aggregate_final, 3),
        "perfect_count":     perfect_count,
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
        save_report(all_results)
    else:
        print("\n  No results to report. Fill in the TODOs in integrate_one().")
