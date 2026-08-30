"""Prompt templates for the mind-map agent.

These map 1:1 onto the Week 1-3 design: draft -> research -> challenge ->
refine -> validate. Edit the wording here first if outputs need tuning --
these are the single source of truth the app and the eval script both use.

Draft/refine prompts explicitly request a nested markdown bullet list,
because that's what agent/mindmap_render.py feeds into markmap.js to draw
the actual node-and-branch diagram -- not just styling, the format matters.
"""

DRAFT_PROMPT = """You are drafting the first pass of a mind map.
Topic: {topic}
Goal: {goal}
Constraints: {constraints}

Reference material the user provided (use it where relevant, ignore
anything irrelevant, and don't invent content attributed to it that
isn't actually there):
{reference_material}

Output a markdown nested bullet list (use "-" at each level): 1 top-level
bullet as the central node, 4-6 second-level bullets as main branches
directly relevant to reaching the goal, 2-4 third-level bullets under each
branch. Every bullet's text under 8 words. Outline only -- no commentary,
no text before or after the list."""

RESEARCH_PROMPT = """Search for 3-5 alternative approaches, frameworks, or
options related to: {topic}, that are not already listed in this draft mind
map:

{draft}

Summarize each alternative in 1-2 sentences."""

CHALLENGE_PROMPT = """Given this draft mind map:
{draft}

And these research findings:
{search_results}

Write 3-5 probing questions that each target one specific, named gap or
unstated assumption in the draft, compared against the research findings.
No generic prompts like "what else could we add."

Respond with ONLY a JSON array of strings, one string per question, and
nothing else -- no markdown fences, no numbering, no commentary. Example:
["Question one?", "Question two?"]"""

REFINE_PROMPT = """Original draft mind map:
{draft}

Research findings and alternatives:
{alternatives}

Sources found:
{sources}

Reference material the user provided (use it where relevant, ignore
anything irrelevant, and don't invent content attributed to it that
isn't actually there):
{reference_material}

User's answers to the probing questions (or a note that none were given):
{user_answers}

Incorporate the user's answers (or your best-guess assumptions, clearly
marked) into an updated mind map. Output it as a markdown nested bullet
list in the same format as the original draft (1 top-level bullet as the
central node, second-level bullets as main branches, third-level bullets
as sub-points).

For every branch, append a short tag in brackets: [your input], [research:
source name], [challenge round], or [assumed]. Add a one-letter confidence
mark right after: (H) for well-established / high confidence, (?) for
worth double-checking. Keep each full bullet line, including its tag and
mark, under 14 words so it stays readable in a mind map viewer. After the
list, on its own line, state once, clearly, that these are the model's own
estimates, not verified facts."""

VALIDATE_PROMPT = """Topic: {topic}

Mind map to check:
{map_text}

Does it have a central topic, at least 3 main branches, and no empty
branches? Is every branch under 14 words?

If any check fails, or the topic was too vague to draft from, respond with
ONLY one clarifying question to ask the user -- do not repeat the map.
Otherwise, respond with exactly: OK"""
