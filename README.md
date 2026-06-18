# MLE-STAR Agentic Solver Framework

This repository contains the curriculum, starter code, and documentation for the 8-week Competitive Programming Track. The primary objective of this course is to build an autonomous, agentic pipeline that solves algorithmic challenges using Large Language Models (LLMs).

The system reads a problem statement, generates a Python script, tests it against hidden test cases, parses the execution verdicts, and iteratively refines the code based on the failure logs.

## Table of Contents

* [Course Materials](#course-materials)
* [Information for Educators](#information-for-educators)
* [Information for Students](#information-for-students)
* [Course Architecture](#course-architecture)
* [Weekly Syllabus](#weekly-syllabus)
* [Setup and Installation](#setup-and-installation)

---

## Course Materials

The following course files and presentations are available in this repository:

* **Week 1:** [week1FromScriptstoSystems.pdf](./presentations/week1FromScriptstoSystems.pdf)
* **Week 2:** [week2FromStrategyToImplementati.pdf](./presentations/week2FromStrategyToImplementati.pdf)
* **Week 3:** [week3RunningTheMachine.pdf](./presentations/week3RunningTheMachine.pdf)
* **Week 4:** [week4Milestone1Coder.pdf](./presentations/week4Milestone1Coder.pdf)
* **Week 5:** [week5Milestone2Benchmark.pdf](./presentations/week5Milestone2Benchmark.pdf)
* **Week 6:** [week6Deck.pptx](./presentations/week6Deck.pptx)
* **Week 7:** [Week7_Deck.pptx](./presentations/Week7_Deck.pptx)
* **Week 8:** [Week8_Pipeline_Evaluation.pptx](./presentations/Week8_Pipeline_Evaluation.pptx)

---

## Information for Educators

This curriculum shifts the focus of competitive programming away from rote algorithm memorization and toward system orchestration. It is designed to train students for Forward Deployed Engineer roles by teaching them how to build evaluation frameworks, design feedback loops, and debug production failures.

**Grading and Evaluation:**
Students are evaluated on a 200-point scale split across two deliverables:

* **Live Presentation (100 pts):** A walkthrough of the system demonstrating one successful solve and one failure analysis.
* **Repository README (100 pts):** Graded on reproducibility, clarity, and honest reporting of success rates against a held-out dataset. Overfitting to visible test cases is strictly monitored, and honest failure analysis is rewarded.

---

## Information for Students

Your goal is to transform a simple prompt-response script into a robust, autonomous system. By the end of Week 8, your solver must be able to run independently from a clean clone and produce a verifiable integration report.

The pipeline operates on four primary verdicts:

| Verdict | Meaning | Action for the Loop |
| --- | --- | --- |
| **AC** | Accepted | All test cases passed; halt the loop. |
| **WA** | Wrong Answer | Fix logic or correct output formatting. |
| **TLE** | Time Limit Exceeded | Retain the approach but reduce time complexity. |
| **RE** | Runtime Error | Handle the crashing edge case. |

---

## Course Architecture

The framework is built across four major milestones. Each component passes typed results to the next, ensuring the system remains composable.

* **Milestone 1: Coder**
Injects the problem statement into a prompt template and extracts the generated Python code utilizing standard fencing.
* **Milestone 2: Benchmarker**
Executes the generated code in a subprocess against hidden cases with strict time limits. It branches the LLM feedback dynamically based on the exact failure type.
* **Milestone 3: Refiner**
Performs an ablation study by systematically stubbing marked code blocks to find bottlenecks. It then prompts the LLM for variants of the targeted block, splicing the best-performing variant back into the solution.
* **Milestone 4: Integration**
Wires the Coder, Benchmarker, and Refiner together. It outputs a comprehensive, self-contained run report detailing initial scores, final scores, and the specific phase that improved the result.

---

## Weekly Syllabus

| Week | Topic | Core Focus |
| --- | --- | --- |
| **1** | From Scripts to Systems | Building the Orchestrator loop and understanding sub-agent architecture. |
| **2** | Strategy to Implementation | Test-Driven Development and forcing structured output from the LLM. |
| **3** | Running the Machine | Establishing score-driven retries and injecting failure messages into subsequent prompts. |
| **4** | Milestone 1: Coder | Running the generation pipeline end-to-end on unseen problems. |
| **5** | Milestone 2: Benchmarker | Building the evaluation harness to categorize runtime and logic failures. |
| **6** | Milestone 3: Refiner | Implementing block-level ablation to optimize specific components of the code without regenerating the entire script. |
| **7** | Milestone 4: Integration | Composing all components to run autonomously and output a final integration report. |
| **8** | Demo Preparation | Stress-testing the loop against held-out cases, finalizing repository documentation, and presenting the findings[cite: 2]. |

---

## Setup and Installation

Follow these steps to configure the environment and run the pipeline locally.

1. Clone the repository and navigate to the project root directory.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Download and cache the problem dataset by running `python data/filter.py --download`.
4. Set your environment variables for offline execution to prevent HuggingFace timeout errors: `export HF_DATASETS_OFFLINE=1` and `export HF_HUB_OFFLINE=1`.
5. Export your required LLM API keys based on your chosen model.
6. Execute the solver on a single problem to view the verbose logs: `python solve.py --problem data/samples/example.json --verbose`.
7. Run the full batch evaluation to generate your final metrics: `python eval.py --split held_out --out results/held_out.json`.
