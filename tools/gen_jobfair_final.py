"""잡페어 완성 포스터 5종 — layout_spec 생성기 (3:4 네이티브).

브리프: 키비주얼-캠페인/브리프-완성포스터-ppt디테일.md
디자인 타깃: 완성포스터-흑백회사색/완성-NAVER.png 외 4장 (레이아웃 그대로)

역할 분담이 이 포스터의 전부다:
  · kie = **우측 인물 플레이트 한 장뿐** (흑백 인물 + 회사색 랜야드 + 대각 컬러 패널).
    plate-*.png 는 tools/prep_jobfair_plate.py 가 배경을 순백으로 정규화하고
    패널을 브랜드 정색으로 치환한 뒤 대각선을 다시 자른 결과물이다.
  · 그 외 100%는 여기서 네이티브 개체로 조판한다 — 글자·아이콘·로고자리 전부.
    (Codex 통짜 버전이 반려된 이유가 '글자·아이콘이 AI 근사치'라서다.)

인물 플레이트 실측 윤곽(prep_jobfair_plate.py --probe)에 맞춰 좌측 텍스트 폭과
우측 컬럼 x를 잡았다. 인물이 바뀌면 --probe 를 다시 돌려 아래 상수를 검증할 것.

사용:  python3 tools/gen_jobfair_final.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "projects" / "knu-jobfair-final" / "pages"

INK = "111111"
BODY = "333333"
GRAY = "6E6E6E"
RULE = "D5D5D5"

# ── 판면 그리드 (3:4 = 7.5in × 10in) ─────────────────────────────────────────
ML = 0.062          # 좌 마진
MR = 0.938          # 우 경계
COL_R = 0.745       # 우측 컬럼 x — 플레이트 머리 우측끝 0.723 보다 오른쪽
COL_RW = 0.200
TXT_X = 0.150       # 프로그램 텍스트 x (아이콘 + 세로 룰 오른쪽)
ROWS = (0.372, 0.478, 0.584)   # 프로그램 3행 상단

ASPECT = 0.75       # x 비율 → y 비율 (정원·정사각 보정: 7.5in / 10in)

# 대각 컬러 패널 — **5종 완전 동일한 네이티브 도형**. (AI가 그린 패널은 각도·경계가
# 매번 달라 시리즈로 안 붙는다.) 우측 가장자리 y0.42에서 시작해 하단 x0.38로 내려간다:
# 우측 컬럼 텍스트(≤y0.435)보다 아래에서 시작하고, 하단 좌측 일정/KNU 자리는 비운다.
PANEL = [(1.0, 0.42), (1.0, 1.0), (0.38, 1.0)]

# 인물 배치 목표 — NAVER 컷 실측값이 기준. 5종의 머리 크기·위치를 여기에 맞춘다.
HEAD_TOP, HEAD_RIGHT, HEAD_W = 0.331, 0.723, 0.212

# 텍스트가 실제로 앉는 자리 — (이름, y0, y1, 인물이 넘으면 안 되는 x, 좌/우).
# 블록별 실측 오른쪽 끝 + 여유 0.02. 뭉뚱그린 큰 박스로 재면 멀쩡한 배치도 오검출된다.
ZONES = [
    ("헤드라인", 0.100, 0.245, 0.500, "left"),
    ("부제", 0.250, 0.330, 0.410, "left"),
    ("프로그램1", 0.368, 0.455, 0.500, "left"),
    ("프로그램2", 0.474, 0.560, 0.425, "left"),
    ("프로그램3", 0.580, 0.640, 0.495, "left"),
    ("일정", 0.695, 0.792, 0.275, "left"),
    ("장소", 0.792, 0.826, 0.353, "left"),
    ("주최", 0.826, 0.858, 0.330, "left"),
    ("KNU", 0.858, 0.925, 0.230, "left"),
    ("우측 컬럼", 0.090, 0.440, 0.735, "right"),
]


def sq(w: float) -> float:
    return w * ASPECT


def txt(x, y, w, runs, *, size, spacing=1.45, align="left", style="body",
        tracking=None, h=None, anchor=None):
    it = {"type": "text", "style": style, "x": x, "y": y, "w": w,
          "size": size, "spacing": spacing, "align": align, "runs": runs}
    if tracking is not None:
        it["tracking"] = tracking
    if h is not None:
        it["h"] = h
    if anchor:
        it["anchor"] = anchor
    return it


def bar(x, y, w, h, fill):
    """얇은 채움 막대 — check_align [A]에 걸리지 않도록 card가 아닌 shape로 낸다."""
    return {"type": "shape", "shape": "rounded", "adj": [0.0],
            "x": x, "y": y, "w": w, "h": h, "fill": fill}


def outline_box(x, y, w, h, *, radius=0.18, ow=1.6):
    return {"type": "shape", "shape": "rounded", "adj": [radius],
            "x": x, "y": y, "w": w, "h": h, "fill": "none",
            "outline": INK, "outline_w": ow}


def circle(cx, cy, d, *, ow=1.6):
    return {"type": "shape", "shape": "oval", "x": cx - d / 2, "y": cy - sq(d) / 2,
            "w": d, "h": sq(d), "fill": "none", "outline": INK, "outline_w": ow}


def arc_top(cx, cy, w, *, ow=1.6):
    """어깨 아치 = 타원 아웃라인 + 아래 절반을 순백으로 덮기 (배경이 순백이라 성립).

    반원 프리미티브가 없어서 쓰는 기법. 마스크는 반드시 도형 '직후'에 와야 한다
    (z-order = items 배열 순서).
    """
    h = sq(w)
    return [
        {"type": "shape", "shape": "oval", "x": cx - w / 2, "y": cy - h / 2,
         "w": w, "h": h, "fill": "none", "outline": INK, "outline_w": ow},
        bar(cx - w / 2 - 0.004, cy, w + 0.008, h / 2 + 0.006, "FFFFFF"),
    ]


def bubble(x, y, w, h, *, nib_x):
    """말풍선 — 아웃라인 박스 + 아래쪽 솔리드 nib(같은 잉크라 경계선과 이어져 보인다)."""
    return [
        outline_box(x, y, w, h, radius=0.30, ow=1.5),
        {"type": "shape", "shape": "triangle", "rot": 180,
         "x": nib_x, "y": y + h - 0.0006, "w": 0.0055, "h": 0.0048, "fill": INK},
    ]


# ── 라인 아이콘 3종 (실루엣이 서로 확실히 다르게: 발표자 / 두 사람 / 화면) ──────
def icon_session(cy: float) -> list[dict]:
    items = [circle(0.0785, cy - 0.0120, 0.0140)]
    items += arc_top(0.0785, cy + 0.0135, 0.0300)
    items += bubble(0.0975, cy - 0.0250, 0.0250, 0.0180, nib_x=0.1005)
    return items


def icon_mentoring(cy: float) -> list[dict]:
    items = []
    for px in (0.0735, 0.1105):
        items.append(circle(px, cy + 0.0010, 0.0125))
        items += arc_top(px, cy + 0.0235, 0.0275)
    items += bubble(0.0800, cy - 0.0300, 0.0245, 0.0155, nib_x=0.0895)
    return items


def icon_experience(cy: float) -> list[dict]:
    return [
        outline_box(0.0645, cy - 0.0225, 0.0550, 0.0315, radius=0.14),
        txt(0.0645, cy - 0.0225, 0.0550,
            [[{"t": "AI", "font": "display_b", "color": INK}]],
            size=9.5, align="center", h=0.0315, anchor="middle", spacing=1.0),
        bar(0.09125, cy + 0.0090, 0.0022, 0.0075, INK),
        bar(0.08000, cy + 0.0165, 0.0245, 0.0022, INK),
    ]


PROGRAMS = (
    (icon_session, 0.038, "CAREER SESSION", "현직자 직무특강",
     "현직자가 들려주는 생생한 직무 이야기"),
    (icon_mentoring, 0.038, "CAREER MENTORING", "1:1 취업멘토링",
     "현직자와 함께하는 1:1 맞춤 상담"),
    (icon_experience, 0.024, "JOB EXPERIENCE", None,
     "AI 면접 · 이미지컨설팅 · AI 직무분석"),
)

# ── 5종 데이터 (브리프 §5종 데이터 표 그대로 — 창작 금지) ──────────────────────
DECKS = [
    dict(key="naver", brand="03C75A", name="NAVER", name_size=26, col_size=18,
         roles=["서비스 기획", "Product Manager"],
         quote=["사용자의 일상을", "더 편리하게 만드는", "일을 합니다."],
         speaker="김도현", affil="NAVER 서비스기획 리더"),
    dict(key="hyundai", brand="002C5F", name="현대자동차", name_size=24, col_size=17,
         roles=["국내생산", "경영지원"],
         quote=["함께 움직이는 기술,", "내일을 만드는", "원동력."],
         speaker="이준호", affil="국내생산지원팀 매니저"),
    dict(key="skhynix", brand="EA5514", name="SK하이닉스", name_size=24, col_size=17,
         roles=["반도체 공정", "기술 직무"],
         quote=["기술로 연결하고,", "함께 더 큰", "가능성을 만듭니다."],
         speaker="박준영", affil="SK하이닉스 공정기술팀"),
    dict(key="samsung", brand="1428A0", name="삼성전자", name_size=25, col_size=18,
         roles=["소프트웨어 개발", "Backend Engineer"],
         quote=["좋은 코드는", "끝까지 팀을", "믿게 만듭니다."],
         speaker="최유진", affil="삼성전자 MX사업부"),
    dict(key="kepco", brand="6B2C91", name="한국전력공사", name_size=21, col_size=15.5,
         roles=["전력계통 운영", "사업관리"],
         quote=["전기를 통해", "사람과 사회를", "연결합니다."],
         speaker="김태현", affil="계통운영부"),
]

THEME_TOKENS = {
    "_grammar": "잡페어 완성 포스터 — 순백 배경 + 회사 메인컬러 1색. Pretendard 전용.",
    "bg": "FFFFFF", "ink": INK, "card": "F5F5F5", "card2": "EDEDED",
    "gray": GRAY, "hair": RULE, "arrow": "BBBBBB", "highlight": "F0F0F0",
    "body_ink": BODY, "dark_bg": "111111", "dark_fg": "FFFFFF", "dark_sub": "AAAAAA",
    "fonts": {
        "display_b": ["Pretendard ExtraBold", False],
        "display_sb": ["Pretendard SemiBold", False],
        "body": ["Pretendard", False],
        "body_sb": ["Pretendard Medium", False],
        "body_b": ["Pretendard", True],
        "serif": ["Pretendard", False],
    },
}


def place(meta: dict, nudge: dict) -> tuple[float, float, float]:
    """누끼 실측 좌표 → 이미지 배치(x, y, 배율). 눈대중 금지, 전부 여기서 푼다.

    5종의 인물 실루엣이 제각각이라 '머리 크기 고정' 한 가지 규칙으로는 못 푼다.
    대신 **텍스트를 한 글자도 안 가리는 최대 배율**을 수치 탐색한다:
      · x = 머리 오른쪽 끝이 우측 컬럼 앞에 딱 서도록 (왼쪽 여유가 최대가 되는 배치)
      · y = 하단을 정확히 블리드시키도록
      · 배율은 큰 쪽부터 내려오며 ZONES 충돌이 0이 되는 첫 값
    """
    hl, hr = meta["head"]
    _, by0, _, by1 = meta["bbox"]
    for step in range(0, 90):
        w = (1.25 - step * 0.01) * nudge.get("scale", 1.0)
        x = HEAD_RIGHT - hr * w + nudge.get("dx", 0.0)
        y = 1.0 - by1 * w + nudge.get("dy", 0.0)
        if y + by0 * w < 0.055:        # 머리가 마스트헤드까지 치솟으면 무효
            continue
        if not audit(meta, x, y, w):
            return x, y, w
    raise SystemExit("배치 해 없음 — 인물 실루엣이 판면 계약을 못 맞춥니다")


def audit(meta: dict, x: float, y: float, w: float) -> list[str]:
    """배치된 인물 실루엣이 텍스트 자리를 침범하는지 행 단위로 검사한다."""
    bad = []
    prof = meta["profile"]
    n = len(prof)
    for name, y0, y1, limit, side in ZONES:
        worst = None
        for i, pr in enumerate(prof):
            if pr is None:
                continue
            py = y + (i + 0.5) / n * w
            if not (y0 <= py <= y1):
                continue
            v = x + pr[0] * w if side == "left" else x + pr[1] * w
            if side == "left" and v < limit and (worst is None or v < worst):
                worst = v
            if side == "right" and v > limit and (worst is None or v > worst):
                worst = v
        if worst is not None:
            bad.append(f"    ✗ {name}: 인물 {side} 끝 {worst:.3f} (한계 {limit:.3f})")
    return bad


def build(d: dict, meta: dict) -> dict:
    accent = d["brand"]
    x, y, w = place(meta, d.get("nudge", {}))
    items: list[dict] = [
        # 대각 컬러 패널 (네이티브) → 그 위에 누끼 인물 → 그 위에 전부 텍스트.
        # 이 순서가 곧 z-order다.
        {"type": "poly", "points": PANEL, "fill": accent},
        {"type": "image", "path": f"assets/spots/cut-{d['key']}.png",
         "x": round(x, 4), "y": round(y, 4), "w": round(w, 4), "h": round(w, 4)},

        # 상단 좌 마스트헤드
        txt(ML, 0.034, 0.50, [
            [{"t": "경북대학교 산학협력단", "font": "body_sb", "color": "5A5A5A"}],
            [{"t": "2026 지역협업기술센터 JOB FAIR", "font": "display_sb", "color": INK}],
        ], size=11.5, spacing=1.5, tracking=0.1),

        # 상단 우 회사명
        txt(0.503, 0.030, MR - 0.503,
            [[{"t": d["name"], "font": "display_b", "color": accent}]],
            size=d["name_size"], align="right", spacing=1.0, tracking=-0.2),

        # 헤드라인 — '당신'만 회사색
        txt(0.058, 0.104, 0.62, [
            [{"t": "다음 입사자는", "font": "display_b", "color": INK}],
            [{"t": "당신", "font": "display_b", "color": accent},
             {"t": "입니다.", "font": "display_b", "color": INK}],
        ], size=41, spacing=1.10, tracking=-0.6),

        # 부제
        txt(0.060, 0.258, 0.52, [
            [{"t": "방금 대기업 붙은 선배에게", "font": "display_sb", "color": INK}],
            [{"t": "직접 듣는 취업박람회", "font": "display_sb", "color": INK}],
        ], size=16.5, spacing=1.40, tracking=-0.1),
    ]

    # ── 프로그램 3종 ────────────────────────────────────────────────────────
    for top, (icon, dy, eyebrow, title, caption) in zip(ROWS, PROGRAMS):
        items += icon(top + dy)
        block_h = 0.072 if title else 0.045
        items.append(bar(0.1345, top + 0.0015, 0.0015, block_h, RULE))
        items.append(txt(TXT_X, top, 0.42,
                         [[{"t": eyebrow, "font": "display_sb", "color": INK}]],
                         size=12.5, spacing=1.0, tracking=0.55))
        cap_y = top + 0.058
        if title:
            items.append(txt(TXT_X, top + 0.026, 0.42,
                             [[{"t": title, "font": "display_b", "color": INK}]],
                             size=15, spacing=1.0, tracking=-0.2))
        else:
            cap_y = top + 0.028
        items.append(txt(TXT_X, cap_y, 0.42,
                         [[{"t": caption, "font": "body", "color": GRAY}]],
                         size=10, spacing=1.0, style="caption"))

    # ── 우측 컬럼 (회사 / 직무 / 인용 / 연사 / 소속 / 참여 프로그램) ──────────
    items += [
        txt(COL_R, 0.096, COL_RW,
            [[{"t": d["name"], "font": "display_b", "color": accent}]],
            size=d["col_size"], spacing=1.0, tracking=-0.2),
        txt(COL_R, 0.140, COL_RW,
            [[{"t": d["roles"][0], "font": "display_sb", "color": INK}],
             [{"t": d["roles"][1], "font": "display_sb", "color": INK}]],
            size=12.5, spacing=1.55),
        txt(COL_R, 0.212, COL_RW,
            [[{"t": "“" + d["quote"][0], "font": "body", "color": BODY}],
             [{"t": d["quote"][1], "font": "body", "color": BODY}],
             [{"t": d["quote"][2] + "”", "font": "body", "color": BODY}]],
            size=11.5, spacing=1.60),
        bar(COL_R, 0.312, 0.042, 0.0018, INK),
        txt(COL_R, 0.330, COL_RW,
            [[{"t": d["speaker"], "font": "display_b", "color": INK}]],
            size=15.5, spacing=1.0, tracking=-0.2),
        txt(COL_R, 0.362, COL_RW,
            [[{"t": d["affil"], "font": "body", "color": GRAY}]],
            size=10.5, spacing=1.0),
        txt(COL_R, 0.390, COL_RW,
            [[{"t": "현직자 직무특강 ·", "font": "body", "color": "8A8A8A"}],
             [{"t": "1:1 취업멘토링", "font": "body", "color": "8A8A8A"}]],
            size=9.5, spacing=1.45, style="caption"),
    ]

    # ── 하단 일정 · 주최 · KNU ───────────────────────────────────────────────
    items += [
        # 일정은 한 줄로 길게 늘이지 않는다 — 인물 실루엣이 하단에서 왼쪽으로 벌어져서,
        # 폭을 못 줄이면 5종 중 4종이 글자를 덮는다 (배치 탐색이 해를 못 찾는다).
        bar(ML, 0.700, 0.250, 0.0012, RULE),
        txt(ML, 0.724, 0.50,
            [[{"t": "2026. 00. 00. (화)", "font": "display_sb", "color": INK}],
             [{"t": "10:00 – 16:00", "font": "display_sb", "color": INK}]],
            size=13.5, spacing=1.42, tracking=-0.1),
        txt(ML, 0.798, 0.50,
            [[{"t": "경북대학교 크리에이티브파크", "font": "display_sb", "color": INK}]],
            size=11.5, spacing=1.0, tracking=-0.1),
        txt(ML, 0.830, 0.50,
            [[{"t": "경북대학교 산학협력단 주최", "font": "body", "color": GRAY}]],
            size=10.5, spacing=1.0),
        # KNU 로고 자리 — 실제 로고 파일이 없어 가짜 엠블럼을 그리지 않고
        # 회사색 룰 + 타이포 락업으로 처리한다 (브리프 '주의' 항).
        bar(ML, 0.862, 0.0035, 0.056, accent),
        txt(0.079, 0.862, 0.30,
            [[{"t": "경북대학교", "font": "display_sb", "color": INK}]],
            size=12, spacing=1.0, tracking=0.2),
        txt(0.0775, 0.880, 0.30,
            [[{"t": "KNU", "font": "display_b", "color": INK}]],
            size=26, spacing=1.0, tracking=0.8),
    ]

    return {"page": 1, "theme": "jobfair-final", "variant": "paper",
            "page_size": "3:4", "theme_tokens": THEME_TOKENS, "items": items}


def main(only: list[str] | None = None) -> None:
    for i, d in enumerate(DECKS, start=1):
        if only and d["key"] not in only:
            continue
        pdir = PAGES / f"p{i:02d}"
        pdir.mkdir(parents=True, exist_ok=True)
        cut = ROOT / "projects" / "knu-jobfair-final" / "assets" / "spots"
        meta = json.loads((cut / f"cut-{d['key']}.json").read_text())
        spec = build(d, meta)
        spec["page"] = i
        (pdir / "layout_spec.json").write_text(
            json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        img = spec["items"][1]
        print(f"✓ p{i:02d} {d['name']} ({len(spec['items'])} items)  "
              f"인물 x{img['x']} y{img['y']} ×{img['w']}")
        for line in audit(meta, img["x"], img["y"], img["w"]):
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
