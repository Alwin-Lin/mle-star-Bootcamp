# Instructor Handoff — MLE-STAR Architecture Course

**Course:** Agentic LLM Systems for High Schoolers (competitive-programming track)
**Duration:** 8 weeks, one 60-minute session per week
**Model:** Gemma 4 (`gemma-4-27b-it`) via the Gemini API, free tier
**Environment:** Google Colab (free)
**Prepared for:** the incoming instructor
**Prepared by:** Alwin Lin (outgoing)

---

## 1. What this course is

Students build an **agentic LLM system** that solves competitive-programming
problems on its own. The system has four components, introduced one per
milestone:

- **Coder** — generates a solution from a problem description
- **Benchmarker** — scores the solution against hidden tests, with time/memory limits
- **Refiner** — isolates the weakest part of a solution and improves only that
- **Integration** — wires all three into one pipeline that produces a report

The intellectual backbone is the **MLE-STAR paper** (Orchestrator + sub-agents,
ablation, iterative refinement). We translate that research into something a
high schooler can build and run in Colab.

**Why competitive programming and not ML?** The course originally targeted ML.
It was pivoted because competitive programming gives an *instant numeric
feedback loop* (`score = cases_passed / total`), needs no GPU, and lets us
write custom problems that avoid training-data contamination. That pivot is
load-bearing — don't undo it without understanding why.

---

## 2. The 8-week arc

| Week | Title | Milestone | What students build |
|---|---|---|---|
| 1 | The Agentic Loop | — | read → generate → write loop |
| 2 | Tool Use | — | LLM forced to write *testable* code |
| 3 | System Architecture | — | Orchestrator that runs tests via `subprocess` and retries on failure |
| 4 | Running the Machine | **M1: Coder** | full score-driven retry loop on an unseen problem |
| 5 | The Algorithms Bargain | **M2: Benchmarker** | time/memory measurement, TLE-aware feedback |
| 6 | The Surgical Loop | **M3: Refiner** | ablation + block-level refinement |
| 7 | From Parts to System | **M4: Integration** | end-to-end pipeline producing a report |
| 8 | Demo Day prep | — | rehearse and present the finished system |

Each week's session is lecture + hands-on. The actual demo is scheduled
separately, *after* Week 8.

---

## 3. What's in this package

This handoff covers the materials I built for **Weeks 5, 6, and 7** — the
middle third of the course. Weeks 1–4 and Week 8 exist as separate packages
(see Section 6).

### Slide decks
- `Week5_Deck.pptx` — 16 slides
- `Week6_Deck.pptx` — 12 slides
- `Week7_Deck.pptx` — 10 slides

All three share one visual theme: charcoal background (`0F0F12`), light
background (`F5F5F0`), orange accent (`FF5C28`), green (`5FB95F`), Georgia
headings, Consolas for code. If you build a Week 9 or revise a deck, match
this theme for continuity.

### TA / instructor guides
- `week5_ta_guide.md` — lecture-driven session (algorithms + career framing)
- `week6_ta_guide.md` — ablation + the honest-limitation discussion
- `week7_ta_guide.md` — integration + the peer-authoring homework

These are written for a TA to teach from cold. They include timing tables
cross-referenced to slides, segment-by-segment talking points, circulating-help
tables, common problems, and grading rubrics.

### Student code — problem sets and harnesses
- `problem_set_week5.py` / `run_cases_week5.py` — adds Problems 5–6 (performance traps)
- `problem_set_week6.py` / `run_cases_week6.py` — adds Problems 7–8 (multi-block solutions)
- `problem_set_week7.py` / `run_cases_week7.py` — adds Problem 9 (Brackets Balance) + Problem 10 slot

### Student code — milestone scaffolds
Each milestone ships a `*_starter.py` (with TODOs) and a `*_advanced.py`
(complete reference):
- `benchmark_starter.py` / `benchmark_advanced.py` (Week 5)
- `refiner_starter.py` / `refiner_advanced.py` (Week 6)
- `integration_starter.py` / `integration_advanced.py` (Week 7)

### Week 7 peer-authoring homework
- `problem_10_template.py` — fill-in template for a student-authored problem
- `author_a_problem.md` — guide for writing a good problem for another team

---

## 4. How the pieces fit together (mental model)

Students keep two files constant across the whole course and swap problem sets
as the weeks progress:

- They rename `problem_set_weekN.py` → `problem_set.py`
- They rename `run_cases_weekN.py` → `run_cases.py`
- Their orchestrator imports from those two names

`run_cases.py` is the **harness**: it imports the LLM-generated `solution.py`,
runs the hidden test cases, and prints a JSON score. It runs as a subprocess so
a crash in generated code can't take down the orchestrator. From Week 5 on it
also measures time (`perf_counter`) and memory (`tracemalloc`) and classifies
each case as AC / TLE / MLE / WA / RE.

The milestone scripts (benchmark / refiner / integration) sit *above* the
harness and call it. Each milestone adds one capability without rewriting what
came before.

---

## 5. Week-by-week notes for the new instructor

### Week 5 — The Algorithms Bargain (Benchmarker)

This is the most unusual session in the course. It is **lecture-driven, not
debug-driven**. The arc: teach what a CS degree covers → hand students two
LeetCode mediums to attempt by hand → reveal that Gemma 4 solves them in
seconds → reframe the moment around the Forward Deployed Engineer role and the
changing hiring landscape (Anthropic FDE postings, Google allowing AI in
interviews).

The Benchmarker milestone itself (TLE-aware feedback) is the hands-on portion.
The key engineering idea: **the feedback you send the LLM must differ by failure
type** — a TLE message ("correct but slow") is different from a WA message
("wrong answer").

### Week 6 — The Surgical Loop (Refiner)

Concept: **ablation** — change one component, measure the score impact, refine
only the part that matters. This maps directly onto the MLE-STAR paper's
ablation study (panel b in the paper figure).

We deliberately use a **simplified version** of the paper's method:
- The paper parses the AST to find components. Fragile to LLM output quirks.
- We have the LLM label its own blocks with `# ── BLOCK: name ──` markers and
  splice on those. Less rigorous, far more robust.

**Teach the limitation honestly.** There's a dedicated slide for it. When you
stub a block with `pass`, the variable it produced vanishes and the whole
solution scores 0, so ablation often can't discriminate between blocks. The
refiner falls back to round-robin block selection. This is a real weakness and
students should hear it named.

### Week 7 — From Parts to System (Integration)

Concept: **composition** — the four components become one pipeline. The headline
deliverable is a **report** (`integration_report.json` + `.txt`), not terminal
output. This ties back to the FDE framing: engineers ship reports, not console
logs.

Problem 9 (Brackets Balance) is the fresh end-to-end test. It has a deliberate
trap — brackets inside string literals must be ignored — which Gemma 4 reliably
misses on the first attempt (scores ~8/12), giving the integration something to
fix.

The **peer-authoring homework** is the distinctive part: each team writes
Problem 10 for the *next team in a rotation* (odd team count → clean cycle). This
teaches the FDE skill of specifying a problem clearly for someone else. Authoring
happens between Weeks 7 and 8.

---

## 6. What lives outside this package

- **Weeks 1–4** — earlier materials. The Week 3 package (look for the "Week 3
  class timetable" materials) is a good model for the format of the early weeks:
  TA guide + problem set + run_cases + starter/advanced tracks. Weeks 1–4
  introduce the agentic loop, tool use, the subprocess retry mechanism, and
  Milestone 1.
- **Week 8 — Demo Day prep** — built separately. It's a coaching/rehearsal
  session, not concept-heavy. Students present their integrated pipeline and the
  problem they authored. There's a TA guide and a student presentation outline
  (8-minute structure: system demo → authored problem → one interesting pipeline
  moment → one concrete thing they'd change).
- **The LiveBench stress-test harness** — `run_eval.py`, `lcb_loader.py`,
  `select_hard.py`. This is an *optional* extension that runs the students'
  pipeline against real hard problems from LiveCodeBench. See Section 8.

---

## 7. Known weak spots / what I'd change next round

Candid list. None of these are blockers, but they're where I'd spend the
optimization time.

**Week 5 problems are getting too easy for the model.** Problems 5–6 were
designed to trap Gemma 4 into O(n²) Python idioms (`s.count()` in a loop,
`x in list`). Newer Gemma 4 checkpoints increasingly write the efficient
version unprompted — it even includes complexity analysis. The lecture/career
framing carries the session regardless, but if the live "watch it TLE" demo
stops firing, lean harder into the framing and treat the benchmarker as
"prove your system works" rather than "watch it fail and recover."

**Week 6 ablation doesn't discriminate well.** Covered above. The honest fix is
the paper's approach: replace each block with a *degraded-but-functional*
baseline instead of `pass`. That requires knowing what each block outputs. A
motivated successor could build this and it would make the ablation visibly
meaningful. Until then, the round-robin fallback is fine and we teach the
limitation.

**Gemma 4 sometimes ignores the BLOCK marker instruction.** When it does, the
Week 6 refiner and Week 7 integration fall back to whole-solution retry. The
code handles this gracefully, but if markers fail often, add a one-shot example
of the marker format to the prompt — showing the format before asking for it
reliably fixes compliance.

**The LiveBench stress test is only half-wired.** The harness files are present
and the loader handles the dataset's quirks (difficulty/starter_code nested in
`original_json`, private tests as base64→zlib→pickle), but it's not integrated
into a graded week. It's a strong optional extension — see Section 8.

**Runtime anxiety in Week 7.** The integration takes 15–25 minutes to run on 9
problems because of API rate limits. Students panic and hit Ctrl+C. The deck and
guide both warn about this, but consider a "quick mode" (cap at 3 problems) for
in-class runs so students see a full report fast, then run the full suite as
homework.

---

## 8. The LiveBench stress-test extension (optional)

Three files let students run their pipeline against real hard problems from the
LiveCodeBench dataset:

- `lcb_loader.py` — loads and normalises `question.jsonl`. Handles the schema
  quirks: `difficulty`, `starter_code`, and `fn_name` live inside
  `original_json`; `private_test_cases` are `base64(zlib(pickle(...)))`.
- `select_hard.py` — picks the N hardest problems and writes `hard_subset.jsonl`.
- `run_eval.py` — runs each problem through a pluggable `generate()` hook and
  scores it (a problem is solved only if *every* test passes — the LiveBench rule).

The single integration point is the `generate(prompt)` function in `run_eval.py`.
Swap its body for a call into the students' orchestrator (`return
orchestrator.solve(prompt)`) and their whole pipeline gets measured against
genuinely hard problems.

**Two things to watch** (learned the hard way):
- **Interactive problems** (e.g. "Bad Juice") are incompatible with static
  stdin/stdout grading — they need a live two-way judge. Filter them out with a
  string check on the problem statement.
- **Trailing whitespace** causes false-negative test failures. The harness
  normalises whitespace; keep that.

This would make a strong Week 9 or an honors extension. The lesson — "watch your
system get humbled by olympiad-grade problems" — is a powerful counterpoint to
the Week 5 "the LLM is amazing" framing.

---

## 9. Practical setup

**Build pipeline for decks** (if you edit them):
```
NODE_PATH=/home/claude/.npm-global/lib/node_modules node build_deck.js
```
QA by converting to PDF and rasterizing:
```
soffice --headless --convert-to pdf Week5_Deck.pptx
pdftoppm -jpeg -r 100 Week5_Deck.pdf slide
```
Then eyeball every slide. Watch for the box-drawing dashes in `── BLOCK ──`
markers — they render as a single em-dash in the JPEG QA but display correctly
in actual PowerPoint. Cosmetic only.

**Student environment:**
```python
!pip install google-generativeai
import os
os.environ["GEMINI_API_KEY"] = "your-key-here"
```
Then upload the week's files to the Colab session.

**Grading rubric** (consistent across all milestones, 100 pts):

| Category | Points |
|---|---|
| System Architecture | 20 |
| Autonomous Loop | 30 |
| Task Correctness | 20 |
| Robustness | 15 |
| Presentation | 15 |

The Week 7 peer-authored problem is graded separately (25 pts; rubric in
`author_a_problem.md`).

---

## 10. The one thing to preserve

Across every week, the grading philosophy is: **the machinery is graded, not
whether the LLM happens to fail or improve.** Modern models often score high on
these problems — that's fine. A student whose pipeline works perfectly and whose
LLM aced everything on the first try still earns full marks. The course teaches
*how to build the system*, not *how to make the model struggle*.

If you remember nothing else from this handoff, remember that. It's the most
common thing a new TA gets wrong — marking down a student because "the refiner
didn't improve anything," when the refiner worked perfectly and there was simply
nothing to improve.

---

*Questions about anything here: the TA guides go deeper on each week, and the
`*_advanced.py` reference implementations show exactly what a complete milestone
looks like.*
