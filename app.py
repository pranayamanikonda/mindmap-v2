import streamlit as st

from agent import feedback, file_ingest, llm
from agent.mindmap_render import render_mindmap

st.set_page_config(page_title="MindMap V2", page_icon=":world_map:", layout="wide")

_CSS_SHARED = """
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;500;600&display=swap");

html, body, [class*="css"] { font-family: "Source Sans 3", sans-serif; }
.stApp { background: #f3eee6; }
header[data-testid="stHeader"] { background: transparent; }
h1 {
  font-family: "Fraunces", Georgia, serif !important;
  font-size: 2rem !important;
  font-weight: 600 !important;
  letter-spacing: -0.03em;
  color: #1c1917 !important;
  margin-bottom: 0.15rem !important;
}
h3 { font-size: 0.82rem !important; font-weight: 600 !important; letter-spacing: 0.08em; text-transform: uppercase; color: #57534e !important; }
.welcome-title {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.7rem; font-weight: 500; color: #1c1917;
  margin: 1.6rem 0 0.4rem; letter-spacing: -0.03em;
}
.welcome-sub { color: #57534e; font-size: 1.02rem; line-height: 1.5; margin-bottom: 1.2rem; }
.source-count { color: #57534e; font-size: 0.82rem; }
.studio-tile {
  display: inline-flex; align-items: center; gap: 8px;
  background: #ecfdf5; color: #115e59;
  border: 1px solid #99f6e4; border-radius: 999px;
  padding: 8px 14px; font-size: 0.8rem; font-weight: 600;
  letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 12px;
}
.studio-tile svg { display: block; }
div[data-testid="stChatInput"] {
  background: #fffaf4; border: 1px solid #d6d3d1; border-radius: 28px; padding: 4px 8px;
}
button[kind="secondary"] {
  border-radius: 999px !important;
  border: 1px solid #d6d3d1 !important;
  background: #fffaf4 !important;
  color: #1c1917 !important;
  min-height: 44px !important;
  padding: 0.45rem 1rem !important;
}
@media (prefers-reduced-motion: reduce) {
  .studio-shell,
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child > div {
    animation: none !important;
  }
}
"""

_CSS_SOLO = _CSS_SHARED + """
.block-container {
  padding-top: 2.4rem; padding-bottom: 1.6rem;
  max-width: 740px;
  background: #fffaf4;
  border-radius: 28px;
  box-shadow: 0 1px 2px rgba(28, 25, 23, 0.06), 0 12px 32px rgba(28, 25, 23, 0.04);
}
"""

_CSS_SPLIT = _CSS_SHARED + """
.block-container { padding-top: 1.1rem; padding-bottom: 1.4rem; max-width: 1480px; }
div[data-testid="stHorizontalBlock"] { gap: 0 !important; position: relative; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  min-width: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child > div {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child > div {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {
  background: #fffaf4;
  border-radius: 20px;
  padding: 16px 14px 10px;
  box-shadow: 0 1px 2px rgba(28, 25, 23, 0.06), 0 12px 32px rgba(28, 25, 23, 0.04);
  min-height: 78vh;
}
div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] > div {
  background: transparent; box-shadow: none; padding: 0; min-height: 0; border-radius: 0;
}
div[data-testid="stIFrame"] iframe { overflow: hidden !important; }
.studio-shell { animation: studio-in 280ms cubic-bezier(0.2, 0, 0, 1); }
@keyframes studio-in {
  from { opacity: 0; transform: translateX(18px); }
  to { opacity: 1; transform: none; }
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child > div {
  animation: studio-in 280ms cubic-bezier(0.2, 0, 0, 1);
}
.mm-split-handle {
  position: absolute;
  top: 0; bottom: 0;
  width: 12px;
  margin-left: -6px;
  cursor: col-resize;
  z-index: 30;
  touch-action: none;
}
.mm-split-handle::before {
  content: "";
  position: absolute;
  top: 16%; bottom: 16%;
  left: 5px;
  width: 2px;
  border-radius: 2px;
  background: #d6d3d1;
}
.mm-split-handle:hover::before,
.mm-split-handle:focus-visible::before { background: #0f766e; }
.mm-split-handle:focus-visible { outline: none; }
@media (prefers-reduced-motion: reduce) {
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child > div {
    animation: none !important;
  }
}
"""

STUDIO_LABEL = """
<div class="studio-tile" role="status">
  <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="none">
    <circle cx="8" cy="3" r="2" fill="currentColor"/>
    <circle cx="3" cy="12" r="2" fill="currentColor"/>
    <circle cx="13" cy="12" r="2" fill="currentColor"/>
    <path d="M8 5v3M8 8L3.5 11M8 8l4.5 3" stroke="currentColor" stroke-width="1.4"/>
  </svg>
  Mind map
</div>
"""

SUGGESTIONS = [
    "10-day trip to Singapore",
    "Launch strategy for a D2C skincare brand",
    "Research plan for renewable energy storage",
]

DISCLAIMER = (
    "Drafts a starting mind map and challenges it with a quick research pass. "
    "It doesn't verify facts, can't see documents you haven't pasted in, and "
    "its search pass may miss recent or niche sources."
)


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.phase = "await_topic"
        st.session_state.uploaded_sources = {}
        add_message(
            "assistant",
            "What should we map? Give me a **topic**, or attach a source "
            "(.txt, .md, .csv, .pdf) and I’ll use it once we start drafting.",
        )


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def combined_reference_material() -> str:
    sources = st.session_state.get("uploaded_sources", {})
    if not sources:
        return ""
    parts = []
    for name, text in sources.items():
        snippet = text if len(text) <= 6000 else text[:6000] + "\n...[truncated]"
        parts.append(f"### {name}\n{snippet}")
    return "\n\n".join(parts)


def reset_conversation() -> None:
    for key in (
        "messages", "phase", "topic", "goal", "constraints", "uploaded_sources",
        "draft", "alternatives", "sources", "questions", "answers", "refined",
    ):
        st.session_state.pop(key, None)


def submit(text: str, files=None) -> None:
    """Handles one user turn, then reruns so the chat history redraws with
    the new messages before the next input is accepted."""
    handle_user_input((text or "").strip(), files)
    st.rerun()


def handle_user_input(text: str, files=None) -> None:
    files = files or []

    new_source_names = []
    for f in files:
        st.session_state.uploaded_sources[f.name] = file_ingest.extract_text(f)
        new_source_names.append(f.name)

    if text:
        add_message("user", text)
    elif new_source_names:
        add_message("user", f"📎 Attached: {', '.join(new_source_names)}")
    else:
        return  # nothing was actually submitted

    try:
        # A new source landing after a map already exists should visibly
        # change that map -- otherwise attaching a file does nothing the
        # user can see, which defeats the point of adding it.
        if new_source_names and st.session_state.get("draft"):
            with st.spinner("Updating the mind map with the new source..."):
                refined = llm.refine_mind_map(
                    st.session_state.draft,
                    st.session_state.get("answers", ""),
                    st.session_state.get("alternatives", ""),
                    st.session_state.get("sources", []),
                    reference_material=combined_reference_material(),
                )
                check = llm.validate_map(refined, st.session_state.topic)
            if check == "OK":
                st.session_state.refined = refined
                st.session_state.phase = "final"
                add_message("assistant", "Updated the mind map on the right to reflect the new source.")
            else:
                add_message("assistant", check)
                st.session_state.phase = "await_answers"
        elif new_source_names:
            add_message(
                "assistant",
                f"Added {', '.join(new_source_names)} as source material — "
                "I'll use it once we start drafting.",
            )

        if not text:
            return

        phase = st.session_state.phase  # re-read: may have just changed above

        if phase == "await_topic":
            st.session_state.topic = text
            add_message(
                "assistant",
                "Got it. What's your main goal here — what are you trying to accomplish?",
            )
            st.session_state.phase = "await_goal"

        elif phase == "await_goal":
            st.session_state.goal = text
            add_message(
                "assistant",
                "Any constraints I should know about (budget, timeline, etc)? "
                "Type \"skip\" if none.",
            )
            st.session_state.phase = "await_constraints"

        elif phase == "await_constraints":
            st.session_state.constraints = "" if text.lower() == "skip" else text
            with st.spinner("Drafting..."):
                st.session_state.draft = llm.draft_mind_map(
                    st.session_state.topic,
                    st.session_state.goal,
                    st.session_state.constraints,
                    reference_material=combined_reference_material(),
                )
            add_message(
                "assistant",
                "Here's a first draft — check the mind map on the right. "
                "Now let me look into some alternatives and angles you might be missing...",
            )
            with st.spinner("Researching..."):
                alternatives, sources, questions = llm.research_and_challenge(
                    st.session_state.topic, st.session_state.draft
                )
            st.session_state.update(alternatives=alternatives, sources=sources, questions=questions)
            q_text = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions)) or "(none this round)"
            links = ""
            if sources:
                links = "\n\nSources: " + ", ".join(f"[{s['title']}]({s['url']})" for s in sources)
            add_message(
                "assistant",
                f"Here's what I found:\n\n{alternatives}{links}\n\n"
                f"**A few questions to sharpen this:**\n\n{q_text}\n\n"
                "Answer any you have a view on, or just say \"use your best guess.\"",
            )
            st.session_state.phase = "await_answers"

        elif phase == "await_answers":
            prior = st.session_state.get("answers", "")
            st.session_state.answers = (prior + "\n" + text).strip()
            with st.spinner("Refining..."):
                refined = llm.refine_mind_map(
                    st.session_state.draft,
                    st.session_state.answers,
                    st.session_state.alternatives,
                    st.session_state.sources,
                    reference_material=combined_reference_material(),
                )
                check = llm.validate_map(refined, st.session_state.topic)
            if check != "OK":
                add_message("assistant", check)  # stay in await_answers, loop
            else:
                st.session_state.refined = refined
                add_message(
                    "assistant",
                    "Done — the refined map is on the right. Rate it there, "
                    "or type \"start over\" for a new topic.",
                )
                st.session_state.phase = "final"

        elif phase == "final":
            if text.lower() in ("start over", "restart", "new topic"):
                reset_conversation()
            else:
                add_message(
                    "assistant",
                    "Noted. You can rate the map on the right, or type "
                    "\"start over\" for a new topic.",
                )
    except Exception as e:
        add_message(
            "assistant",
            f"Something went wrong talking to the model: {e}. You can try that again.",
        )
        # Phase intentionally left unchanged so the same input can be retried.


def render_chat(n_sources: int, map_ready: bool) -> None:
    head_l, head_r = st.columns([0.72, 0.28])
    with head_l:
        st.subheader("Chat")
    with head_r:
        label = "1 source" if n_sources == 1 else f"{n_sources} sources"
        st.markdown(
            f'<p class="source-count" style="text-align:right;margin-top:0.4rem;">{label}</p>',
            unsafe_allow_html=True,
        )
    if st.session_state.uploaded_sources:
        st.caption(", ".join(st.session_state.uploaded_sources.keys()))

    chat_box = st.container(height=560 if map_ready else 480)
    with chat_box:
        for m in st.session_state.messages:
            st.chat_message(m["role"]).markdown(m["content"])
        if st.session_state.phase == "await_topic" and len(st.session_state.messages) == 1:
            st.markdown(
                '<p class="welcome-title">Start with a topic.</p>'
                '<p class="welcome-sub">I’ll draft a mind map, then challenge it. '
                "Studio opens beside chat only when that map is ready.</p>",
                unsafe_allow_html=True,
            )
            for s in SUGGESTIONS:
                if st.button(s, key=f"suggest_{s}"):
                    submit(s)

    submission = st.chat_input(
        "Describe a topic, or attach a source",
        accept_file="multiple",
        file_type=["txt", "md", "csv", "pdf"],
    )
    if submission:
        submit(submission.text, submission.files)


def render_studio(map_markdown: str) -> None:
    st.subheader("Studio")
    st.markdown(STUDIO_LABEL, unsafe_allow_html=True)
    render_mindmap(map_markdown, height=560)
    if st.session_state.get("refined"):
        st.caption(
            "Tags show where each branch came from. (H) = well-established, "
            "(?) = worth double-checking. These are the model's own estimates, "
            "not verified facts."
        )
        rating = st.slider("Rate this map", 1, 5, 3)
        comment = st.text_input("Optional comment")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve & log feedback", use_container_width=True):
                feedback.log(
                    st.session_state.topic,
                    st.session_state.refined,
                    rating,
                    comment,
                )
                st.success("Logged. Thanks!")
        with c2:
            if st.button("Start over", use_container_width=True):
                reset_conversation()
                st.rerun()
    else:
        st.caption("Draft — refining based on your answers in the chat.")


init_state()

map_markdown = st.session_state.get("refined") or st.session_state.get("draft")
map_ready = bool(map_markdown)
n_sources = len(st.session_state.get("uploaded_sources", {}))

st.markdown(
    f"<style>{_CSS_SPLIT if map_ready else _CSS_SOLO}</style>",
    unsafe_allow_html=True,
)

st.title("MindMap V2")
st.caption(DISCLAIMER)

if map_ready:
    left, right = st.columns([0.42, 0.58], gap="xxsmall")
    with left:
        render_chat(n_sources, map_ready=True)
    with right:
        render_studio(map_markdown)
else:
    render_chat(n_sources, map_ready=False)
