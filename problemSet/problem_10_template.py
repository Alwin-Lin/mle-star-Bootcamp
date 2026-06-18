# ============================================================
# problem_10_template.py — Peer-authored Problem 10 template
# ============================================================
# Each team writes Problem 10 for the next team on the rotation.
#
# HOW TO USE:
#   1. Fill in the dict below with your problem.
#   2. Hand this file to the receiving team.
#   3. Receiving team copies the dict into the  10: { ... }  slot
#      in problem_set.py.
#   4. Validate: python run_cases.py 10  against a correct solution.py
#      should print  "score": 1.0
#
# FIELD REFERENCE:
#   title          — short name shown in the integration report
#   description    — full problem statement + function signature
#                    (injected verbatim into the LLM prompt)
#   examples       — 1-2 worked examples the LLM can study
#   function_name  — the exact Python function the solution must define;
#                    run_cases.py uses this for dynamic dispatch on p.10
#   hidden_cases   — list of 4-tuples:
#                      (args_dict, expected, time_limit_ms, memory_limit_mb)
# ============================================================

PROBLEM_10 = {

    # ── Title ─────────────────────────────────────────────────
    "title": "Even Sum",

    # ── Problem statement ─────────────────────────────────────
    "description": """\
Given a list of integers, return the sum of all even numbers.
If there are no even numbers, return 0.

Implement:
  def even_sum(nums: list) -> int:
""",

    # ── Worked examples ───────────────────────────────────────
    "examples": """\
Example 1:
  even_sum([1, 2, 3, 4, 5])  →  6   (2 + 4)

Example 2:
  even_sum([1, 3, 5])  →  0   (no even numbers)
""",

    # ── Function name (must match the signature above exactly) ─
    "function_name": "even_sum",

    # ── Hidden test cases ─────────────────────────────────────
    # Each 4-tuple: (args_dict, expected, time_limit_ms, memory_limit_mb)
    # args_dict keys must match the function's parameter names.
    "hidden_cases": [
        ({"nums": [1, 2, 3, 4, 5]},            6,   2000, 64),   # basic mix
        ({"nums": [2, 4, 6, 8]},               20,   2000, 64),   # all even
        ({"nums": [1, 3, 5, 7]},                0,   2000, 64),   # all odd
        ({"nums": []},                          0,   2000, 64),   # empty list
        ({"nums": [0]},                         0,   2000, 64),   # zero is even
        ({"nums": [-2, -4, 1]},                -6,   2000, 64),   # negative evens
        ({"nums": [1_000_000, 999_999]},  1_000_000, 2000, 64),  # large value
        ({"nums": list(range(1, 101))},      2550,   2000, 64),   # 1..100, even sum
    ],
}
