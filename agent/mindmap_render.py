"""Renders a markdown nested-bullet outline as an interactive, pannable,
zoomable mind-map diagram (via markmap.js), instead of a flat bullet list.

markmap.js builds its node tree directly from markdown list nesting, which
is exactly the format agent/prompts.py already asks the model for -- so no
extra parsing is needed on the Python side, just an HTML/JS wrapper.

Requires the end user's browser to reach cdn.jsdelivr.net (d3, markmap-lib,
markmap-view). If your network blocks that, the diagram won't render --
see the fallback note in app.py.
"""

import html

import streamlit as st

_TEMPLATE = """
<div id="mm-shell">
  <div id="mm-toolbar" role="toolbar" aria-label="Mind map zoom">
    <button type="button" id="mm-zoom-out" aria-label="Zoom out">−</button>
    <button type="button" id="mm-fit" aria-label="Fit to panel">Fit</button>
    <button type="button" id="mm-zoom-in" aria-label="Zoom in">+</button>
    <span id="mm-zoom-label">100%%</span>
  </div>
  <div id="mm-viewport">
    <div id="mm-sizer">
      <svg id="markmap"></svg>
    </div>
  </div>
</div>
<pre id="mm-source" hidden>%(escaped_markdown)s</pre>
<style>
  html, body { margin: 0; background: #fffaf4; overflow: hidden; height: 100%%; }
  #mm-shell { display: flex; flex-direction: column; height: 100%%; background: #fffaf4; }
  #mm-toolbar {
    display: flex; align-items: center; gap: 6px; padding: 0 2px 8px; flex: 0 0 auto;
    font-family: "Source Sans 3", "Segoe UI", sans-serif;
  }
  #mm-toolbar button {
    min-width: 40px; min-height: 40px; padding: 0 10px;
    border: 1px solid #d6d3d1; border-radius: 10px;
    background: #fffaf4; color: #1c1917; font-size: 1rem; cursor: pointer;
  }
  #mm-toolbar button:hover { border-color: #0f766e; color: #0f766e; }
  #mm-toolbar button:focus-visible { outline: 2px solid #0f766e; outline-offset: 2px; }
  #mm-zoom-label { margin-left: 4px; font-size: 0.8rem; color: #57534e; }
  #mm-viewport {
    position: relative; height: %(height)dpx; max-height: %(height)dpx;
    overflow: hidden; border-radius: 12px; background: #fffaf4;
  }
  #mm-viewport.is-zoomed {
    overflow: auto;
    scrollbar-gutter: stable;
  }
  #mm-viewport.is-zoomed::-webkit-scrollbar { width: 10px; height: 10px; }
  #mm-viewport.is-zoomed::-webkit-scrollbar-thumb {
    background: #c4c0bb; border-radius: 8px;
  }
  #mm-sizer { position: relative; width: 100%%; height: %(height)dpx; }
  #markmap { width: 100%%; height: %(height)dpx; display: block; transform-origin: 0 0; }
  #markmap text { fill: #1c1917; font-family: "Source Sans 3", "Segoe UI", sans-serif; }
  #markmap .markmap-foreign,
  #markmap .markmap-foreign * { color: #1c1917 !important; font-family: "Source Sans 3", "Segoe UI", sans-serif; }
  #markmap .markmap-link { stroke-opacity: 0.55; }
</style>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-lib"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-view"></script>
<script>
(function() {
  var BASE = %(height)d;
  var scale = 1;
  var markdown = document.getElementById('mm-source').innerHTML;
  var mm = window.markmap;
  var Transformer = mm.Transformer, Markmap = mm.Markmap, loadCSS = mm.loadCSS, loadJS = mm.loadJS;
  var transformer = new Transformer();
  var result = transformer.transform(markdown);
  var assets = transformer.getUsedAssets(result.features);
  if (assets.styles) loadCSS(assets.styles);
  if (assets.scripts) loadJS(assets.scripts, { getMarkmap: function() { return mm; } });
  var instance = Markmap.create('#markmap', {
    duration: 0, initialExpandLevel: -1, zoom: false, pan: true
  }, result.root);
  try { instance.fit(); } catch (e) {}

  var viewport = document.getElementById('mm-viewport');
  var sizer = document.getElementById('mm-sizer');
  var svg = document.getElementById('markmap');
  var label = document.getElementById('mm-zoom-label');

  function applyScale() {
    var vw = viewport.clientWidth || svg.clientWidth;
    sizer.style.width = (vw * scale) + 'px';
    sizer.style.height = (BASE * scale) + 'px';
    svg.style.width = vw + 'px';
    svg.style.height = BASE + 'px';
    svg.style.transform = 'scale(' + scale + ')';
    viewport.classList.toggle('is-zoomed', scale > 1.01);
    viewport.style.overflow = scale > 1.01 ? 'auto' : 'hidden';
    label.textContent = Math.round(scale * 100) + '%%';
  }

  function setScale(next) {
    scale = Math.min(3, Math.max(0.5, next));
    applyScale();
  }

  document.getElementById('mm-zoom-in').addEventListener('click', function() { setScale(scale * 1.25); });
  document.getElementById('mm-zoom-out').addEventListener('click', function() { setScale(scale / 1.25); });
  document.getElementById('mm-fit').addEventListener('click', function() {
    scale = 1;
    applyScale();
    try { instance.fit(); } catch (e) {}
  });

  applyScale();
  window.addEventListener('resize', applyScale);

  // Parent-page splitter: drag the gutter between Chat and Studio.
  try {
    var doc = window.parent.document;
    var KEY = 'mmv2-split';
    function layout(leftPct) {
      var row = doc.querySelector('[data-testid="stHorizontalBlock"]');
      if (!row) return false;
      var cols = row.querySelectorAll(':scope > [data-testid="stColumn"]');
      if (cols.length < 2) return false;
      cols[0].style.flex = '0 0 ' + leftPct + '%%';
      cols[0].style.maxWidth = leftPct + '%%';
      cols[0].style.width = leftPct + '%%';
      cols[1].style.flex = '0 0 ' + (100 - leftPct) + '%%';
      cols[1].style.maxWidth = (100 - leftPct) + '%%';
      cols[1].style.width = (100 - leftPct) + '%%';
      row.style.gap = '0px';
      row.style.position = 'relative';
      var handle = row.querySelector('.mm-split-handle');
      if (!handle) {
        handle = doc.createElement('div');
        handle.className = 'mm-split-handle';
        handle.setAttribute('role', 'separator');
        handle.setAttribute('aria-orientation', 'vertical');
        handle.setAttribute('aria-label', 'Resize chat and studio');
        handle.tabIndex = 0;
        row.appendChild(handle);
        var dragging = false;
        function pctFromX(x) {
          var rect = row.getBoundingClientRect();
          var pct = ((x - rect.left) / rect.width) * 100;
          return Math.min(70, Math.max(28, pct));
        }
        function commit(pct) {
          try { sessionStorage.setItem(KEY, String(pct)); } catch (e) {}
          layout(pct);
        }
        handle.addEventListener('pointerdown', function(e) {
          dragging = true;
          handle.setPointerCapture(e.pointerId);
          e.preventDefault();
        });
        handle.addEventListener('pointermove', function(e) {
          if (!dragging) return;
          commit(pctFromX(e.clientX));
        });
        handle.addEventListener('pointerup', function() { dragging = false; });
        handle.addEventListener('keydown', function(e) {
          var cur = parseFloat(sessionStorage.getItem(KEY) || '42');
          if (e.key === 'ArrowLeft') { commit(cur - 2); e.preventDefault(); }
          if (e.key === 'ArrowRight') { commit(cur + 2); e.preventDefault(); }
        });
      }
      handle.style.left = leftPct + '%%';
      return true;
    }
    var saved = 42;
    try { saved = parseFloat(sessionStorage.getItem(KEY) || '42'); } catch (e) {}
    if (!isFinite(saved)) saved = 42;
    var tries = 0;
    (function boot() {
      if (layout(saved) || tries++ > 40) return;
      requestAnimationFrame(boot);
    })();
  } catch (e) {}
})();
</script>
"""


def render_mindmap(markdown_text: str, height: int = 560) -> None:
    """Renders markdown_text (a nested bullet outline) as an interactive
    mind map. Use the toolbar to zoom; scroll appears only after zooming
    in past the panel. Drag to pan."""
    escaped = html.escape(markdown_text)
    # %-formatting, not str.format(), because the CSS/JS above is full of
    # literal { } braces that would collide with .format()'s placeholders.
    doc = _TEMPLATE % {"height": height, "escaped_markdown": escaped}
    st.iframe(doc, height=height + 52)
