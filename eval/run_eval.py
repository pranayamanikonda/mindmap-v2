"""Week 1 initial capability check.

Runs draft -> research -> challenge end-to-end on a few sample topics and
prints the output, so you have concrete evidence of basic functionality
for the Week 1 submission (plus a place to jot what worked / didn't).

Run from the project root: python eval/run_eval.py
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agent import llm  # noqa: E402
from eval.topics import TEST_TOPICS  # noqa: E402

if __name__ == "__main__":
    for case in TEST_TOPICS:
        print("=" * 70)
        print("TOPIC:", case["topic"])

        draft = llm.draft_mind_map(case["topic"], case["goal"], case["constraints"])
        print("\n--- DRAFT ---\n" + draft)

        alternatives, sources, questions = llm.research_and_challenge(case["topic"], draft)
        print("\n--- RESEARCHED ALTERNATIVES ---\n" + alternatives)
        if sources:
            print("\nSources:")
            for s in sources:
                print(f"  - {s['title']}: {s['url']}")

        print("\n--- PROBING QUESTIONS ---")
        if questions:
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q}")
        else:
            print("  (none returned)")
        print()
