# MindMap V2

Chat-first mind-map agent: you give a topic, it drafts a map, researches alternatives, asks probing questions, then refines the diagram. Built for a 3-week human-centered AI design brief (user needs, trust, feedback, error handling).

## Try it (evaluators)

- **Code:** https://github.com/pranayamanikonda/mindmap-v2
- **Live app:** Streamlit Community Cloud — after one GitHub sign-in, deploy `app.py` from `main` and add `GEMINI_API_KEY` in App settings → Secrets. Share the `*.streamlit.app` URL.
- **Eval deck:** `docs/MindMap-V2-Eval.pptx` (also `docs/MindMap-V2-Eval.html` — arrows or print to PDF)

Until the Cloud URL is live, run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste a Gemini key
streamlit run app.py
```

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

**Suggested try:** “3-day Yosemite camping trip” → skip goal/constraints if you want → answer the probing questions → rate the map. You can attach `.txt`, `.md`, `.csv`, or `.pdf` in the chat.

## Deploy (Streamlit Community Cloud)

The API key must **not** live in GitHub. After the repo is public:

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Deploy this repo, branch `main`, main file `app.py`.
3. App settings → Secrets:

```toml
GEMINI_API_KEY = "your-key-here"
```

Free-tier Gemini quota is shared by everyone using that key. If the app hits rate limits, it falls back to a lighter model; Search grounding may skip when quota is exhausted.

## How it maps to the flow

Studio (the mind map) stays hidden until a draft exists. Chat drives: topic → goal → constraints → probing answers → final. `app.py` `handle_user_input()` is the phase machine.

| File | Step |
|---|---|
| `agent/llm.py: draft_mind_map` | Draft initial mind map |
| `agent/llm.py: research_and_challenge` | Research & challenge (Google Search grounding + probing questions) |
| `app.py` (`await_answers` phase) | You respond in chat |
| `agent/llm.py: refine_mind_map` | Refine & finalize |
| `agent/llm.py: validate_map` | Validation / graceful failure fallback |
| `agent/feedback.py` | Rating + comment log |

## Week 1 capability check

```
python eval/run_eval.py
```

Runs draft → research → challenge on 3 sample topics in `eval/topics.py`.

## Notes

- Attach sources in chat (`.txt`, `.md`, `.csv`, `.pdf`). Text is extracted in `agent/file_ingest.py`. Image-only PDFs will say so instead of silently adding nothing. Unsupported types are blocked by the file picker.
- Maps render with [markmap.js](https://markmap.js.org) in an iframe (`agent/mindmap_render.py`). Zoom with − / Fit / +. The browser needs internet for the CDN scripts.
- Probing questions are JSON from `CHALLENGE_PROMPT`; answers are collected in chat.
- Validation (`llm.validate_map`) must return exactly `OK` or the app asks a clarifying question instead of showing a broken map.
- Feedback logs to `eval/feedback_log.csv` (created on first Approve).
- Models: `gemini-3.6-flash`, fallback `gemini-3.5-flash-lite` in `agent/config.py`.
