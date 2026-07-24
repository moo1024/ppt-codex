"""네이티브 PPT 렌더러 + 테마 라이브러리 (아키텍처 v7 — Claude 직접 디자인).

Claude가 작성한 pages/pNN/layout_spec.json을 python-pptx 네이티브 개체로 그린다.
텍스트는 100% 편집 가능. GPT(kie) 이미지는 image 아이템(스팟 슬롯)에만 쓴다.

layout_spec: {"page": N, "theme": "gyoan|anthropic|cupertino|stripe|figma|vercel",
              "variant": "paper|dark", "items": [...]}

테마 5종(gyoan 제외)은 getdesign.md의 브랜드 DESIGN.md 원전 규칙을 한글 타이포로
번안한 것 — 팔레트 hex·서피스 문법·시그니처 무브를 원전에서 그대로 가져온다.

아이템 타입:
  glow / label / serif_label / headline / text / card / pill / chip /
  hairline / arrow / sowhat / timetable / bars / steps / image /
  chart(네이티브 PPT 차트 — 엑셀 백업 데이터, 편집 가능) /
  table(네이티브 PPT 표 — 셀 데이터 편집 가능)
  ※ 그래프·표는 반드시 chart/table(네이티브 개체)로 — card 사각형으로 그리지 말 것.

runs: [{"t": "텍스트", "color"?: hex, "weight"?: "bold", "font"?: 폰트키, "size"?: pt}]
좌표는 전부 슬라이드 비율(0~1).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.util import Emu, Pt

SLIDE_W = 12192000
SLIDE_H = 6858000

# 페이지 크기 프리셋 — layout_spec의 "page_size" 키(덱 단위, 첫 페이지 기준)
PAGE_SIZES = {
    "16:9": (12192000, 6858000),
    "a4p": (6858000, 9906000),   # A4 세로 (결과보고서·수료증 등 문서형)
    "3:4": (6858000, 9144000),   # 세로 포스터·키비주얼 (인스타·에타 마스터)
}


def _set_page_size(key: str):
    global SLIDE_W, SLIDE_H
    if key not in PAGE_SIZES:
        raise ValueError(f"unknown page_size: {key} (지원: {list(PAGE_SIZES)})")
    SLIDE_W, SLIDE_H = PAGE_SIZES[key]

# ── 교안 토큰 (하위 호환용 상수) ──────────────────────────────────────────────
PAPER = "F7F5F1"
INK = "1B1A18"
ORANGE = "E8622C"
CARD = "EFECE7"
CARD_DARKER = "E9E5DF"
GRAY = "8A857D"
HAIR = "D8D3CB"
DARK = "0B0A09"
WHITE = "F5F2ED"
DARK_SUB = "B7A99A"

FONTS = {
    "display_b": ("Paperlogy 7 Bold", False),
    "display_sb": ("Paperlogy 6 SemiBold", False),
    "body": ("Pretendard", False),
    "body_sb": ("Pretendard SemiBold", False),
    "body_b": ("Pretendard", True),
    "serif": ("Georgia", False),
}

# ── 테마 라이브러리 ───────────────────────────────────────────────────────────
# 각 테마 = 색 토큰 + 폰트 매핑 + 글로우 팔레트. 프리미티브는 전부 공유.
THEMES: dict[str, dict] = {
    # 교안 (기본): 웜페이퍼 + 챠콜 + 번트오렌지, Paperlogy/Pretendard
    "gyoan": {
        "bg": PAPER, "ink": INK, "accent": ORANGE, "on_accent": "FFFFFF",
        "card": CARD, "card2": CARD_DARKER, "gray": GRAY, "hair": HAIR,
        "arrow": "B9B2A8", "highlight": "F6DEC9", "body_ink": "4A463F",
        "dark_bg": DARK, "dark_fg": WHITE, "dark_sub": DARK_SUB,
        "fonts": dict(FONTS),
        "glow": {"core": (242, 122, 40), "deep": (120, 48, 14), "base": (11, 10, 9)},
    },
    # 앤트로픽(Claude DESIGN.md): 크림 캔버스 + 코랄 한 점, 세리프 디스플레이.
    # "굵기가 아니라 크기로 말한다" — 헤드라인은 바탕체, 라벨/본문은 산스.
    "anthropic": {
        "bg": "FAF9F5", "ink": "141413", "accent": "CC785C", "on_accent": "FFFFFF",
        "card": "EFE9DE", "card2": "E8E0D2", "gray": "6C6A64", "hair": "E6DFD8",
        "arrow": "C9C1B4", "highlight": "F5F0E8", "body_ink": "3D3D3A",
        "dark_bg": "181715", "dark_fg": "FAF9F5", "dark_sub": "A09D96",
        "fonts": {
            "display_b": ("KoPubWorld바탕체 Bold", False),
            "display_sb": ("Pretendard SemiBold", False),
            "body": ("Pretendard", False),
            "body_sb": ("Pretendard SemiBold", False),
            "body_b": ("Pretendard", True),
            "serif": ("KoPubWorld바탕체 Light", False),
        },
        "glow": {"core": (230, 140, 105), "deep": (140, 60, 35), "base": (24, 23, 21)},
    },
    # 쿠퍼티노(Apple DESIGN.md): 화이트/파치먼트/다크 타일 3서피스, 단일 블루 악센트.
    # 시스템 전체에 그림자·장식 0 — 서피스 색 전환이 곧 구획.
    "cupertino": {
        "bg": "FFFFFF", "ink": "1D1D1F", "accent": "0066CC", "on_accent": "FFFFFF",
        "card": "F5F5F7", "card2": "EBEBED", "gray": "86868B", "hair": "E0E0E0",
        "arrow": "C7C7CC", "highlight": "D9E8FA", "body_ink": "424245",
        "dark_bg": "161617", "dark_fg": "F5F5F7", "dark_sub": "98989D",
        "fonts": {
            "display_b": ("AppleSDGothicNeoB00", False),
            "display_sb": ("AppleSDGothicNeoSB00", False),
            "body": ("AppleSDGothicNeoR00", False),
            "body_sb": ("AppleSDGothicNeoSB00", False),
            "body_b": ("AppleSDGothicNeoB00", False),
            "serif": ("Georgia", False),
        },
        "glow": {"core": (238, 238, 244), "deep": (70, 70, 78), "base": (10, 10, 11)},
    },
    # 스트라이프(Stripe DESIGN.md): 딥네이비 잉크 + 인디고, 라이트웨이트 엘레강스.
    # 디스플레이는 에스코어드림 라이트 — 얇은 대형 활자가 브랜드 그 자체.
    "stripe": {
        "bg": "FFFFFF", "ink": "0D253D", "accent": "533AFD", "on_accent": "FFFFFF",
        "card": "F6F9FC", "card2": "EAF0F7", "gray": "64748D", "hair": "E3E8EE",
        "arrow": "B9C4D9", "highlight": "E7E4FE", "body_ink": "3C4257",
        "dark_bg": "1C1E54", "dark_fg": "F6F9FC", "dark_sub": "A5AEE0",
        "fonts": {
            "display_b": ("에스코어 드림 7 ExtraBold", False),
            "display_sb": ("에스코어 드림 5 Medium", False),
            "body": ("Pretendard", False),
            "body_sb": ("Pretendard SemiBold", False),
            "body_b": ("Pretendard", True),
            "serif": ("D2Coding", False),
        },
        "glow": {"core": (160, 120, 255), "deep": (80, 60, 220), "base": (28, 30, 84)},
    },
    # 피그마(Figma DESIGN.md): 흑백 크롬 + 파스텔 컬러블록, 모노 아이브로우.
    # 구조는 전부 블랙/화이트, 색은 블록(카드 fill 오버라이드)으로만.
    "figma": {
        "bg": "FFFFFF", "ink": "0A0A0A", "accent": "0A0A0A", "on_accent": "FFFFFF",
        "card": "F7F7F5", "card2": "EDEDE8", "gray": "6E6E6B", "hair": "E6E6E6",
        "arrow": "C9C9C9", "highlight": "DCEEB1", "body_ink": "1A1A1A",
        "dark_bg": "1F1D3D", "dark_fg": "FFFFFF", "dark_sub": "C9C0EE",
        "fonts": {
            "display_b": ("더잠실 5 Bold", False),
            "display_sb": ("더잠실 4 Medium", False),
            "body": ("Pretendard", False),
            "body_sb": ("Pretendard SemiBold", False),
            "body_b": ("Pretendard", True),
            "serif": ("D2Coding", False),
        },
        "glow": {"core": (197, 176, 244), "deep": (110, 85, 200), "base": (31, 29, 61)},
    },
    # 버셀(Vercel DESIGN.md): 잉크 모노크롬 + 모노스페이스 라벨, 다크 폴라리티 밴드.
    # 웨이트 상한 600, 문장형+마침표 헤드라인, 색은 링크 블루 한 점만.
    "vercel": {
        "bg": "FAFAFA", "ink": "171717", "accent": "171717", "on_accent": "FFFFFF",
        "card": "FFFFFF", "card2": "F5F5F5", "gray": "888888", "hair": "EBEBEB",
        "arrow": "BFBFBF", "highlight": "D3E5FF", "body_ink": "4D4D4D",
        "dark_bg": "0A0A0A", "dark_fg": "EDEDED", "dark_sub": "8F8F8F",
        "fonts": {
            "display_b": ("Freesentation 7 Bold", False),
            "display_sb": ("Freesentation 5 Medium", False),
            "body": ("Pretendard", False),
            "body_sb": ("Pretendard SemiBold", False),
            "body_b": ("Pretendard", True),
            "serif": ("D2Coding", False),
        },
        "glow": {"core": (0, 190, 220), "deep": (100, 40, 190), "base": (10, 10, 10)},
    },
}

# TYPE SCALE — 크기·폰트키·색 "역할" (색은 테마에서 해석)
TYPO_ROLES = {
    "label":     {"size": 10,   "font": "display_sb", "role": "accent"},
    "headline":  {"size": 23,   "font": "display_b",  "role": "ink"},
    "divider_h": {"size": 30,   "font": "display_b",  "role": "dark_fg"},
    "sub":       {"size": 13,   "font": "body",       "role": "gray"},
    "cardtitle": {"size": 13.5, "font": "display_sb", "role": "ink"},
    "body":      {"size": 11.5, "font": "body",       "role": "body_ink"},
    "sowhat":    {"size": 12,   "font": "body_sb",    "role": "ink"},
    "caption":   {"size": 8.5,  "font": "body",       "role": "gray"},
    "chip":      {"size": 10,   "font": "body_sb",    "role": "on_accent"},
    "pill":      {"size": 10.5, "font": "body_sb",    "role": "on_accent"},
    "num_xl":    {"size": 34,   "font": "display_b",  "role": "ink"},
    "meta":      {"size": 10.5, "font": "body",       "role": "dark_sub"},
    "serif":     {"size": 11,   "font": "serif",      "role": "dark_sub"},
}

_ACTIVE = THEMES["gyoan"]  # render_page가 페이지별로 설정

# JSON 테마 레지스트리 — 코드 수정 없이 테마 추가.
# 탐색 순서: 프로젝트/themes/<name>.json → pptm/design/themes/<name>.json.
# JSON은 THEMES 항목과 같은 구조(부분 정의 가능 — 빠진 키는 gyoan에서 상속).
_BUILTIN_THEME_DIR = Path(__file__).parent / "themes"


def _normalize_theme(raw: dict) -> dict:
    t = {**THEMES["gyoan"], **raw}
    t["fonts"] = {**THEMES["gyoan"]["fonts"],
                  **{k: tuple(v) for k, v in raw.get("fonts", {}).items()}}
    if "glow" in raw:
        t["glow"] = {k: tuple(v) for k, v in raw["glow"].items()}
    return t


def resolve_theme(name: str, project_dir: Path | None = None) -> dict:
    if name in THEMES:
        return THEMES[name]
    candidates = []
    if project_dir is not None:
        candidates.append(Path(project_dir) / "themes" / f"{name}.json")
    candidates.append(_BUILTIN_THEME_DIR / f"{name}.json")
    for p in candidates:
        if p.exists():
            theme = _normalize_theme(json.loads(p.read_text()))
            THEMES[name] = theme  # 캐시
            return theme
    raise KeyError(f"테마 '{name}' 없음 — THEMES 내장 또는 themes/{name}.json 필요")


def _typo(key: str) -> dict:
    r = TYPO_ROLES[key]
    return {"size": r["size"], "font": r["font"], "color": _ACTIVE[r["role"]]}


# 하위 호환: 기존 코드/스펙이 TYPO를 참조하면 gyoan 값으로 해석
TYPO = {k: {"size": v["size"], "font": v["font"], "color": THEMES["gyoan"][v["role"]]}
        for k, v in TYPO_ROLES.items()}


def _c(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr)


def _x(v: float) -> Emu:
    return Emu(int(v * SLIDE_W))


def _y(v: float) -> Emu:
    return Emu(int(v * SLIDE_H))


def _set_runs(para, runs, default_style: dict, spacing: float | None = None):
    para.alignment = PP_ALIGN.LEFT
    for r in runs:
        run = para.add_run()
        run.text = r["t"]
        fkey = r.get("font", default_style["font"])
        fname, fbold = _ACTIVE["fonts"][fkey]
        run.font.name = fname
        # font.name은 <a:latin>만 설정 — 한글은 <a:ea>(동아시아) 슬롯을 쓰므로
        # 같이 지정하지 않으면 렌더러가 기본 고딕으로 폴백한다.
        rPr = run._r.get_or_add_rPr()
        for tag in ("a:ea", "a:cs"):
            e = rPr.find(qn(tag))
            if e is None:
                e = rPr.makeelement(qn(tag), {})
                rPr.append(e)
            e.set("typeface", fname)
        run.font.bold = fbold or (r.get("weight") == "bold")
        run.font.size = Pt(r.get("size", default_style["size"]))
        run.font.color.rgb = _c(r.get("color", default_style["color"]))
        # 자간(letter-spacing) — python-pptx 미노출이라 rPr/@spc(1/100 pt)를 직접 쓴다.
        # 매거진 마스트헤드처럼 "가늘게 + 넓게" 앉히는 조판에 필수.
        track = r.get("tracking", default_style.get("tracking"))
        if track:
            rPr.set("spc", str(int(round(track * 100))))


def _textbox(slide, x, y, w, h=None):
    tb = slide.shapes.add_textbox(_x(x), _y(y), _x(w), _y(h if h else 0.06))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tb, tf


def _norm_runs(item, style):
    if "runs" in item:
        return [item["runs"]] if isinstance(item["runs"][0], dict) else item["runs"]
    lines = item.get("lines") or [item["text"]]
    color = item.get("color", style["color"])
    return [[{"t": ln, "color": color}] for ln in lines]


def _add_text_item(slide, item, style_key):
    style = dict(_typo(style_key))
    if "size" in item:
        style["size"] = item["size"]
    if "color" in item:
        style["color"] = item["color"]
    if "tracking" in item:
        style["tracking"] = item["tracking"]
    line_groups = _norm_runs(item, style)
    tb, tf = _textbox(slide, item["x"], item["y"], item["w"], item.get("h"))
    first = True
    for runs in line_groups:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        _set_runs(para, runs, style)
        # num_xl(빅넘버)은 1.0 — 기본 1.45는 글자를 박스 아래로 밀어 밑줄/헤어라인과 겹친다.
        _def_sp = {"headline": 1.18, "divider_h": 1.18, "num_xl": 1.0}.get(style_key, 1.45)
        para.line_spacing = item.get("spacing", _def_sp)
        align = item.get("align", "left")
        para.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                          "right": PP_ALIGN.RIGHT}[align]
    if item.get("rot"):
        tb.rotation = item["rot"]
    if item.get("anchor"):
        tb.text_frame.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
                                         "bottom": MSO_ANCHOR.BOTTOM}[item["anchor"]]
    return tb


def _add_poly(slide, pts, fill, outline=None, outline_w=1.0):
    """프리폼 다각형 채우기 — 아이소메트릭 타일 등. pts = [(x_frac, y_frac), ...]."""
    epts = [(int(px * SLIDE_W), int(py * SLIDE_H)) for (px, py) in pts]
    fb = slide.shapes.build_freeform(epts[0][0], epts[0][1], scale=1.0)
    fb.add_line_segments(epts[1:], close=True)
    shp = fb.convert_to_shape()
    if fill == "none":
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = _c(fill)
    if outline:
        shp.line.color.rgb = _c(outline)
        shp.line.width = Pt(outline_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    _strip_style(shp)
    return shp


def _pill_w(text: str, size: float) -> float:
    """필 자동 폭 — 한글/CJK는 전각, 라틴/숫자는 반각으로 추정."""
    f = 0.0
    for ch in text:
        wide = ord(ch) >= 0x1100 or ch in "·—↔→←“”"
        f += 0.0105 if wide else 0.0058
    return 0.024 + f * size / 10.5


def _strip_style(shp):
    """add_shape가 붙이는 <p:style>(테마 effectRef 그림자 참조) 제거.

    빈 <a:effectLst/>만으로는 LibreOffice가 테마 그림자를 무시하지 않는다.
    """
    el = shp._element
    st = el.find(qn("p:style"))
    if st is not None:
        el.remove(st)
    return shp


def _rounded(slide, x, y, w, h, fill, radius=0.5, outline=None,
             outline_w=1.2, outline_dash=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, _x(x), _y(y), _x(w), _y(h))
    try:
        shp.adjustments[0] = radius
    except Exception:
        pass
    if fill == "none":
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = _c(fill)
    if outline:
        shp.line.color.rgb = _c(outline)
        shp.line.width = Pt(outline_w)
        if outline_dash:  # 빈 슬롯(자리) 선언용 파선 테두리
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            shp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return _strip_style(shp)


def _hairline_shape(slide, x, y, w, color=None, dash=None, thick=None):
    h = Emu(int(9525 * (thick or 1)))
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, _x(x), _y(y), _x(w), h)
    ln.fill.solid()
    ln.fill.fore_color.rgb = _c(color or _ACTIVE["hair"])
    ln.line.fill.background()
    ln.shadow.inherit = False
    if dash:  # 점선: 촘촘한 사각 세그먼트로 재현 (렌더러 독립적)
        ln.fill.background()
        seg = 0.006
        cx = x
        while cx < x + w:
            s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, _x(cx), _y(y),
                                       _x(min(seg, x + w - cx)), h)
            s.fill.solid()
            s.fill.fore_color.rgb = _c(color or _ACTIVE["hair"])
            s.line.fill.background()
            s.shadow.inherit = False
            _strip_style(s)
            cx += seg * 2
    return _strip_style(ln)


# 범용 도형 프리미티브 — 인포그래픽 조립용 (관공서 장표 문법: 육각형·사선 밴드·파이·링)
_SHAPES = {
    "hexagon": MSO_SHAPE.HEXAGON,
    "parallelogram": MSO_SHAPE.PARALLELOGRAM,
    "pie": MSO_SHAPE.PIE,
    "arc_ring": MSO_SHAPE.BLOCK_ARC,
    "chevron": MSO_SHAPE.CHEVRON,
    "pentagon_arrow": MSO_SHAPE.PENTAGON,
    "oval": MSO_SHAPE.OVAL,
    "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
    "diamond": MSO_SHAPE.DIAMOND,
    "rounded": MSO_SHAPE.ROUNDED_RECTANGLE,
}


def _add_shape_item(slide, item, T):
    shp = slide.shapes.add_shape(_SHAPES[item["shape"]], _x(item["x"]), _y(item["y"]),
                                 _x(item["w"]), _y(item["h"]))
    for i, v in enumerate(item.get("adj", [])):
        try:
            shp.adjustments[i] = v
        except Exception:
            pass
    fill = item.get("fill", T["accent"])
    if fill == "none":
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = _c(fill)
    if item.get("outline"):
        shp.line.color.rgb = _c(item["outline"])
        shp.line.width = Pt(item.get("outline_w", 1.2))
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    if item.get("rot"):
        shp.rotation = item["rot"]
    _strip_style(shp)
    if item.get("text"):
        tf = shp.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Emu(20000)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        style = dict(_typo(item.get("style", "chip")))
        style["color"] = item.get("text_color", style["color"])
        if "size" in item:
            style["size"] = item["size"]
        _set_runs(tf.paragraphs[0], [{"t": item["text"]}], style)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    return shp


def _apply_grad(shp, top_hex, bottom_hex):
    """카드 세로 2-stop 그라데이션 (평가자료 모드 헤더 필)."""
    from pptx.oxml.ns import nsmap
    import copy
    spPr = shp._element.spPr
    for tag in ("a:solidFill", "a:noFill", "a:gradFill"):
        e = spPr.find(qn(tag))
        if e is not None:
            spPr.remove(e)
    from lxml import etree
    grad = etree.SubElement(spPr, qn("a:gradFill"))
    lst = etree.SubElement(grad, qn("a:gsLst"))
    for pos, hx in ((0, top_hex), (100000, bottom_hex)):
        gs = etree.SubElement(lst, qn("a:gs"))
        gs.set("pos", str(pos))
        clr = etree.SubElement(gs, qn("a:srgbClr"))
        clr.set("val", hx)
    lin = etree.SubElement(grad, qn("a:lin"))
    lin.set("ang", "5400000")  # 90° = 위→아래
    lin.set("scaled", "1")
    # ln(테두리)보다 앞에 와야 하므로 위치 재조정
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(grad)
        ln.addprevious(grad)


def _apply_shadow(shp, alpha_pct=22):
    """소프트 드롭섀도우 (평가자료 모드 카드)."""
    from lxml import etree
    spPr = shp._element.spPr
    old = spPr.find(qn("a:effectLst"))
    if old is not None:
        spPr.remove(old)
    eff = etree.SubElement(spPr, qn("a:effectLst"))
    sh = etree.SubElement(eff, qn("a:outerShdw"))
    sh.set("blurRad", "90000")
    sh.set("dist", "28000")
    sh.set("dir", "5400000")
    sh.set("rotWithShape", "0")
    clr = etree.SubElement(sh, qn("a:srgbClr"))
    clr.set("val", "1F3864")
    a = etree.SubElement(clr, qn("a:alpha"))
    a.set("val", str(alpha_pct * 1000))


def _glow_png(assets_dir: Path, theme_name: str, cx: float, cy: float,
              sigma: float, intensity: float) -> Path:
    """다크 디바이더용 블룸 배경 PNG (테마 팔레트, 결정적 자체 생성)."""
    w = 2560
    h = int(round(w * SLIDE_H / SLIDE_W))
    key = f"glow_{theme_name}_{w}x{h}_{cx:.2f}_{cy:.2f}_{sigma:.2f}_{intensity:.2f}.png"
    out = assets_dir / key
    if out.exists():
        return out
    g = _ACTIVE["glow"]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    d2 = ((xx - cx * w) ** 2 + (yy - cy * h) ** 2) / (sigma * w) ** 2
    core = np.exp(-d2 * 2.2)
    halo = np.exp(-d2 * 0.55)
    base = np.array(g["base"], dtype=np.float64)
    corec = np.array(g["core"], dtype=np.float64)
    deep = np.array(g["deep"], dtype=np.float64)
    img = base[None, None, :] \
        + deep[None, None, :] * (halo[..., None] * 0.85 * intensity) \
        + corec[None, None, :] * (core[..., None] * 0.9 * intensity)
    rng = np.random.default_rng(0)
    img += rng.standard_normal((h, w, 1)) * 1.1
    assets_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out)
    return out


def _scrim_png(assets_dir: Path, edge: str, color: str, strength: float,
               softness: float) -> Path:
    """풀블리드 이미지용 알파 그라데이션 스크림 PNG (투명→color). 시네마틱 자막 하단부용.

    edge: bottom/top/left/right — 그 방향 바깥으로 갈수록 진해진다. 배치 rect에 맞춰 늘어난다.
    """
    key = f"scrim_{edge}_{color}_{strength:.2f}_{softness:.2f}.png"
    out = assets_dir / key
    if out.exists():
        return out
    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    vertical = edge in ("bottom", "top")
    n = 1024
    ramp = np.linspace(0.0, 1.0, n)  # 0=안쪽(투명) → 1=바깥(진함)
    if edge in ("top", "left"):
        ramp = ramp[::-1].copy()
    alpha = np.clip(ramp, 0, 1) ** softness * strength
    a8 = (alpha * 255).astype(np.uint8)
    if vertical:
        arr = np.zeros((n, 8, 4), dtype=np.uint8)
        arr[..., 3] = a8[:, None]
    else:
        arr = np.zeros((8, n, 4), dtype=np.uint8)
        arr[..., 3] = a8[None, :]
    arr[..., 0], arr[..., 1], arr[..., 2] = r, g, b
    assets_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, "RGBA").save(out)
    return out


_ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}

_CHART_KIND = {
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,        # 가로 막대
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,  # 세로 막대
    "line": XL_CHART_TYPE.LINE,
    "line_markers": XL_CHART_TYPE.LINE_MARKERS,
    "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT,
}
# "No Style, No Grid" — 기본 밴딩/테두리 없는 표 스타일
_TABLE_NO_GRID = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


def _ea_cs(rpr, fname):
    """defRPr/rPr에 동아시아(a:ea)·복합문자(a:cs) typeface 주입 — 한글 폴백 방지.

    a:latin 뒤에 오도록 append (OOXML 시퀀스 순서 유지)."""
    if rpr is None:
        return
    for tag in ("a:ea", "a:cs"):
        e = rpr.find(qn(tag))
        if e is None:
            e = rpr.makeelement(qn(tag), {})
            rpr.append(e)
        e.set("typeface", fname)


def _font_ea(font_obj, fname, size=None, color=None, bold=None):
    font_obj.name = fname
    if size is not None:
        font_obj.size = Pt(size)
    if color is not None:
        font_obj.color.rgb = _c(color)
    if bold is not None:
        font_obj.bold = bold
    _ea_cs(font_obj._rPr, fname)


def _add_chart(slide, item):
    """네이티브 PPT 차트(엑셀 백업 데이터 — 더블클릭 편집 가능)."""
    kind = item.get("kind", "column")
    xltype = _CHART_KIND.get(kind, XL_CHART_TYPE.COLUMN_CLUSTERED)
    size = item.get("size", 10)
    fname = _ACTIVE["fonts"][item.get("font", "body")][0]
    nfmt = item.get("number_format", "General")

    data = CategoryChartData()
    data.categories = item["categories"]
    for s in item["series"]:
        data.add_series(s.get("name", "series"), tuple(s["values"]), number_format=nfmt)

    gf = slide.shapes.add_chart(xltype, _x(item["x"]), _y(item["y"]),
                                _x(item["w"]), _y(item["h"]), data)
    chart = gf.chart
    chart.has_title = False
    _font_ea(chart.font, fname, size=size, color=item.get("text_color", _ACTIVE["body_ink"]))

    is_pie = kind in ("pie", "doughnut")
    chart.has_legend = bool(item.get("legend", len(item["series"]) > 1 or is_pie))
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        _font_ea(chart.legend.font, fname, size=size, color=_ACTIVE["body_ink"])

    plot = chart.plots[0]
    if not is_pie and item.get("gap") is not None:
        plot.gap_width = item["gap"]

    if item.get("value_labels"):
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.number_format = item.get("label_format", nfmt)
        dl.number_format_is_linked = False
        _font_ea(dl.font, fname, size=item.get("label_size", size),
                 color=item.get("value_color"), bold=True)
        try:
            dl.position = XL_LABEL_POSITION.OUTSIDE_END if not is_pie \
                else XL_LABEL_POSITION.BEST_FIT
        except (ValueError, KeyError):
            pass

    # 색상: 단일 시리즈 → 포인트별 / 다중 시리즈 → 시리즈별
    colors = item.get("colors")
    sers = list(chart.series)
    if colors and len(sers) == 1:
        for i, pt in enumerate(sers[0].points):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = _c(colors[i % len(colors)])
    else:
        for i, ser in enumerate(sers):
            c = (colors[i % len(colors)] if colors else item["series"][i].get("color"))
            if c:
                ser.format.fill.solid()
                ser.format.fill.fore_color.rgb = _c(c)

    if not is_pie:
        try:
            cat_ax, val_ax = chart.category_axis, chart.value_axis
            cat_ax.visible = item.get("cat_axis", True)
            val_ax.visible = item.get("val_axis", False)
            cat_ax.has_major_gridlines = False
            val_ax.has_major_gridlines = item.get("gridlines", False)
            if cat_ax.visible:
                _font_ea(cat_ax.tick_labels.font, fname, size=size, color=_ACTIVE["body_ink"])
                cat_ax.format.line.color.rgb = _c(item.get("axis_color", _ACTIVE["hair"]))
            if val_ax.visible:
                _font_ea(val_ax.tick_labels.font, fname, size=size, color=_ACTIVE["gray"])
            if item.get("value_max") is not None:
                val_ax.maximum_scale = item["value_max"]
            if item.get("value_min") is not None:
                val_ax.minimum_scale = item["value_min"]
        except (ValueError, KeyError, AttributeError):
            pass
    return gf


def _tc_bottom_border(cell, color, w_pt):
    """셀 하단 헤어라인 — solidFill 앞에 a:lnB 삽입(OOXML 시퀀스 준수)."""
    tcPr = cell._tc.get_or_add_tcPr()
    old = tcPr.find(qn("a:lnB"))
    if old is not None:
        tcPr.remove(old)
    ln = tcPr.makeelement(qn("a:lnB"), {"w": str(int(w_pt * 12700)), "cap": "flat"})
    fill = ln.makeelement(qn("a:solidFill"), {})
    clr = fill.makeelement(qn("a:srgbClr"), {"val": color})
    fill.append(clr)
    ln.append(fill)
    fill_tags = ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill",
                 "a:pattFill", "a:grpFill")
    ref = None
    for tag in fill_tags:
        ref = tcPr.find(qn(tag))
        if ref is not None:
            break
    if ref is not None:
        ref.addprevious(ln)
    else:
        tcPr.append(ln)


def _add_table(slide, item):
    """네이티브 PPT 표(셀 데이터 편집 가능). 밴딩 스타일 제거 후 직접 채색."""
    rows = item["rows"]
    nrows, ncols = len(rows), len(rows[0])
    gf = slide.shapes.add_table(nrows, ncols, _x(item["x"]), _y(item["y"]),
                                _x(item["w"]), _y(item["h"]))
    table = gf.table
    table.first_row = table.last_row = table.horz_banding = table.vert_banding = False
    styleId = table._tbl.tblPr.find(qn("a:tableStyleId"))
    if styleId is None:
        styleId = table._tbl.tblPr.makeelement(qn("a:tableStyleId"), {})
        table._tbl.tblPr.append(styleId)
    styleId.text = _TABLE_NO_GRID

    col_w = item.get("col_w")
    if col_w:
        for i, cw in enumerate(col_w[:ncols]):
            table.columns[i].width = _x(item["w"] * cw)
    if item.get("row_h"):
        for r in table.rows:
            r.height = _y(item["row_h"])

    header = item.get("header", True)
    size = item.get("size", 11)
    fontkey = item.get("font", "body")
    aligns = item.get("align")
    borders = item.get("borders", True)
    for ri, row in enumerate(rows):
        is_head = header and ri == 0
        for ci in range(ncols):
            val = row[ci] if ci < len(row) else ""
            cell = table.cell(ri, ci)
            cell.margin_left = cell.margin_right = Emu(int(0.014 * SLIDE_W))
            cell.margin_top = cell.margin_bottom = Emu(int(0.008 * SLIDE_H))
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if is_head:
                fill = item.get("header_fill", _ACTIVE["ink"])
            elif item.get("alt_fill") and ri % 2 == 1:
                fill = item["alt_fill"]
            else:
                fill = item.get("body_fill", _ACTIVE["bg"])
            cell.fill.solid()
            cell.fill.fore_color.rgb = _c(fill)
            color = (item.get("header_color", "FFFFFF") if is_head
                     else item.get("body_color", _ACTIVE["ink"]))
            style = {**_typo("body"), "size": size,
                     "font": (item.get("header_font", "body_b") if is_head else fontkey),
                     "color": color}
            run = {"t": str(val), "color": color}
            if is_head or item.get("weight") == "bold":
                run["weight"] = "bold"
            para = cell.text_frame.paragraphs[0]
            _set_runs(para, [run], style)
            al = (aligns[ci] if aligns and ci < len(aligns) else item.get("cell_align", "left"))
            para.alignment = _ALIGN[al]
            if borders and not is_head and ri < nrows - 1:
                _tc_bottom_border(cell, item.get("border_color", _ACTIVE["hair"]), 0.75)
            if is_head:
                _tc_bottom_border(cell, item.get("header_border", item.get("header_fill", _ACTIVE["ink"])), 1.2)
    return gf


def render_page(slide, spec: dict, assets_dir: Path):
    global _ACTIVE
    theme_name = spec.get("theme", "gyoan")
    if "theme_tokens" in spec:  # 스펙 인라인 일회성 테마
        _ACTIVE = _normalize_theme(spec["theme_tokens"])
        THEMES.setdefault(theme_name, _ACTIVE)
    else:
        _ACTIVE = resolve_theme(theme_name, assets_dir.parent)
    T = _ACTIVE
    variant = spec.get("variant", "paper")

    bgfill = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bgfill.fill.solid()
    bgfill.fill.fore_color.rgb = _c(T["dark_bg"] if variant == "dark" else T["bg"])
    bgfill.line.fill.background()
    bgfill.shadow.inherit = False
    _strip_style(bgfill)

    for item in spec.get("items", []):
        t = item["type"]
        if t == "glow":
            png = _glow_png(assets_dir, theme_name, item["cx"], item["cy"],
                            item.get("sigma", 0.35), item.get("intensity", 1.0))
            slide.shapes.add_picture(str(png), 0, 0, SLIDE_W, SLIDE_H)
        elif t == "scrim":
            edge = item.get("edge", "bottom")
            png = _scrim_png(assets_dir, edge, item.get("color", "000000"),
                             item.get("strength", 0.9), item.get("softness", 1.25))
            if edge in ("bottom", "top"):
                hh = item.get("h", 0.5)
                yy = 1 - hh if edge == "bottom" else 0.0
                slide.shapes.add_picture(str(png), 0, _y(yy), SLIDE_W, _y(hh))
            else:
                ww = item.get("w", 0.5)
                xx = 1 - ww if edge == "right" else 0.0
                slide.shapes.add_picture(str(png), _x(xx), 0, _x(ww), SLIDE_H)
        elif t == "label":
            _add_text_item(slide, {**item, "w": item.get("w", 0.4)}, "label")
        elif t == "serif_label":
            style = dict(_typo("serif"))
            if "color" in item:
                style["color"] = item["color"]
            if "size" in item:
                style["size"] = item["size"]
            tb, tf = _textbox(slide, item["x"], item["y"], item["w"])
            para = tf.paragraphs[0]
            _set_runs(para, [{"t": item["text"]}], style)
            for run in para.runs:
                run.font.italic = True
            para.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                              "right": PP_ALIGN.RIGHT}[item.get("align", "center")]
        elif t == "headline":
            _add_text_item(slide, item, "divider_h" if variant == "dark" else "headline")
        elif t == "text":
            _add_text_item(slide, item, item.get("style", "body"))
        elif t == "card":
            shp = _rounded(slide, item["x"], item["y"], item["w"], item["h"],
                           item.get("fill", T["card"]), item.get("radius", 0.18),
                           item.get("outline"), item.get("outline_w", 1.2),
                           item.get("outline_dash"))
            if item.get("rot"):  # 스티키 노트 등 살짝 기울이기 (도)
                shp.rotation = item["rot"]
            if item.get("grad"):  # 세로 그라데이션 ["top","bottom"] — 평가자료 헤더 필
                _apply_grad(shp, item["grad"][0], item["grad"][1])
            if item.get("shadow"):  # 소프트 드롭섀도우 — 평가자료 카드
                _apply_shadow(shp, item.get("shadow_alpha", 22))
        elif t == "shape":
            _add_shape_item(slide, item, T)
        elif t == "pill":
            h = item["h"]
            w = item.get("w", _pill_w(item["text"], item.get("size", 10.5)))
            shp = _rounded(slide, item["x"], item["y"], w, h,
                           item.get("fill", T["accent"]), radius=0.5)
            tf = shp.text_frame
            tf.word_wrap = False
            tf.margin_left = tf.margin_right = Emu(20000)
            tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = tf.paragraphs[0]
            style = dict(_typo("pill"))
            style["color"] = item.get("text_color", style["color"])
            if "size" in item:
                style["size"] = item["size"]
            _set_runs(para, [{"t": item["text"]}], style)
            para.alignment = PP_ALIGN.CENTER
            if item.get("grad"):  # 카드와 동일: 세로 그라데이션
                _apply_grad(shp, item["grad"][0], item["grad"][1])
            if item.get("shadow"):  # 소프트 드롭섀도우
                _apply_shadow(shp, item.get("shadow_alpha", 22))
        elif t == "chip":
            d = item["d"]
            shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, _x(item["x"]), _y(item["y"]),
                                         _x(d), Emu(int(d * SLIDE_W)))
            shp.fill.solid()
            shp.fill.fore_color.rgb = _c(item.get("fill", T["accent"]))
            shp.line.fill.background()
            shp.shadow.inherit = False
            _strip_style(shp)
            tf = shp.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = tf.paragraphs[0]
            style = dict(_typo("chip"))
            style["color"] = item.get("text_color", style["color"])
            _set_runs(para, [{"t": item["text"]}], style)
            para.alignment = PP_ALIGN.CENTER
        elif t == "band":
            # 채워진 바(SO WHAT/클로저/캡션) — 라벨+본문을 세로·가로 자동 중앙 정렬.
            # card+별도 text 손좌표의 세로 어긋남·라벨↔본문 빈공백을 구조적으로 제거.
            shp = _rounded(slide, item["x"], item["y"], item["w"], item["h"],
                           item.get("fill", T["card"]), radius=item.get("radius", 0.5))
            tf = shp.text_frame
            tf.word_wrap = True
            pad = item.get("pad", 0.024)
            tf.margin_left = tf.margin_right = _x(pad)
            tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = tf.paragraphs[0]
            lsize = item.get("label_size", 9.5)
            runs = []
            if item.get("label"):
                runs.append({"t": item["label"], "color": item.get("label_color", T["accent"]),
                             "weight": "bold", "size": lsize})
                runs.append({"t": item.get("sep", "   "), "size": lsize})
            runs.append({"t": item.get("text", ""), "color": item.get("text_color", T["ink"]),
                         "size": item.get("size", 11)})
            _set_runs(para, runs, dict(_typo("body")))
            para.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                              "right": PP_ALIGN.RIGHT}[item.get("align", "center")]
        elif t == "hairline":
            _hairline_shape(slide, item["x"], item["y"], item["w"], item.get("color"),
                            dash=item.get("dash"), thick=item.get("thick"))
        elif t == "arrow":
            ar = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, _x(item["x"]), _y(item["y"]),
                                        _x(item["w"]), _y(item.get("h", 0.014)))
            ar.adjustments[0] = 0.5
            ar.adjustments[1] = 0.55
            ar.fill.solid()
            ar.fill.fore_color.rgb = _c(item.get("color", T["arrow"]))
            ar.line.fill.background()
            ar.shadow.inherit = False
            _strip_style(ar)
        elif t == "sowhat":
            y = item.get("y", 0.885)
            _hairline_shape(slide, 0.05, y, 0.90)
            tb, tf = _textbox(slide, 0.05, y + 0.028, 0.90)
            para = tf.paragraphs[0]
            _set_runs(para, [
                {"t": item.get("label", "SO WHAT"), "color": T["accent"],
                 "font": "body_b", "size": 11},
                {"t": "   " + item["text"], "color": T["ink"],
                 "font": "body_sb", "size": 12},
            ], _typo("sowhat"))
        elif t == "timetable":
            rows = item["rows"]
            row_h = item.get("row_h", 0.135)
            x0, y0, w0 = item["x"], item["y"], item["w"]
            time_w = item.get("time_w", 0.13)
            body_x = x0 + item.get("body_indent", 0.17)
            for i, r in enumerate(rows):
                ry = y0 + i * row_h
                cy = ry + row_h / 2
                hl = r.get("highlight", False)
                text_h = 0.036
                ty = cy - text_h / 2
                if hl:
                    band_h = row_h * 0.72
                    _rounded(slide, x0, cy - band_h / 2, w0, band_h,
                             item.get("highlight_fill", T["highlight"]), radius=0.5)
                tb, tf = _textbox(slide, x0 + 0.025, ty, time_w)
                _set_runs(tf.paragraphs[0], [{"t": r["time"]}],
                          {**_typo("cardtitle"), "size": 15,
                           "color": T["accent"] if hl else T["ink"]})
                tb, tf = _textbox(slide, body_x, ty + 0.002, 0.45)
                tf.word_wrap = False
                _set_runs(tf.paragraphs[0], [{"t": r["body"]}],
                          {**_typo("body"), "size": 12.5,
                           "color": T["ink"] if hl else T["body_ink"]})
                if hl and r.get("pill"):
                    pill_w = item.get("pill_w", 0.055)
                    px = body_x + r.get("pill_offset", 0.145)
                    ph = 0.046
                    shp = _rounded(slide, px, cy - ph / 2, pill_w, ph,
                                   T["accent"], radius=0.5)
                    ptf = shp.text_frame
                    ptf.margin_left = ptf.margin_right = ptf.margin_top = ptf.margin_bottom = 0
                    ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
                    _set_runs(ptf.paragraphs[0], [{"t": r["pill"]}], _typo("pill"))
                    ptf.paragraphs[0].alignment = PP_ALIGN.CENTER
                    if r.get("note"):
                        tb, tf = _textbox(slide, px + pill_w + 0.015, ty + 0.002, 0.3)
                        tf.word_wrap = False
                        _set_runs(tf.paragraphs[0], [{"t": r["note"]}],
                                  {**_typo("body"), "size": 12.5, "color": T["ink"]})
                if i < len(rows) - 1:
                    _hairline_shape(slide, x0, ry + row_h - 0.001, w0)
        elif t == "bars":
            rows = item["items"]
            mx = item.get("max", max(r["value"] for r in rows))
            row_h = item["h"] / len(rows)
            bar_x = item["x"] + item.get("label_w", 0.13)
            bar_span = item["w"] - item.get("label_w", 0.13) - 0.06
            for i, r in enumerate(rows):
                yy = item["y"] + i * row_h
                tb, tf = _textbox(slide, item["x"], yy + row_h * 0.18,
                                  item.get("label_w", 0.13))
                _set_runs(tf.paragraphs[0], [{"t": r["label"]}],
                          {**_typo("body"), "size": 11, "color": T["gray"]})
                bw = max(0.015, bar_span * r["value"] / mx)
                hl = r.get("highlight")
                _rounded(slide, bar_x, yy + row_h * 0.16, bw, row_h * 0.52,
                         T["accent"] if hl else T["card2"], radius=0.5)
                tb, tf = _textbox(slide, bar_x + bw + 0.012, yy + row_h * 0.18, 0.05)
                _set_runs(tf.paragraphs[0], [{"t": str(r["value"])}],
                          {**_typo("body"), "size": 11.5, "font": "body_sb",
                           "color": T["accent"] if hl else T["ink"]})
        elif t == "steps":
            names = item["items"]
            n = len(names)
            span = item["w"] / n
            d = item.get("d", 0.022)
            for i, name in enumerate(names):
                x0 = item["x"] + i * span
                shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, _x(x0), _y(item["y"]),
                                             _x(d), Emu(int(d * SLIDE_W)))
                shp.fill.solid()
                shp.fill.fore_color.rgb = _c(item.get("fill", T["accent"]))
                shp.line.fill.background()
                shp.shadow.inherit = False
                _strip_style(shp)
                tf = shp.text_frame
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.MIDDLE
                _set_runs(tf.paragraphs[0], [{"t": str(i + 1)}], _typo("chip"))
                tf.paragraphs[0].alignment = PP_ALIGN.CENTER
                tb, tf2 = _textbox(slide, x0 + d + 0.008, item["y"] + 0.004,
                                   span - d - 0.03)
                _set_runs(tf2.paragraphs[0], [{"t": name}],
                          {**_typo("body"), "size": 11.5, "font": "body_sb",
                           "color": T["ink"]})
                if i < n - 1:
                    ar = slide.shapes.add_shape(
                        MSO_SHAPE.RIGHT_ARROW,
                        _x(x0 + span - 0.033), _y(item["y"] + 0.006),
                        _x(0.02), _y(0.012))
                    ar.fill.solid()
                    ar.fill.fore_color.rgb = _c(T["arrow"])
                    ar.line.fill.background()
                    ar.shadow.inherit = False
                    _strip_style(ar)
        elif t == "image":
            p = Path(item["path"])
            if not p.is_absolute():
                p = assets_dir.parent / item["path"]
            if p.exists():
                slide.shapes.add_picture(str(p), _x(item["x"]), _y(item["y"]),
                                         _x(item["w"]), _y(item["h"]))
        elif t == "poly":
            _add_poly(slide, item["points"], item.get("fill", T["accent"]),
                      item.get("outline"), item.get("outline_w", 1.0))
        elif t == "chart":
            _add_chart(slide, item)
        elif t == "table":
            _add_table(slide, item)
        else:
            raise ValueError(f"unknown item type: {t}")


def render_deck(project_dir: Path) -> Path:
    project_dir = Path(project_dir)
    assets_dir = project_dir / "assets"
    page_dirs = sorted((project_dir / "pages").glob("p[0-9][0-9]"))

    # 덱 페이지 크기 — 첫 스펙의 page_size 키 (없으면 16:9)
    size_key = "16:9"
    for pdir in page_dirs:
        sp = pdir / "layout_spec.json"
        if sp.exists():
            size_key = json.loads(sp.read_text()).get("page_size", "16:9")
            break
    _set_page_size(size_key)

    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    blank = prs.slide_layouts[6]
    for pdir in page_dirs:
        spec_path = pdir / "layout_spec.json"
        if not spec_path.exists():
            continue
        spec = json.loads(spec_path.read_text())
        slide = prs.slides.add_slide(blank)
        render_page(slide, spec, assets_dir)

    out_dir = project_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "deck.pptx"
    prs.save(out)
    return out
