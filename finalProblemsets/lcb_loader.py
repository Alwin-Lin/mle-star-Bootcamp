"""
lcb_loader.py
-------------
Loads the LiveBench *coding* questions you pulled from HuggingFace and
normalizes every problem into one simple dict shape, regardless of how the
test cases happen to be encoded in the file.

LiveBench wraps LiveCodeBench problems. Depending on the exact dump, the
private test cases are stored either as plain JSON or as base64(zlib(json)).
This loader handles both so the rest of the pipeline never has to care.

Normalized problem shape:
{
    "question_id":  str,
    "title":        str,
    "prompt":       str,    # the full natural-language problem statement
    "difficulty":   str,    # "easy" | "medium" | "hard" (lowercased)
    "task":         str,    # "code_generation" | "code_completion"
    "starter_code": str,    # "" for stdin problems, non-empty for functional
    "fn_name":      str|None,# function name for functional (LeetCode) problems
    "tests":        [ {"input": str, "output": str, "testtype": str}, ... ],
    "partial":      str,    # only for code_completion: the partial solution
}
"""

import json
import base64
import zlib
import pickle


def _decode_tests(raw):
    """Return a list of test dicts from whatever encoding `raw` is in."""
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        return raw
    # Try plain JSON first.
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Fall back to the LiveCodeBench compressed encoding:
    # base64 -> zlib -> pickle -> json string -> list.
    try:
        decoded = pickle.loads(zlib.decompress(base64.b64decode(raw.encode("utf-8"))))
        if isinstance(decoded, str):
            return json.loads(decoded)
        return decoded
    except Exception as e:
        raise ValueError(f"Could not decode test cases: {e}")


def _get(d, *keys, default=None):
    """Return the first present key (handles schema drift between dumps)."""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _extract_prompt(q):
    """The statement lives in `turns` (a list) in LiveBench, or `question_content`."""
    turns = q.get("turns")
    if isinstance(turns, list) and turns:
        return "\n".join(str(t) for t in turns)
    return _get(q, "question_content", "prompt", "question", default="")


def load_problems(path):
    """Read a LiveBench coding question.jsonl and yield normalized problems."""
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                q = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  [warn] skipping malformed line {line_no}: {e}")
                continue

            # difficulty sometimes lives inside a "metadata" JSON string
            difficulty = _get(q, "difficulty")
            fn_name = None
            meta_raw = q.get("metadata")
            if meta_raw:
                try:
                    meta = meta_raw if isinstance(meta_raw, dict) else json.loads(meta_raw)
                    difficulty = difficulty or meta.get("difficulty")
                    fn_name = meta.get("func_name") or meta.get("fn_name")
                except Exception:
                    pass

            public = _decode_tests(_get(q, "public_test_cases"))
            private = _decode_tests(_get(q, "private_test_cases"))

            problems.append({
                "question_id": str(_get(q, "question_id", "id", default=f"line{line_no}")),
                "title": _get(q, "question_title", "title", default="(untitled)"),
                "prompt": _extract_prompt(q),
                "difficulty": (difficulty or "unknown").lower(),
                "task": _get(q, "task", default="code_generation"),
                "starter_code": _get(q, "starter_code", default="") or "",
                "fn_name": fn_name,
                "tests": list(public) + list(private),
                "partial": _get(q, "partial_solution", default="") or "",
            })
    return problems


if __name__ == "__main__":
    # Quick sanity check: python lcb_loader.py path/to/question.jsonl
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "question.jsonl"
    probs = load_problems(p)
    print(f"Loaded {len(probs)} problems")
    from collections import Counter
    print("By difficulty:", dict(Counter(x["difficulty"] for x in probs)))
    print("By task:", dict(Counter(x["task"] for x in probs)))
    if probs:
        ex = probs[0]
        print(f"\nExample: {ex['title']} [{ex['difficulty']}] "
              f"task={ex['task']} tests={len(ex['tests'])} fn={ex['fn_name']}")
