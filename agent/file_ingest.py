"""Extracts plain text from uploaded source files so it can be folded into
the draft/refine prompts as reference material -- this is the equivalent
of NotebookLM's "Sources": grounding content the model should draw on.

Supported: .txt, .md, .csv (read directly as UTF-8), .pdf (text layer
extracted via pypdf -- scanned/image-only PDFs won't have a text layer
and will come back empty). Anything else is reported, not silently
dropped, so the user knows why a file didn't do anything.
"""

import io

_TEXT_EXTENSIONS = {"txt", "md", "csv"}


def extract_text(uploaded_file) -> str:
    name = getattr(uploaded_file, "name", "uploaded file")
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    data = uploaded_file.read()

    if suffix in _TEXT_EXTENSIONS:
        return data.decode("utf-8", errors="replace")

    if suffix == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return "[Could not read this PDF -- run: pip install pypdf]"
        try:
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text or "[No extractable text -- this PDF may be scanned images]"
        except Exception as e:
            return f"[Could not extract text from this PDF: {e}]"

    return f"[Skipped {name} -- only .txt, .md, .csv, and .pdf are read right now]"
