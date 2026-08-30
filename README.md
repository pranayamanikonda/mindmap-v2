# MindMap V2

A Streamlit chat + studio mind-map agent for a 3-week HCAI course. You give a topic; the agent drafts a map, runs a short research pass, asks probing questions, then refines the diagram.

Chat stays in the lead. Studio (the map) only appears once a draft exists.

- **Code:** https://github.com/pranayamanikonda/mindmap-v2
- **Live Cloud URL:** not published yet. If you deploy on Streamlit Community Cloud, the app needs a secret for the model — don’t use a leftover movies demo.

## Try it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Suggested path:** type “3-day Yosemite camping trip” → answer the goal prompt (or keep it short) → type `skip` on constraints if you want → wait for the draft and questions → answer in chat → rate the map in Studio. You can attach `.txt`, `.md`, `.csv`, or `.pdf` in the chat.

---

## Week 1 — Capability check

```
python eval/run_eval.py
```

Runs draft → research → challenge on three sample topics in `eval/topics.py` (fintech onboarding, energy storage, D2C launch). This is the basic “does the loop work?” evidence — it does not score quality.

---

## Week 2 — Who it’s for, and how the session is staged

**Target user.** Someone who needs a starting map for a messy brief — a trip, a launch, a research plan — and wants the agent to push back before they treat the diagram as finished. They are not looking for a source library or a fact-checked report.

**Need → what the product does**

- *I don’t know how to start the map* → staged chat: topic, then goal, then constraints, then a draft.
- *Don’t show me an empty studio* → Studio stays hidden until a draft exists. First screen is chat-only.
- *I have notes, not just a sentence* → attach files in chat; they become reference material for draft and refine.
- *I need to see and move the map* → Studio renders an interactive markmap (zoom − / Fit / +, pan). Drag the split between chat and Studio.
- *I shouldn’t trust this blindly* → a disclaimer under the title: drafts are a starting point, facts aren’t verified, unread files aren’t used, and the search pass can miss recent or niche sources.

**Mental model.** Chat is the conversation. Studio is the artifact. Sources are material you handed over, not a separate notebook. The first map is a draft on purpose — the interesting work is the challenge that comes after.

**How a session actually runs**

1. **Topic** — what to map, or a file plus a topic.
2. **Goal** — what you’re trying to accomplish.
3. **Constraints** — budget, timeline, etc. Type `skip` if none.
4. **Draft** — Studio opens with a nested-bullet mind map.
5. **Research + questions** — alternatives, optional source links, then 3–5 specific probing questions.
6. **Answers** — reply in chat, or say “use your best guess.”
7. **Final** — refined map in Studio, with a rating and optional comment.

You can start over from Studio or by typing “start over.”

**Files.** Supported types: `.txt`, `.md`, `.csv`, `.pdf`. Image-only PDFs say so instead of adding silence. If a map already exists, a new file updates that map. Attach before the first draft and the text is used when drafting starts.

---

## Week 3 — Challenge, trust marks, feedback, and failure

**Research and challenge.** After the draft, the agent searches for alternatives that are *not* already on the map, then writes questions aimed at a named gap or unstated assumption — not “what else could we add?” Answers (or a best-guess note) go into the refine step.

**Provenance on the final map.** Each branch gets a short tag — `[your input]`, `[research: …]`, `[challenge round]`, or `[assumed]` — plus `(H)` (well-established) or `(?)` (worth double-checking). The caption states these are the model’s own estimates, not verified facts.

**Validate before “done.”** The refined map is checked for a central topic, at least three branches, no empty branches, and short labels. If that check fails, you get a clarifying question and stay in the answers step. This is a **structure** check, not a fact check.

**Feedback.** On the final map: rate 1–5, optional comment, **Approve & log feedback**. Rows go to `eval/feedback_log.csv` (timestamp, topic, map, rating, comment).

**When things fail (honestly)**

- Missing model secret: the chat explains that the model isn’t configured (local setup or Cloud secret).
- Rate limit (429): the app retries on a lighter model (`gemini-3.6-flash` → `gemini-3.5-flash-lite`).
- Search rate limit: research still runs, but without live search grounding — alternatives may be thinner and source links may be empty.
- Any other model error: a message in chat; the step does not advance, so you can retry.

**Eval + try path.** Week 1’s `eval/run_eval.py` is still the scripted loop. For a human pass, use the Yosemite path above and log a rating. That covers draft, challenge, refine, validate, and feedback in one sitting.

**Known gaps (don’t overclaim)**

- Validate only checks shape and length — it will accept a tidy map that is wrong.
- Sending a **file and an answer in the same message** after a draft exists can apply the file and skip treating the text as answers.
- Cloud (when deployed) shares one model quota; search grounding may drop when that quota is exhausted.
- You cannot edit a single branch in Studio — only answer in chat, attach a source, or start over.
- There is no published MindMap V2 Cloud URL yet.
