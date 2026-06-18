# ============================================================
# problem_set.py
# ============================================================
# WEEK 7 — MILESTONE 4: INTEGRATION
#
# Usage:
#   Run integration_starter.py or integration_advanced.py
#   from inside the problemSet/ directory.
#
# NEW IN WEEK 7:
#   - Problem 9 (Brackets Balance) is added as a fresh end-to-end test.
#   - Problem 10 is reserved for a PEER-AUTHORED problem from another
#     team. Each team writes Problem 10 for the team next on the
#     rotation list. See the homework section in the TA guide.
#
# Problems 1–8 are retained unchanged.
# ============================================================

import random


# ── Helpers for Problem 9 ─────────────────────────────────────

def _make_brackets_cases():
    """
    Problem 9 hidden cases.
    Tests the classic bracket-matching problem with a TWIST:
    brackets inside string literals (single or double quoted) must
    be IGNORED. Most LLM-generated naive solutions miss this carve-out.
    """
    return [
        # --- Plain brackets, no strings ---
        ({"s": "()"},                  True,  1000, 64),
        ({"s": "()[]{}"},              True,  1000, 64),
        ({"s": "(]"},                  False, 1000, 64),
        ({"s": "([)]"},                False, 1000, 64),
        ({"s": "{[]}"},                True,  1000, 64),
        ({"s": ""},                    True,  1000, 64),    # empty = balanced
        # --- Brackets inside string literals — must be ignored ---
        ({"s": '"(("'},                True,  1000, 64),    # whole thing is in quotes
        ({"s": '"["'},                 True,  1000, 64),
        ({"s": "[\"(\"]"},             True,  1000, 64),    # [ then "(" then ]
        ({"s": "([\")\"])"},           True,  1000, 64),    # the ) is inside quotes
        # --- Mixed: real brackets AND string literals ---
        ({"s": "(\"hello\")"},         True,  1000, 64),
        ({"s": "['no )]\" closing'"},  False, 1000, 64),    # [ never closes
    ]


# ── Problem definitions ───────────────────────────────────────

PROBLEMS = {

    # ----------------------------------------------------------
    # Problems 1–8 retained (descriptions abbreviated)
    # ----------------------------------------------------------
    1: {
        "title": "Tram Stops",
        "description": """
A tram route has N stops 1..N in a circle. The tram travels clockwise.
Given [board, exit] pairs, return total clockwise distance.

Implement:
  def tram_distance(n: int, trips: list) -> int:
""",
        "examples": """
Example: tram_distance(5, [[1, 3], [4, 2]])  →  5
""",
        "hidden_cases": [
            ({"n": 5, "trips": [[1,3],[4,2],[3,3]]},   5,  5000, 256),
            ({"n": 4, "trips": [[4,1],[1,4]]},          4,  5000, 256),
            ({"n": 4, "trips": [[1,4]]},                3,  5000, 256),
            ({"n": 6, "trips": [[2,2],[3,3]]},          0,  5000, 256),
            ({"n": 10, "trips": [[1,10],[10,1]]},      10,  5000, 256),
            ({"n": 3, "trips": [[1,2],[2,3],[3,1]]},    3,  5000, 256),
            ({"n": 5, "trips": []},                     0,  5000, 256),
            ({"n": 1, "trips": [[1,1]]},                0,  5000, 256),
            ({"n": 8, "trips": [[3,7],[7,3]]},          8,  5000, 256),
            ({"n": 6, "trips": [[5,1],[6,2],[1,6]]},    9,  5000, 256),
        ]
    },

    2: {
        "title": "Inventory Manager",
        "description": """
Warehouse starts at 0. Positives restock, negatives sell.
Sale is rejected if it would go below 0.
Returns (final_stock, total_rejections).

Implement:
  def manage_inventory(transactions: list) -> tuple:
""",
        "examples": "Example: manage_inventory([10, -3, -15, 5, -4])  →  (8, 1)",
        "hidden_cases": [
            ({"transactions": [10, -3, -15, 5, -4]},   (8, 1),  5000, 256),
            ({"transactions": [5, -3, -3, -3]},         (2, 2),  5000, 256),
            ({"transactions": []},                       (0, 0),  5000, 256),
            ({"transactions": [-5]},                    (0, 1),  5000, 256),
            ({"transactions": [100]},                (100, 0),  5000, 256),
            ({"transactions": [3, -3, -1]},             (0, 1),  5000, 256),
            ({"transactions": [10, -5, -5, -5]},        (0, 1),  5000, 256),
            ({"transactions": [1, -1, 1, -1, 1]},       (1, 0),  5000, 256),
            ({"transactions": [-1, -1, 10, -3]},        (7, 2),  5000, 256),
            ({"transactions": [5, -2, -4, 3, -6]},      (0, 1),  5000, 256),
        ]
    },

    3: {
        "title": "Shift Decoder",
        "description": """
Each lowercase letter is shifted forward by its 1-based position
(non-letters pass through but count). Alphabet wraps. Decode.

Implement:
  def decode_message(encoded: str) -> str:
""",
        "examples": 'Example: decode_message("bdfhjl")  →  "abcdef"',
        "hidden_cases": [
            ({"encoded": "bdfhjl"},  "abcdef",  5000, 256),
            ({"encoded": "b c"},     "a z",     5000, 256),
            ({"encoded": ""},        "",        5000, 256),
            ({"encoded": "b"},       "a",       5000, 256),
            ({"encoded": "a"},       "z",       5000, 256),
            ({"encoded": "igopt"},   "hello",   5000, 256),
            ({"encoded": "dcw"},     "cat",     5000, 256),
            ({"encoded": "aqr"},     "zoo",     5000, 256),
            ({"encoded": "b1e"},     "a1b",     5000, 256),
            ({"encoded": "beh"},     "ace",     5000, 256),
        ]
    },

    4: {
        "title": "Compression Score",
        "description": """
For each run of identical chars, contribution = position(a=1) × length².

Implement:
  def compression_score(s: str) -> int:
""",
        "examples": 'Example: compression_score("aaabbc")  →  20',
        "hidden_cases": [
            ({"s": "aaabbc"},    20,   5000, 256),
            ({"s": "abc"},        6,   5000, 256),
            ({"s": ""},           0,   5000, 256),
            ({"s": "a"},          1,   5000, 256),
            ({"s": "z"},         26,   5000, 256),
            ({"s": "aaaaaa"},    36,   5000, 256),
            ({"s": "zz"},       104,   5000, 256),
            ({"s": "abba"},      10,   5000, 256),
            ({"s": "aabbccdd"},  40,   5000, 256),
            ({"s": "mmm"},      117,   5000, 256),
        ]
    },

    5: {
        "title": "Frequency Tag",
        "description": """
Replace each char with how many times it appears in the string.
Use 'X' for counts ≥ 10.

Implement:
  def frequency_tag(s: str) -> str:
""",
        "examples": 'Example: frequency_tag("aabbc")  →  "22221"',
        "hidden_cases": [
            ({"s": "aabbc"},      "22221",  2000, 64),
            ({"s": "abc"},        "111",    2000, 64),
            ({"s": "aaaa"},       "4444",   2000, 64),
            ({"s": ""},           "",       2000, 64),
            ({"s": "z"},          "1",      2000, 64),
            ({"s": "aaaaaaaaaaa"}, "XXXXXXXXXXX", 2000, 64),
            ({"s": "bbba"},       "3331",   2000, 64),
            ({"s": "ab"*50},      "XX"*50,  2000, 64),
            ({"s": "a"*15},       "X"*15,   2000, 64),
            ({"s": "abcdefghij"}, "1111111111", 2000, 64),
        ]
    },

    6: {
        "title": "First Occurrence Only",
        "description": """
Return integers in their order of first occurrence, each exactly once.

Implement:
  def first_occurrence_only(nums: list) -> list:
""",
        "examples": "Example: first_occurrence_only([1, 2, 1, 3, 2])  →  [1, 2, 3]",
        "hidden_cases": [
            ({"nums": [1, 2, 1, 3, 2]},      [1, 2, 3],      2000, 64),
            ({"nums": [4, 4, 4, 4]},          [4],            2000, 64),
            ({"nums": [1, 2, 3]},             [1, 2, 3],      2000, 64),
            ({"nums": []},                    [],             2000, 64),
            ({"nums": [7]},                   [7],            2000, 64),
            ({"nums": [3, 1, 2, 1, 3, 2]},   [3, 1, 2],      2000, 64),
            ({"nums": [0, 0, 1, 1, 2, 2]},   [0, 1, 2],      2000, 64),
            ({"nums": list(range(100))},      list(range(100)), 2000, 64),
            ({"nums": [5]*50},                [5],            2000, 64),
            ({"nums": [1,2,3,1,2,3,1,2,3]},   [1,2,3],        2000, 64),
        ]
    },

    7: {
        "title": "Log Triage",
        "description": """
Parse log lines, count by source, format as "source: count" pairs
in descending count order (alphabetical tiebreak).

Each line: TIMESTAMP LEVEL source: message

Solution should use 3 labeled blocks: parse, count, format.

Implement:
  def log_triage(log: str) -> str:
""",
        "examples": 'Example: log_triage("... INFO alpha: ok")  →  "alpha: 1"',
        "hidden_cases": [
            ({"log": "2026-05-24T12:00:00 INFO alpha: ok"},
             "alpha: 1", 2000, 64),
            ({"log": "2026-05-24T12:00:00 INFO alpha: ok\n"
                     "2026-05-24T12:00:01 WARN alpha: slow"},
             "alpha: 2", 2000, 64),
            ({"log": ""}, "", 2000, 64),
            ({"log": "2026-05-24T12:00:00 INFO charlie: x\n"
                     "2026-05-24T12:00:01 INFO bravo: y\n"
                     "2026-05-24T12:00:02 INFO alpha: z"},
             "alpha: 1, bravo: 1, charlie: 1", 2000, 64),
            ({"log": "2026-05-24T12:00:00 ERROR delta: bad\n"
                     "2026-05-24T12:00:01 ERROR delta: bad\n"
                     "2026-05-24T12:00:02 WARN gamma: meh\n"
                     "2026-05-24T12:00:03 INFO alpha: ok"},
             "delta: 2, alpha: 1, gamma: 1", 2000, 64),
            ({"log": "2026-05-24T12:00:00 INFO web-01: x\n"
                     "2026-05-24T12:00:01 WARN web-01: y\n"
                     "2026-05-24T12:00:02 INFO db-02: z"},
             "web-01: 2, db-02: 1", 2000, 64),
            ({"log": "\n".join(f"2026-05-24T12:00:0{i} INFO solo: msg" for i in range(5))},
             "solo: 5", 2000, 64),
            ({"log": "2026-05-24T12:00:00 INFO gamma: x\n"
                     "2026-05-24T12:00:01 INFO gamma: x\n"
                     "2026-05-24T12:00:02 INFO alpha: x"},
             "gamma: 2, alpha: 1", 2000, 64),
        ]
    },

    8: {
        "title": "Robot Walk",
        "description": """
Robot on a width × height grid starts at `start`. Follows N/S/E/W
commands. Off-grid moves are ignored. Return final [x, y].

Solution should use 3 blocks: bounds, move, walk.

Implement:
  def robot_walk(width: int, height: int, start: list, commands: str) -> list:
""",
        "examples": "Example: robot_walk(5, 5, [2, 2], \"ENWS\")  →  [2, 2]",
        "hidden_cases": [
            ({"width": 5, "height": 5, "start": [0, 0], "commands": "E"},
             [1, 0], 2000, 64),
            ({"width": 5, "height": 5, "start": [2, 2], "commands": "ENWS"},
             [2, 2], 2000, 64),
            ({"width": 3, "height": 3, "start": [1, 1], "commands": ""},
             [1, 1], 2000, 64),
            ({"width": 3, "height": 3, "start": [0, 0], "commands": "EEEEE"},
             [2, 0], 2000, 64),
            ({"width": 3, "height": 3, "start": [0, 0], "commands": "NNNNN"},
             [0, 2], 2000, 64),
            ({"width": 3, "height": 3, "start": [1, 1], "commands": "SSSS"},
             [1, 0], 2000, 64),
            ({"width": 3, "height": 3, "start": [1, 1], "commands": "WWWW"},
             [0, 1], 2000, 64),
            ({"width": 4, "height": 4, "start": [0, 0], "commands": "EENNW"},
             [1, 2], 2000, 64),
            ({"width": 10, "height": 10, "start": [5, 5],
              "commands": "EEEENNNNWWWWSSSS"}, [5, 5], 2000, 64),
            ({"width": 100, "height": 100, "start": [50, 50],
              "commands": "E"*30 + "N"*20 + "W"*10 + "S"*5},
             [70, 65], 2000, 64),
        ]
    },

    # ----------------------------------------------------------
    # Problem 9 — Brackets Balance  (NEW — Week 7)
    #
    # TA NOTE: This is the fresh end-to-end test for the integration.
    # Gemma 4 reliably produces a naive bracket-matching solution that
    # IGNORES the string-literal carve-out. About 6/12 cases pass on
    # attempt 1; cases involving strings fail until the Refiner
    # iterates. Good integration story:
    #
    #   Coder      → produces a "looks correct" solution
    #   Benchmarker → catches the string-literal failures
    #   Refiner    → identifies the bracket-tracking logic as broken,
    #                generates variants that handle quotes
    # ----------------------------------------------------------
    9: {
        "title": "Brackets Balance",
        "description": """
Given a string containing parentheses (), square brackets [], curly
braces {}, and possibly other characters, determine whether all the
brackets are properly matched and nested.

Brackets must match in type: ( pairs with ), [ with ], { with }.
Brackets must close in the correct order — ([)] is NOT balanced.

IMPORTANT RULE: brackets that appear inside string literals are
NOT counted. A string literal is anything between a pair of matching
double quotes (") or matching single quotes ('). For example:

  "(("   is balanced  (the parens are inside a string)
  ("x")  is balanced  (the parens are real, the "x" is a string)
  [")"]  is balanced  (the ) is inside the string)
  "[]"   is balanced  (everything is inside the string)

Return True if balanced, False otherwise. An empty string is balanced.

Implement:
  def is_balanced(s: str) -> bool:
""",
        "examples": """
Example 1:
  is_balanced("()[]{}")  →  True

Example 2:
  is_balanced("([)]")  →  False
  (closes in wrong order)

Example 3:
  is_balanced('("hello")')  →  True
  (the parens are real, hello is in a string)

Example 4:
  is_balanced('"(("')  →  True
  (all three parens are inside the string, so they don't count)

Example 5:
  is_balanced("(")  →  False
  (never closed)
""",
        "hidden_cases": _make_brackets_cases(),
    },

    # ----------------------------------------------------------
    # Problem 10 — Peer-authored (filled in by another team)
    # ----------------------------------------------------------
    # See problem_10_template.py — your team writes Problem 10 for the
    # team next on the rotation. Receiving team copies that file's
    # contents into the slot below.
    #
    # 10: { ... fill in from peer team ... },

}


def get_prompt(problem_id: int) -> str:
    """Build the full LLM prompt for a given problem."""
    p = PROBLEMS[problem_id]

    # Multi-block problems need the marker instruction
    extra = ""
    if problem_id in (7, 8):
        extra = (
            "\n- IMPORTANT: organise your solution into the labeled blocks "
            "shown in the description. Use comment lines of the form "
            "`# ── BLOCK: <name> ──` to mark the start of each block."
        )

    return f"""You are a competitive programming assistant.
Solve the following problem by implementing the specified function.

PROBLEM: {p['title']}
{p['description']}

EXAMPLES:
{p['examples']}

INSTRUCTIONS:
- Output a single ```python block containing ONLY the function implementation.
- Do not import any external libraries.
- Do not add explanations, test code, or main() calls.
- The function must match the signature exactly.{extra}
"""
