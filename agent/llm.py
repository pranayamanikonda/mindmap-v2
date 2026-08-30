"""Each function here is one step from the workflow diagram: draft, research
+ challenge, refine, validate. Keep them separate -- it's what makes the
loop debuggable and lets you swap one step's prompt without touching the
others.
"""

import json
import re

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from . import config, prompts

_client = None
_active_model = config.MODEL_NAME


def _get_client():
    """Lazy client init: a missing key only fails when an API call is
    actually attempted, not at import time -- so pure functions like
    _parse_questions stay unit-testable without any key present."""
    global _client
    if _client is None:
        api_key = config.resolve_gemini_api_key()
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Locally: copy .env.example to "
                ".env. On Streamlit Cloud: App settings → Secrets → "
                'GEMINI_API_KEY = "your-key". Get a key at '
                "https://aistudio.google.com/apikey"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _generate(contents: str, tools=None):
    global _active_model
    cfg = types.GenerateContentConfig(tools=tools) if tools else None
    try:
        return _get_client().models.generate_content(
            model=_active_model, contents=contents, config=cfg
        )
    except ClientError as e:
        fallback = getattr(config, "FALLBACK_MODEL_NAME", None)
        if e.code != 429 or not fallback or _active_model == fallback:
            raise
        _active_model = fallback
        return _get_client().models.generate_content(
            model=_active_model, contents=contents, config=cfg
        )


def draft_mind_map(topic: str, goal: str, constraints: str, reference_material: str = "") -> str:
    prompt = prompts.DRAFT_PROMPT.format(
        topic=topic,
        goal=goal,
        constraints=constraints or "none given",
        reference_material=reference_material or "none provided",
    )
    return _generate(prompt).text


def research_and_challenge(topic: str, draft: str):
    """Runs a grounded search for alternatives, then turns the draft +
    alternatives into probing questions. Returns (alternatives_text,
    sources, questions_list)."""
    search_prompt = prompts.RESEARCH_PROMPT.format(topic=topic, draft=draft)
    try:
        search_response = _generate(
            search_prompt, tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    except ClientError as e:
        if e.code != 429:
            raise
        search_response = _generate(search_prompt)
    alternatives = search_response.text or ""
    sources = _extract_sources(search_response)

    challenge_prompt = prompts.CHALLENGE_PROMPT.format(
        draft=draft, search_results=alternatives
    )
    challenge_response = _generate(challenge_prompt)
    questions = _parse_questions(challenge_response.text or "")
    return alternatives, sources, questions


def _parse_questions(text: str) -> list[str]:
    """Parses the challenge step's JSON array of questions. Falls back to
    splitting on lines if the model didn't return clean JSON -- a bad
    parse here shouldn't crash the app, just degrade gracefully."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, list) and data:
            return [str(q).strip() for q in data if str(q).strip()]
    except json.JSONDecodeError:
        pass
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    parsed = [re.sub(r"^[\d\-\*\.\)]+\s*", "", line) for line in lines]
    return parsed or ([cleaned] if cleaned else [])


def _extract_sources(response) -> list[dict]:
    """Pulls {title, url} pairs out of the grounding metadata, if present.
    Defensive by design -- grounding metadata shape has shifted across SDK
    versions, so a missing field here should degrade to an empty list
    rather than crash the app."""
    sources = []
    try:
        for candidate in response.candidates:
            metadata = getattr(candidate, "grounding_metadata", None)
            chunks = getattr(metadata, "grounding_chunks", None) if metadata else None
            for chunk in chunks or []:
                web = getattr(chunk, "web", None)
                if web:
                    sources.append({"title": web.title, "url": web.uri})
    except Exception:
        pass
    return sources


def refine_mind_map(
    draft: str,
    user_answers: str,
    alternatives: str,
    sources: list[dict],
    reference_material: str = "",
) -> str:
    source_list = "\n".join(f"- {s['title']}: {s['url']}" for s in sources) or "none found"
    prompt = prompts.REFINE_PROMPT.format(
        draft=draft,
        alternatives=alternatives,
        sources=source_list,
        reference_material=reference_material or "none provided",
        user_answers=user_answers or "no answer given -- use your best guess",
    )
    return _generate(prompt).text


def validate_map(map_text: str, topic: str) -> str:
    prompt = prompts.VALIDATE_PROMPT.format(map_text=map_text, topic=topic)
    return _generate(prompt).text.strip()
