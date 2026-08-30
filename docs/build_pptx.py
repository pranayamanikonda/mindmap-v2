"""Build a 16:9 .pptx for the MindMap V2 eval deck using only the stdlib."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "MindMap-V2-Eval.pptx"
SHOT = ROOT / "assets" / "studio.png"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}

SLIDE_W = 12192000
SLIDE_H = 6858000
INK = "1C1917"
MUTED = "57534E"
TEAL = "0F766E"
PAPER = "F3EEE6"
CARD = "FFFAF4"


def rgb(s: str) -> str:
    return f'<a:srgbClr val="{s}"/>'


def solid(s: str) -> str:
    return f"<a:solidFill>{rgb(s)}</a:solidFill>"


def run(text: str, size: int, color: str, bold: bool = False, font: str = "Calibri") -> str:
    b = ' b="1"' if bold else ""
    return (
        f'<a:r><a:rPr lang="en-US" sz="{size}"{b} dirty="0">'
        f"{solid(color)}<a:latin typeface=\"{font}\"/></a:rPr>"
        f"<a:t>{escape(text)}</a:t></a:r>"
    )


def para(runs: str, align: str = "l", spc: int = 0) -> str:
    spc_xml = f'<a:spcBef><a:spcPts val="{spc}"/></a:spcBef>' if spc else ""
    return (
        f'<a:p><a:pPr algn="{align}">{spc_xml}</a:pPr>{runs}'
        f'<a:endParaRPr lang="en-US"/></a:p>'
    )


def shape(sid: int, name: str, x: int, y: int, w: int, h: int, body: str) -> str:
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{sid}" name="{name}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="{x}" y="{y}"/>
            <a:ext cx="{w}" cy="{h}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/>
          <a:lstStyle/>
          {body}
        </p:txBody>
      </p:sp>"""


def picture(sid: int, rid: str, x: int, y: int, w: int, h: int) -> str:
    return f"""
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="{sid}" name="Screenshot"/>
          <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="{rid}"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm>
            <a:off x="{x}" y="{y}"/>
            <a:ext cx="{w}" cy="{h}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>"""


def slide_xml(shapes: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:cSld>
    <p:bg><p:bgPr>{solid(PAPER)}<a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {shapes}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def title_body_slide(kicker: str, title: str, bullets: list[str]) -> str:
    body_runs = para(run(kicker.upper(), 1400, TEAL, True))
    body_runs += para(run(title, 3200, INK, True, "Georgia"), spc=600)
    bullets_xml = "".join(
        para(run(item, 1800, MUTED), spc=400) for item in bullets
    )
    return slide_xml(
        shape(2, "Title", 548640, 548640, 11000000, 2200000, body_runs)
        + shape(3, "Body", 548640, 2800000, 11000000, 3500000, bullets_xml)
    )


SLIDES: list[tuple[str, str | None]] = []


def add(xml: str, extra_rels: str | None = None) -> None:
    SLIDES.append((xml, extra_rels))


add(
    slide_xml(
        shape(
            2,
            "Kicker",
            548640,
            3200000,
            11000000,
            400000,
            para(run("HCAI  ·  WEEKS 1–3", 1400, TEAL, True)),
        )
        + shape(
            3,
            "Title",
            548640,
            3600000,
            11000000,
            1400000,
            para(run("MindMap V2", 6000, INK, True, "Georgia")),
        )
        + shape(
            4,
            "Lede",
            548640,
            5100000,
            10000000,
            900000,
            para(
                run(
                    "A chat-first agent that drafts a mind map, challenges it with research, and only finalizes after you answer.",
                    1800,
                    MUTED,
                )
            ),
        )
    )
)

add(
    title_body_slide(
        "Who it’s for",
        "Someone starting a messy plan, not a polished report.",
        [
            "Need: turn a vague topic into a map they can argue with — trip, launch, or research plan.",
            "Success: they can say what the challenge step changed, and whether they’d use the result.",
            "Studio stays hidden until a draft exists. Conversation first, artifact second.",
        ],
    )
)

add(
    title_body_slide(
        "The loop",
        "Chat drives every step.",
        [
            "Topic → goal → constraints → draft → research + questions → your answers → validate → rate.",
            "You can skip goal/constraints, answer any probing question, attach a source, or start over.",
            "Validation must return OK or the app asks a clarifying question instead of showing a broken map.",
        ],
    )
)

pic_rel = """
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/studio.png"/>
"""
add(
    slide_xml(
        shape(
            2,
            "Kicker",
            548640,
            400000,
            11000000,
            300000,
            para(run("PRODUCT", 1400, TEAL, True)),
        )
        + shape(
            3,
            "Title",
            548640,
            700000,
            11000000,
            700000,
            para(run("Chat on the left. Studio on the right.", 2800, INK, True, "Georgia")),
        )
        + picture(4, "rId2", 548640, 1600000, 11085000, 4800000)
    ),
    pic_rel,
)

add(
    title_body_slide(
        "HCAI mapping",
        "Where the brief shows up in the product",
        [
            "Trust: disclaimer on every screen — drafts and challenges, does not verify facts.",
            "Control: skip, answer, attach files, start over. The map is not a one-shot dump.",
            "Feedback: rate + comment after a final map. Logged to eval/feedback_log.csv.",
        ],
    )
)

add(
    title_body_slide(
        "What to try",
        "A 12-minute evaluation path",
        [
            "Happy path: “10-day trip to Singapore.” Skip goal if you want. Answer two questions. Watch the map change.",
            "Source: attach a short .txt or .pdf mid-chat. Check that the map absorbs it.",
            "Close the loop: rate the result. If something felt off, say so in the comment.",
        ],
    )
)

add(
    title_body_slide(
        "Evidence in the repo",
        "What graders can open without a demo",
        [
            "eval/run_eval.py — draft → research → challenge on 3 topics.",
            "agent/prompts.py — draft, research, challenge, refine, validate.",
            "agent/file_ingest.py — .txt / .md / .csv / .pdf; image-only PDFs say so.",
            "https://github.com/pranayamanikonda/mindmap-v2",
        ],
    )
)

add(
    title_body_slide(
        "Honest gaps",
        "Known, not hidden",
        [
            "Validate checks structure, not unsafe / out-of-scope content.",
            "File + answer in the same send can skip the answer.",
            "Google Search 429s fall back to ungrounded research.",
            "Free-tier Gemini quota is shared by everyone on the live app.",
        ],
    )
)

add(
    title_body_slide(
        "Links",
        "Code is public. Live app needs Streamlit Cloud.",
        [
            "Repo: github.com/pranayamanikonda/mindmap-v2",
            "Deploy: share.streamlit.io — this repo, main, app.py",
            "Secret (Cloud only, never in Git): GEMINI_API_KEY",
            "After deploy, send evaluators the *.streamlit.app URL.",
        ],
    )
)

add(
    slide_xml(
        shape(
            2,
            "Title",
            548640,
            2400000,
            11000000,
            1600000,
            para(run("Try it, then tell me what you’d change.", 3600, INK, True, "Georgia")),
        )
        + shape(
            3,
            "Lede",
            548640,
            4200000,
            10000000,
            1200000,
            para(
                run(
                    "The useful critique is: did the challenge step earn the map, or would you have been better with a blank page?",
                    1800,
                    MUTED,
                )
            ),
        )
    )
)


def presentation_xml(n: int) -> str:
    sld_ids = "\n".join(
        f'<p:sldId id="{256 + i}" r:id="rId{i + 2}"/>' for i in range(n)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}"
    saveSubsetFonts="1">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {sld_ids}
  </p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""


def presentation_rels(n: int) -> str:
    rels = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    ]
    for i in range(n):
        rels.append(
            f'<Relationship Id="rId{i + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i + 1}.xml"/>'
        )
    rels.append(
        '<Relationship Id="rId100" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>'
    )
    rels.append(
        '<Relationship Id="rId101" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>'
    )
    rels.append(
        '<Relationship Id="rId102" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    inner = "\n  ".join(rels)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {inner}
</Relationships>
"""


THEME = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{NS['a']}" name="MindMap V2">
  <a:themeElements>
    <a:clrScheme name="MindMap">
      <a:dk1><a:srgbClr val="{INK}"/></a:dk1>
      <a:lt1><a:srgbClr val="{PAPER}"/></a:lt1>
      <a:dk2><a:srgbClr val="{MUTED}"/></a:dk2>
      <a:lt2><a:srgbClr val="{CARD}"/></a:lt2>
      <a:accent1><a:srgbClr val="{TEAL}"/></a:accent1>
      <a:accent2><a:srgbClr val="{TEAL}"/></a:accent2>
      <a:accent3><a:srgbClr val="{TEAL}"/></a:accent3>
      <a:accent4><a:srgbClr val="{TEAL}"/></a:accent4>
      <a:accent5><a:srgbClr val="{TEAL}"/></a:accent5>
      <a:accent6><a:srgbClr val="{TEAL}"/></a:accent6>
      <a:hlink><a:srgbClr val="{TEAL}"/></a:hlink>
      <a:folHlink><a:srgbClr val="{TEAL}"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="MindMap">
      <a:majorFont><a:latin typeface="Georgia"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="MindMap">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>
"""

MASTER = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}">
  <p:cSld>
    <p:bg><p:bgPr>{solid(PAPER)}<a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
</p:sldMaster>
"""

LAYOUT = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{NS['a']}" xmlns:r="{NS['r']}" xmlns:p="{NS['p']}" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""

PRES_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>
"""

VIEW_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr>
  <p:slideViewPr>
    <p:cSldViewPr>
      <p:cViewPr varScale="1">
        <p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale>
        <p:origin x="0" y="0"/>
      </p:cViewPr>
      <p:guideLst/>
    </p:cSldViewPr>
  </p:slideViewPr>
</p:viewPr>
"""

CONTENT_TYPES_HEAD = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
"""


def main() -> None:
    n = len(SLIDES)
    overrides = "".join(
        f'  <Override PartName="/ppt/slides/slide{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
        for i in range(n)
    )
    content_types = CONTENT_TYPES_HEAD + overrides + "</Types>\n"

    rels_root = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>
"""
    master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""
    layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_root)
        z.writestr("ppt/presentation.xml", presentation_xml(n))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(n))
        z.writestr("ppt/slideMasters/slideMaster1.xml", MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
        z.writestr("ppt/theme/theme1.xml", THEME)
        z.writestr("ppt/presProps.xml", PRES_PROPS)
        z.writestr("ppt/viewProps.xml", VIEW_PROPS)
        if SHOT.exists():
            z.write(SHOT, "ppt/media/studio.png")
        for i, (xml, extra) in enumerate(SLIDES, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", xml)
            rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  {extra or ""}
</Relationships>
"""
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rels)

    print(f"Wrote {OUT} ({n} slides)")


if __name__ == "__main__":
    main()
