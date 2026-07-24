#!/usr/bin/env python3
"""결과보고서(결보) A4 세로 템플릿 4종 생성기.

4종은 색만 다른 게 아니라 골격 문법이 다르다:
  s5-crimson  KNU 크림슨 클래식 — 풀블리드 곡선 표지, 틴트 필 소제목 바, 대형 챕터 숫자
  s5-navygold 프리미엄 컨설팅   — 다크 네이비 표지+골드 프레임, 골드 짧은 언더바, 세리프 숫자 워터마크
  s5-govblue  관공서 정격       — 백지 표지+상단 컬러바, 로마숫자 챕터, 이중 헤어라인, 각진 네이비 필
  s5-teal     소셜/임팩트       — 페트롤 2분할 표지, 넘버 서클, 코랄 캡슐 소제목

좌표는 0~1 비율(A4 세로 540×780pt). 정사각 보정 SQ=0.692.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"

SQ = 540 / 780          # 정사각 도형의 y높이 = x폭 × SQ
PT = 1 / 780            # 1pt를 세로 비율로
L, R = 0.075, 0.925     # 좌우 마진
W = R - L

COVER_SRC = Path("/mnt/c/Users/hansb/Desktop/결보 템플릿/결보 표지 디자인/"
                 "ChatGPT Image 2026년 4월 28일 오후 01_36_47.png")


def pill_w(text, size, pad_pt=24):
    """pill 폭 실측 추정 — 렌더러 _pill_w는 한글 전각 기준이라 혼합 문자열에서 좁게 나온다.
    한글/전각 1.0em, 그 외 0.55em으로 환산 후 좌우 패딩을 더한다."""
    em = sum(1.0 if ord(ch) > 0x1100 else 0.55 for ch in text)
    return (em * size + pad_pt) / 540


def vc(y, h, size, spacing=1.45):
    """행 높이 h 안에서 size pt 한 줄을 세로 중앙에 두는 y."""
    return y + (h - size * spacing * PT) / 2


# ────────────────────────────────────────────────────────────── 템플릿 팔레트
CRIMSON = dict(
    slug="s5-crimson", theme="gyeolbo", label="KNU 크림슨 클래식",
    accent="D80C18", accent2="FC3E31", deep="8C0A12", ink="1A1A1A",
    body="3A3A3A", gray="76767A", hair="E6E7E9", tint="FDF0F0", tint2="F9DCDD",
    on_dark="FFFFFF", dark_sub="F5B9BC", bg="FFFFFF", arrow_gray="C9CBD0",
    hdr_grad=["FC3E31", "D80C18"], hdr_fill=None, hdr_fg="FFFFFF",
    emblem="emblem_crimson.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png",
)
NAVYGOLD = dict(
    slug="s5-navygold", theme="goldnavy", label="프리미엄 네이비·골드",
    accent="C8912F", accent2="E0B25C", deep="1B2A4A", ink="1B2A4A",
    body="3A4358", gray="7A7E8C", hair="E2DCCB", tint="F5F2EA", tint2="EFE9DA",
    on_dark="F5F2EA", dark_sub="B9A67C", bg="FDFBF6", arrow_gray="C2BBA6",
    hdr_grad=None, hdr_fill="1B2A4A", hdr_fg="F5F2EA",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png",
)
GOVBLUE = dict(
    slug="s5-govblue", theme="govblue", label="관공서 정격 블루",
    accent="2E75B6", accent2="5B9BD5", deep="1F4E79", ink="1F4E79",
    body="333333", gray="6E7787", hair="DDE4EE", tint="EBF3FA", tint2="D7E7F5",
    on_dark="FFFFFF", dark_sub="9FC0E0", bg="FFFFFF", arrow_gray="AFBFD6",
    hdr_grad=None, hdr_fill="1F4E79", hdr_fg="FFFFFF",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png",
)
TEAL = dict(
    slug="s5-teal", theme="tealcoral", label="소셜 임팩트 페트롤·코랄",
    accent="EF7B68", accent2="F5A492", deep="10577D", ink="143B4E",
    body="2E4653", gray="7C8890", hair="E4DFD1", tint="EAF1F5", tint2="D9E5EB",
    on_dark="FAF7EF", dark_sub="9FC3D4", bg="FAF7EF", arrow_gray="BFC8CC",
    hdr_grad=None, hdr_fill="10577D", hdr_fg="FFFFFF",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png",
)

# ────────────────────────────────────────────────────────────── 공통 샘플 내용
EVENT = "2026 지역 상생 아카데미"
ORG = "경북대학교 지식재산전문인력양성사업단"
ORG_SHORT = "지식재산전문인력양성사업단"

CHAPTERS = [
    ("01", "Ⅰ", "과업추진 개요", "CHAPTER 01",
     "본 장에서는 과업의 목적과 추진 배경, 운영 개요와 핵심 성과 지표를 요약한다.\n"
     "세부 일정과 인력 구성은 이어지는 절에 정리하였다."),
    ("02", "Ⅱ", "과업 수행 내역", "CHAPTER 02",
     "모집·홍보부터 사전 준비, 현장 운영까지 과업 수행의 전 과정을 시간 순으로 기술한다.\n"
     "각 단계의 산출물과 점검 결과를 함께 제시한다."),
    ("03", "Ⅲ", "과업 수행 결과", "CHAPTER 03",
     "참여 현황과 만족도 조사 결과, 참여자 의견을 정리하고 증빙 자료를 첨부한다.\n"
     "목표 대비 달성률을 지표별로 대조하였다."),
    ("04", "Ⅳ", "산출 내역", "CHAPTER 04",
     "과업 수행에 소요된 예산의 집행 내역과 정산 결과를 항목별로 제시한다.\n"
     "증빙 서류는 별첨으로 제출한다."),
]

OVERVIEW = [
    ("행 사 명", f"「{EVENT}」 역량강화 프로그램"),
    ("운영 기간", "2026. 05. 12.(화) ~ 06. 20.(금) / 총 6주, 12회차"),
    ("운영 장소", "경북대학교 글로벌플라자 2층 세미나실 (대구광역시 북구 대학로 80)"),
    ("참여 대상", "지역 시민 및 재직자 40명 (1일 2회차, 회차당 20명)"),
    ("주최 · 주관", "대구광역시 · 경북대학교 지식재산전문인력양성사업단"),
    ("수행 기관", "모드어스 스튜디오 (계약 제2026-0512호)"),
]

KPI = [("128", "명", "총 참여 인원", "목표 120명 대비 106.7%"),
       ("89.1", "%", "수 료 율", "수료 기준 12시간 이상 이수"),
       ("4.6", "/5.0", "종합 만족도", "설문 응답 114부 기준")]

SCHEDULE = [
    ("기획 · 계약", "04.14 ~ 04.30", "■■□□□□", "운영계획 수립, 계약 체결"),
    ("모집 · 홍보", "05.01 ~ 05.09", "□■■□□□", "채널 게시, 신청 접수·선발"),
    ("사전 준비", "05.04 ~ 05.11", "□■■□□□", "교재 제작, 강사 계약, 장소 점검"),
    ("현장 운영", "05.12 ~ 06.20", "□□■■■□", "12회차 강의 운영, 출결 관리"),
    ("결과 정리", "06.21 ~ 06.30", "□□□□■■", "만족도 분석, 결과보고서 제출"),
]

STAFF = [
    ("총괄 책임", "사업단 단장", "과업 총괄 및 대외 협의", "1명"),
    ("운영 실무", "사업단 전임연구원", "일정·예산 관리, 현장 총괄", "2명"),
    ("강사진", "외부 전문가", "회차별 강의 및 실습 지도", "4명"),
    ("현장 지원", "학부 근로장학생", "출결·설문·기자재 지원", "3명"),
]

PROMO = [
    ("기관 누리집", "05.01 ~ 05.09", "3건", "1,240회"),
    ("SNS (인스타그램)", "05.01 ~ 05.09", "6건", "3,870회"),
    ("지역 커뮤니티 카페", "05.02 ~ 05.08", "4건", "2,150회"),
    ("현수막 · 포스터", "05.01 ~ 05.12", "12개소", "—"),
]

PREP = [
    ("01", "교재 · 실습자료 제작", "회차별 워크북 12종, 실습 데이터셋 4종 사전 검수 완료"),
    ("02", "강사 섭외 및 계약", "분야별 전문가 4인 위촉, 강의계획서 사전 검토"),
    ("03", "장소 · 기자재 점검", "좌석 배치 20석, 노트북 20대, 네트워크 사전 테스트"),
    ("04", "안전 · 운영 매뉴얼", "비상 연락망, 출결·설문 절차 표준화 및 사전 교육"),
]

TIMETABLE = [
    ("13:00", "등록 및 오리엔테이션 — 출결 확인, 교재 배부"),
    ("13:20", "1교시 이론 강의 — 주제별 핵심 개념과 사례 분석"),
    ("14:20", "휴식 (10분)"),
    ("14:30", "2교시 실습 — 개인별 과제 수행 및 강사 첨삭"),
    ("15:40", "질의응답 및 회차 정리 — 만족도 설문 작성"),
    ("16:00", "종료 및 차시 안내"),
]

SATIS = [("강의 내용의 유익성", 4.7), ("강사의 전달력", 4.8),
         ("실습 시간의 적정성", 4.4), ("운영·안내의 원활함", 4.6),
         ("재참여 의향", 4.5)]

RESULT_TBL = [
    ("참여 인원", "120명", "128명", "106.7%"),
    ("수료 인원", "100명", "114명", "114.0%"),
    ("운영 회차", "12회차", "12회차", "100.0%"),
    ("만족도 (5점)", "4.0 이상", "4.6", "115.0%"),
]

VOICES = [
    ("실습 위주로 진행되어 바로 업무에 적용해 볼 수 있었습니다.\n특히 회차마다 첨삭을 받은 점이 가장 도움이 되었습니다.",
     "3회차 참여자 A"),
    ("처음에는 어렵게 느껴졌지만 단계별로 따라가니 끝까지 완주할 수 있었습니다.\n다음 심화 과정도 개설되면 다시 참여하고 싶습니다.",
     "8회차 참여자 B"),
]

PHOTOS = ["개강식 및 오리엔테이션 진행", "회차별 이론 강의 운영",
          "조별 실습 및 강사 첨삭", "수료식 및 기념 촬영"]

BUDGET = [
    ("강사료", "4인 × 12회차", "14,400,000", "14,400,000", "—"),
    ("교재 · 실습자료", "40부 × 12종", "3,600,000", "3,540,000", "60,000"),
    ("장소 · 기자재 임차", "12회차", "2,400,000", "2,400,000", "—"),
    ("운영 인건비", "3인 × 6주", "5,400,000", "5,400,000", "—"),
    ("홍보 · 인쇄", "포스터·현수막", "1,200,000", "1,160,000", "40,000"),
]
BUDGET_SUM = ("합    계", "", "27,000,000", "26,900,000", "100,000")


# ────────────────────────────────────────────────────────────── 공통 프리미티브
def running_head(T, chapter_no, chapter_title, page_no):
    """상·하단 러닝헤드 — 템플릿마다 문법이 다르다."""
    it = []
    s = T["slug"]
    if s == "s5-crimson":
        it += [
            {"type": "text", "text": f"「{EVENT}」 결과보고서", "x": L, "y": 0.0235,
             "w": 0.5, "style": "caption", "size": 8, "color": T["gray"]},
            {"type": "text", "text": ORG_SHORT, "x": 0.5, "y": 0.0225, "w": W - 0.425,
             "align": "right", "style": "cardtitle", "size": 9, "color": T["ink"]},
            {"type": "hairline", "x": L, "y": 0.0455, "w": W, "color": T["hair"]},
            {"type": "card", "x": L, "y": 0.9535, "w": 0.018, "h": 0.0075,
             "fill": T["accent"], "radius": 0.0},
            {"type": "text", "text": f"{chapter_no}  {chapter_title}".strip(), "x": L + 0.028,
             "y": 0.9495, "w": 0.5, "style": "caption", "size": 8, "color": T["gray"]},
            {"type": "text", "text": f"- {page_no} -", "x": 0.6, "y": 0.9495,
             "w": W - 0.525, "align": "right", "style": "caption", "size": 8,
             "color": T["gray"]},
        ]
    elif s == "s5-navygold":
        it += [
            {"type": "hairline", "x": L, "y": 0.042, "w": W, "color": T["accent"],
             "thick": 0.8},
            {"type": "text", "text": f"{EVENT}  |  결과보고서", "x": L, "y": 0.0215,
             "w": 0.6, "style": "caption", "size": 8, "color": T["gray"]},
            {"type": "text", "text": f"CHAPTER {chapter_no}", "x": 0.55, "y": 0.0215,
             "w": W - 0.475, "align": "right", "style": "caption", "size": 7.5,
             "color": T["accent"]},
            {"type": "hairline", "x": L, "y": 0.9505, "w": W, "color": T["hair"]},
            {"type": "text", "text": ORG_SHORT, "x": L, "y": 0.9565, "w": 0.6,
             "style": "caption", "size": 7.5, "color": T["gray"]},
            {"type": "text", "text": page_no, "x": 0.6, "y": 0.9555, "w": W - 0.525,
             "align": "right", "style": "cardtitle", "size": 9.5, "color": T["accent"]},
        ]
    elif s == "s5-govblue":
        it += [
            {"type": "card", "x": L, "y": 0.0225, "w": 0.004, "h": 0.019,
             "fill": T["deep"], "radius": 0.0},
            {"type": "text", "text": f"「{EVENT}」 결과보고서", "x": L + 0.014, "y": 0.0225,
             "w": 0.55, "style": "caption", "size": 8, "color": T["deep"]},
            {"type": "text", "text": ORG_SHORT, "x": 0.55, "y": 0.0225, "w": W - 0.475,
             "align": "right", "style": "caption", "size": 8, "color": T["gray"]},
            {"type": "hairline", "x": L, "y": 0.0455, "w": W, "color": T["deep"],
             "thick": 1.8},
            {"type": "hairline", "x": L, "y": 0.0485, "w": W, "color": T["accent2"]},
            {"type": "hairline", "x": L, "y": 0.9455, "w": W, "color": T["accent2"]},
            {"type": "hairline", "x": L, "y": 0.9485, "w": W, "color": T["deep"],
             "thick": 1.8},
            {"type": "text", "text": (f"{chapter_no}. {chapter_title}" if chapter_no
                                       else chapter_title), "x": L,
             "y": 0.9555, "w": 0.5, "style": "caption", "size": 8, "color": T["gray"]},
            {"type": "text", "text": f"- {page_no} -", "x": 0.4, "y": 0.9555,
             "w": 0.2, "align": "center", "style": "caption", "size": 8.5,
             "color": T["deep"]},
        ]
    else:  # s5-teal
        it += [
            {"type": "pill", "x": L, "y": 0.0205, "h": 0.0225,
             "text": f"{chapter_no}  {chapter_title}", "size": 8,
             "w": pill_w(f"{chapter_no}  {chapter_title}", 8, 20),
             "fill": T["tint2"], "text_color": T["deep"]},
            {"type": "text", "text": f"「{EVENT}」 결과보고서", "x": 0.45, "y": 0.0235,
             "w": W - 0.375, "align": "right", "style": "caption", "size": 8,
             "color": T["gray"]},
            {"type": "hairline", "x": L, "y": 0.9495, "w": W, "color": T["hair"]},
            {"type": "text", "text": ORG_SHORT, "x": L, "y": 0.9565, "w": 0.6,
             "style": "caption", "size": 7.5, "color": T["gray"]},
            {"type": "chip", "x": R - 0.032, "y": 0.9525, "d": 0.032,
             "text": page_no, "fill": T["deep"], "text_color": "FFFFFF"},
        ]
    return it


def chapter_head(T, idx, y=0.075):
    """챕터 헤더. (items, 본문 시작 y)를 반환."""
    num, roman, title, cap, lead = CHAPTERS[idx]
    s = T["slug"]
    it = []
    if s == "s5-crimson":
        it += [
            {"type": "text", "text": num, "x": L - 0.008, "y": y, "w": 0.15,
             "style": "num_xl", "size": 40, "color": T["accent"]},
            {"type": "text", "text": "CHAPTER", "x": L - 0.005, "y": y + 0.076,
             "w": 0.12, "style": "caption", "size": 8, "color": T["accent"]},
            {"type": "arrow", "x": L + 0.083, "y": y + 0.079, "w": 0.032, "h": 0.007,
             "color": T["accent"]},
            {"type": "headline", "lines": [title], "x": 0.24, "y": y + 0.004,
             "w": 0.66, "size": 26, "color": T["accent"]},
            {"type": "text", "text": lead, "x": 0.242, "y": y + 0.062, "w": 0.66,
             "style": "body", "size": 9.5, "spacing": 1.55, "color": T["body"]},
        ]
        return it, y + 0.170
    if s == "s5-navygold":
        it += [
            {"type": "text", "text": num, "x": 0.70, "y": y - 0.018, "w": 0.23,
             "align": "right", "style": "num_xl", "size": 62, "color": T["tint2"]},
            {"type": "text", "text": cap, "x": L, "y": y + 0.004, "w": 0.4,
             "style": "caption", "size": 8.5, "color": T["accent"]},
            {"type": "hairline", "x": L, "y": y + 0.030, "w": 0.052,
             "color": T["accent"], "thick": 2.6},
            {"type": "headline", "lines": [title], "x": L - 0.004, "y": y + 0.040,
             "w": 0.6, "size": 25, "color": T["ink"]},
            {"type": "text", "text": lead, "x": L, "y": y + 0.098, "w": 0.66,
             "style": "body", "size": 9.5, "spacing": 1.55, "color": T["body"]},
        ]
        return it, y + 0.170
    if s == "s5-govblue":
        it += [
            {"type": "text", "text": f"{roman}.  {title}", "x": L, "y": y + 0.008,
             "w": 0.7, "style": "headline", "size": 22, "color": T["deep"]},
            {"type": "text", "text": cap, "x": 0.6, "y": y + 0.020, "w": W - 0.525,
             "align": "right", "style": "caption", "size": 8, "color": T["accent"]},
            {"type": "hairline", "x": L, "y": y + 0.055, "w": W, "color": T["deep"],
             "thick": 1.6},
            {"type": "hairline", "x": L, "y": y + 0.0578, "w": W, "color": T["accent2"]},
            {"type": "text", "text": lead, "x": L, "y": y + 0.070, "w": 0.80,
             "style": "body", "size": 9.5, "spacing": 1.55, "color": T["body"]},
        ]
        return it, y + 0.170
    # s5-teal
    it += [
        {"type": "chip", "x": L, "y": y, "d": 0.062, "text": num,
         "fill": T["deep"], "text_color": "FFFFFF"},
        {"type": "text", "text": cap, "x": L + 0.082, "y": y + 0.002, "w": 0.4,
         "style": "caption", "size": 8.5, "color": T["accent"]},
        {"type": "headline", "lines": [title], "x": L + 0.078, "y": y + 0.020,
         "w": 0.66, "size": 24, "color": T["deep"]},
        {"type": "text", "text": lead, "x": L, "y": y + 0.086, "w": 0.70,
         "style": "body", "size": 9.5, "spacing": 1.55, "color": T["body"]},
    ]
    return it, y + 0.170


def section(T, y, title, note=None):
    """절 소제목 바. (items, 다음 콘텐츠 y)를 반환."""
    s = T["slug"]
    it = []
    if s == "s5-crimson":
        it += [
            {"type": "card", "x": L, "y": y, "w": W, "h": 0.029, "fill": T["tint"],
             "outline": T["accent"], "radius": 0.5},
            {"type": "image", "path": f"assets/brand/{T['emblem']}", "x": L + 0.012,
             "y": y + 0.0035, "w": 0.022, "h": 0.022 * SQ},
            {"type": "text", "text": title, "x": L + 0.044, "y": vc(y, 0.029, 10.5),
             "w": 0.5, "style": "cardtitle", "size": 10.5, "color": T["accent"]},
        ]
    elif s == "s5-navygold":
        it += [
            {"type": "text", "text": title, "x": L, "y": y, "w": 0.6,
             "style": "cardtitle", "size": 11, "color": T["ink"]},
            {"type": "hairline", "x": L, "y": y + 0.0245, "w": 0.042,
             "color": T["accent"], "thick": 2.4},
            {"type": "hairline", "x": L + 0.048, "y": y + 0.0252, "w": W - 0.048,
             "color": T["hair"]},
        ]
        y -= 0.002
    elif s == "s5-govblue":
        it += [
            {"type": "band", "x": L, "y": y, "w": W, "h": 0.028, "fill": T["deep"],
             "radius": 0.0, "label": "▪", "label_color": T["accent2"],
             "text": title, "text_color": "FFFFFF", "size": 10.5, "label_size": 9,
             "align": "left", "pad": 0.014},
        ]
    else:
        it += [
            {"type": "pill", "x": L, "y": y, "h": 0.028, "text": title, "size": 10,
             "w": pill_w(title, 10), "fill": T["accent"], "text_color": "FFFFFF"},
            {"type": "hairline", "x": L, "y": y + 0.034, "w": W, "color": T["hair"]},
        ]
    if note:
        # 짙은 필 바(govblue) 위에서는 회색 각주가 묻힌다 — 밝은 톤으로
        note_color = T["dark_sub"] if s == "s5-govblue" else T["gray"]
        it.append({"type": "text", "text": note, "x": 0.50, "y": vc(y, 0.029, 8.5),
                   "w": R - 0.522, "align": "right", "style": "caption", "size": 8,
                   "color": note_color})
    return it, y + 0.046


def table(T, x, y, w, colw, header, rows, row_h=0.0285, hdr_h=0.031,
          aligns=None, size=9.3, tint_col=None, sum_row=None):
    """가로선 위주 문서형 표. (items, 표 하단 y) 반환."""
    aligns = aligns or ["left"] * len(colw)
    xs, acc = [], 0.0
    for cw in colw:
        xs.append(x + acc * w)
        acc += cw
    it = []
    hdr = {"type": "card", "x": x, "y": y, "w": w, "h": hdr_h, "radius": 0.0}
    if T["hdr_grad"]:
        hdr["fill"] = T["hdr_grad"][0]
        hdr["grad"] = T["hdr_grad"]
    else:
        hdr["fill"] = T["hdr_fill"]
    it.append(hdr)
    for i, (cx, cw, hd) in enumerate(zip(xs, colw, header)):
        pad = 0.012 if aligns[i] == "left" else 0.0
        it.append({"type": "text", "text": hd, "x": cx + pad,
                   "y": vc(y, hdr_h, size), "w": cw * w - pad * 2,
                   "align": aligns[i], "style": "cardtitle", "size": size,
                   "color": T["hdr_fg"]})
    ry = y + hdr_h
    body_rows = list(rows) + ([sum_row] if sum_row else [])
    for r_i, row in enumerate(body_rows):
        is_sum = sum_row is not None and r_i == len(body_rows) - 1
        if is_sum:
            it.append({"type": "card", "x": x, "y": ry, "w": w, "h": row_h,
                       "fill": T["tint2"], "radius": 0.0})
        elif tint_col is not None:
            it.append({"type": "card", "x": xs[tint_col], "y": ry,
                       "w": colw[tint_col] * w, "h": row_h, "fill": T["tint"],
                       "radius": 0.0})
        for i, (cx, cw, cell) in enumerate(zip(xs, colw, row)):
            pad = 0.012 if aligns[i] == "left" else 0.0
            strong = is_sum or (tint_col is not None and i == tint_col)
            it.append({"type": "text", "text": cell, "x": cx + pad,
                       "y": vc(ry, row_h, size), "w": cw * w - pad * 2,
                       "align": aligns[i],
                       "style": "cardtitle" if strong else "body", "size": size,
                       "color": T["ink"] if strong else T["body"]})
        it.append({"type": "hairline", "x": x, "y": ry + row_h - 0.0006, "w": w,
                   "color": T["hair"] if not is_sum else T["gray"]})
        ry += row_h
    return it, ry


def kpi_row(T, y, h=0.116):
    """빅넘버 3연타 카드."""
    it = []
    gap = 0.018
    cw = (W - gap * 2) / 3
    for i, (num, unit, label, note) in enumerate(KPI):
        cx = L + i * (cw + gap)
        first = i == 0
        if T["slug"] == "s5-navygold":
            it += [{"type": "card", "x": cx, "y": y, "w": cw, "h": h,
                    "fill": T["tint"] if not first else T["deep"], "radius": 0.06,
                    "outline": T["hair"] if not first else None}]
        elif T["slug"] == "s5-govblue":
            it += [{"type": "card", "x": cx, "y": y, "w": cw, "h": h,
                    "fill": T["tint"] if not first else T["deep"], "radius": 0.0}]
        else:
            it += [{"type": "card", "x": cx, "y": y, "w": cw, "h": h,
                    "fill": T["tint"] if not first else T["deep"], "radius": 0.10}]
        fg = "FFFFFF" if first else T["ink"]
        sub = T["dark_sub"] if first else T["gray"]
        acc = "FFFFFF" if first else T["accent"]
        it += [
            {"type": "text", "text": label, "x": cx + 0.018, "y": y + 0.014,
             "w": cw - 0.036, "style": "caption", "size": 8.5, "color": sub},
            {"type": "text", "runs": [[{"t": num, "color": acc, "font": "display_b",
                                        "size": 27},
                                       {"t": " " + unit, "color": fg,
                                        "font": "body_sb", "size": 11}]],
             "x": cx + 0.017, "y": y + 0.037, "w": cw - 0.03, "style": "body"},
            {"type": "hairline", "x": cx + 0.018, "y": y + 0.090,
             "w": cw - 0.036, "color": T["accent2"] if first else T["hair"]},
            {"type": "text", "text": note, "x": cx + 0.018, "y": y + 0.0955,
             "w": cw - 0.03, "style": "caption", "size": 7.5, "color": sub},
        ]
    return it, y + h


def number_chain(T, y, steps):
    """넘버 서클 체인 + 아래 해설 카드 (CLAUDE.md 규칙 8)."""
    it = []
    n = len(steps)
    d = 0.044
    span = W / n
    line_y = y + d * SQ / 2
    it.append({"type": "hairline", "x": L + span / 2, "y": line_y,
               "w": W - span, "color": T["hair"], "thick": 2.5})
    card_y = y + 0.075
    card_h = 0.095
    gap = 0.014
    cw = (W - gap * (n - 1)) / n
    for i, (num, name, desc) in enumerate(steps):
        cx = L + i * span + span / 2
        it.append({"type": "chip", "x": cx - d / 2, "y": y, "d": d, "text": num,
                   "fill": T["deep"] if i < 2 else T["accent"],
                   "text_color": "FFFFFF"})
        it.append({"type": "text", "text": name, "x": cx - span / 2, "y": y + 0.040,
                   "w": span, "align": "center", "style": "cardtitle", "size": 10,
                   "color": T["ink"]})
        bx = L + i * (cw + gap)
        it.append({"type": "card", "x": bx, "y": card_y, "w": cw, "h": card_h,
                   "fill": T["tint"], "radius": 0.08 if T["slug"] == "s5-teal" else 0.05})
        it.append({"type": "text", "text": desc, "x": bx + 0.014, "y": card_y + 0.014,
                   "w": cw - 0.028, "style": "body", "size": 8.8, "spacing": 1.5,
                   "color": T["body"]})
    return it, card_y + card_h


def bars_block(T, x, y, w, rows, row_h=0.030, maxv=5.0):
    """가로 막대 — 라벨 + 바 + 수치."""
    it = []
    label_w = 0.20
    span = w - label_w - 0.062
    for i, (label, v) in enumerate(rows):
        ry = y + i * row_h
        it.append({"type": "text", "text": label, "x": x, "y": vc(ry, row_h, 9),
                   "w": label_w - 0.01, "style": "body", "size": 9,
                   "color": T["body"]})
        bh = 0.0135
        by = ry + (row_h - bh) / 2
        it.append({"type": "card", "x": x + label_w, "y": by, "w": span, "h": bh,
                   "fill": T["tint"], "radius": 0.5})
        bw = span * v / maxv
        it.append({"type": "card", "x": x + label_w, "y": by, "w": bw, "h": bh,
                   "fill": T["accent"], "radius": 0.5})
        it.append({"type": "text", "text": f"{v:.1f}", "x": x + label_w + span + 0.010,
                   "y": vc(ry, row_h, 9), "w": 0.05, "style": "cardtitle", "size": 9,
                   "color": T["accent"]})
    return it, y + row_h * len(rows)


def photo_grid(T, y, cols=2, rows=2, captions=None):
    """증빙 사진 슬롯 — 교표 워터마크 카드 + 캡션 (회색 IMAGE 박스 금지)."""
    captions = captions or PHOTOS
    it = []
    gap = 0.022
    cw = (W - gap * (cols - 1)) / cols
    ch = cw * (2 / 3) * SQ    # 3:2 크롭 (정사각 보정 필수 — 안 하면 세로로 늘어난다)
    cap_h = 0.026
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        cx = L + c * (cw + gap)
        cy = y + r * (ch + cap_h + 0.026)
        it += [
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": ch, "fill": T["tint"],
             "radius": 0.04 if T["slug"] != "s5-govblue" else 0.0,
             "outline": T["hair"]},
            {"type": "image", "path": f"assets/brand/{T['emblem_wm']}",
             "x": cx + cw / 2 - 0.055, "y": cy + ch / 2 - 0.055 * SQ * 1.0,
             "w": 0.11, "h": 0.11 * SQ},
            {"type": "text", "text": "사진 삽입 영역", "x": cx, "y": cy + ch - 0.030,
             "w": cw, "align": "center", "style": "caption", "size": 7.5,
             "color": T["gray"]},
            {"type": "band", "x": cx, "y": cy + ch + 0.006, "w": cw, "h": cap_h,
             "fill": T["bg"], "radius": 0.0, "label": "▲",
             "label_color": T["accent"], "sep": "  ",
             "text": f"[사진 {i + 1}] {captions[i]}", "text_color": T["body"],
             "size": 8.5, "label_size": 8, "align": "center", "pad": 0.008},
        ]
    return it, y + rows * (ch + cap_h + 0.026)


def closing_band(T, y):
    """마무리 선언 밴드 + 서명행."""
    it = []
    text = "위와 같이 과업을 계획된 일정과 범위에 따라 정상적으로 완료하였음을 보고합니다."
    if T["slug"] == "s5-crimson":
        it.append({"type": "card", "x": L, "y": y, "w": W, "h": 0.052,
                   "fill": T["accent2"], "grad": [T["accent2"], T["accent"]],
                   "radius": 0.06})
    elif T["slug"] == "s5-navygold":
        it += [{"type": "card", "x": L, "y": y, "w": W, "h": 0.052,
                "fill": T["deep"], "radius": 0.03},
               {"type": "hairline", "x": L + 0.014, "y": y + 0.0455, "w": W - 0.028,
                "color": T["accent"], "thick": 0.9}]
    elif T["slug"] == "s5-govblue":
        it.append({"type": "card", "x": L, "y": y, "w": W, "h": 0.052,
                   "fill": T["deep"], "radius": 0.0})
    else:
        it.append({"type": "card", "x": L, "y": y, "w": W, "h": 0.052,
                   "fill": T["deep"], "radius": 0.12})
    it.append({"type": "text", "text": text, "x": L + 0.03,
               "y": vc(y, 0.052, 10.5), "w": W - 0.06, "align": "center",
               "style": "cardtitle", "size": 10.5, "color": "FFFFFF"})
    sy = y + 0.074
    it += [
        {"type": "text", "text": "2026.  06.  30.", "x": 0.40, "y": sy, "w": R - 0.40,
         "align": "right", "style": "cardtitle", "size": 10.5, "color": T["ink"]},
        {"type": "text", "text": ORG, "x": 0.40, "y": sy + 0.028, "w": R - 0.40,
         "align": "right", "style": "headline", "size": 13.5, "color": T["ink"]},
        {"type": "text", "text": "수행기관  모드어스 스튜디오        (인)", "x": 0.40,
         "y": sy + 0.058, "w": R - 0.40, "align": "right", "style": "body",
         "size": 9.5, "color": T["gray"]},
    ]
    return it, sy + 0.084


# ────────────────────────────────────────────────────────────── 페이지 빌더
def page_cover(T):
    s = T["slug"]
    it = []
    if s == "s5-crimson":
        it += [
            {"type": "image", "path": "assets/cover_bg.png", "x": 0.0, "y": 0.0,
             "w": 1.0, "h": 1.0},
            {"type": "image", "path": f"assets/brand/{T['emblem']}", "x": L,
             "y": 0.072, "w": 0.085, "h": 0.085 * SQ},
            {"type": "text", "text": "경북대학교", "x": L + 0.10, "y": 0.086,
             "w": 0.4, "style": "cardtitle", "size": 13, "color": T["ink"]},
            {"type": "text", "text": "KYUNGPOOK NATIONAL UNIVERSITY", "x": L + 0.101,
             "y": 0.107, "w": 0.5, "style": "caption", "size": 7,
             "color": T["gray"]},
            {"type": "text", "text": f"「{EVENT}」 역량강화 프로그램", "x": L,
             "y": 0.412, "w": 0.62, "style": "cardtitle", "size": 12.5,
             "color": T["accent"]},
            {"type": "headline", "lines": ["결과보고서"], "x": L - 0.006, "y": 0.443,
             "w": 0.7, "size": 46, "color": T["ink"]},
            {"type": "hairline", "x": L, "y": 0.536, "w": 0.20, "color": T["accent"],
             "thick": 2.8},
            {"type": "text", "text": "프로그램 운영 결과 및 성과 요약",
             "x": L, "y": 0.552, "w": 0.6, "style": "sub", "size": 11.5,
             "color": T["gray"]},
        ]
        rows = [("주최", "대구광역시"), ("주관", ORG),
                ("수행", "모드어스 스튜디오"), ("기간", "2026. 05. 12. ~ 06. 20.")]
        ry = 0.700
        for lab, val in rows:
            it += [
                {"type": "pill", "x": L, "y": ry, "h": 0.026, "w": 0.048,
                 "text": lab, "size": 8.5, "fill": T["accent"],
                 "text_color": "FFFFFF"},
                {"type": "text", "text": val, "x": L + 0.066,
                 "y": vc(ry, 0.026, 10), "w": 0.6, "style": "body", "size": 10,
                 "color": T["body"]},
                {"type": "hairline", "x": L, "y": ry + 0.034, "w": 0.56,
                 "color": T["hair"]},
            ]
            ry += 0.046
        it.append({"type": "text", "text": "2026. 06.", "x": L, "y": 0.905,
                   "w": 0.4, "style": "cardtitle", "size": 10.5, "color": T["ink"]})
        return it

    if s == "s5-navygold":
        it += [
            {"type": "card", "x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0,
             "fill": T["deep"], "radius": 0.0},
            {"type": "shape", "shape": "rounded", "x": 0.055, "y": 0.038,
             "w": 0.89, "h": 0.924, "adj": [0.0], "fill": "none",
             "outline": T["accent"], "outline_w": 1.0},
            # 골드 코너 악센트
            {"type": "card", "x": 0.055, "y": 0.038, "w": 0.16, "h": 0.0055,
             "fill": T["accent2"], "radius": 0.0},
            {"type": "card", "x": 0.785, "y": 0.9565, "w": 0.16, "h": 0.0055,
             "fill": T["accent2"], "radius": 0.0},
            {"type": "image", "path": f"assets/brand/{T['emblem_white']}",
             "x": 0.5 - 0.048, "y": 0.128, "w": 0.096, "h": 0.096 * SQ},
            {"type": "text", "text": "K Y U N G P O O K   N A T I O N A L   U N I V E R S I T Y",
             "x": 0.15, "y": 0.216, "w": 0.70, "align": "center", "style": "caption",
             "size": 7.5, "color": T["dark_sub"]},
            {"type": "hairline", "x": 0.44, "y": 0.262, "w": 0.12,
             "color": T["accent"], "thick": 1.4},
            {"type": "text", "text": f"「{EVENT}」", "x": 0.12, "y": 0.336, "w": 0.76,
             "align": "center", "style": "cardtitle", "size": 13,
             "color": T["accent2"]},
            {"type": "text", "text": "역량강화 프로그램", "x": 0.12, "y": 0.364,
             "w": 0.76, "align": "center", "style": "body", "size": 11,
             "color": T["dark_sub"]},
            {"type": "headline", "lines": ["결 과 보 고 서"], "x": 0.1, "y": 0.424,
             "w": 0.80, "align": "center", "size": 40, "color": "FFFFFF"},
            {"type": "hairline", "x": 0.40, "y": 0.522, "w": 0.20,
             "color": T["accent"], "thick": 2.6},
            {"type": "text", "text": "RESULT  REPORT", "x": 0.12, "y": 0.540,
             "w": 0.76, "align": "center", "style": "caption", "size": 8.5,
             "color": T["dark_sub"]},
        ]
        rows = [("주    최", "대구광역시"), ("주    관", ORG),
                ("수행기관", "모드어스 스튜디오"),
                ("운영기간", "2026. 05. 12. ~ 06. 20.")]
        ry = 0.700
        for lab, val in rows:
            it += [
                {"type": "text", "text": lab, "x": 0.255, "y": ry, "w": 0.13,
                 "style": "cardtitle", "size": 9.5, "color": T["accent"]},
                {"type": "text", "text": val, "x": 0.395, "y": ry, "w": 0.42,
                 "style": "body", "size": 9.5, "color": "FFFFFF"},
            ]
            ry += 0.038
        it.append({"type": "text", "text": "2026.  06.", "x": 0.12, "y": 0.888,
                   "w": 0.76, "align": "center", "style": "cardtitle", "size": 10.5,
                   "color": T["accent2"]})
        return it

    if s == "s5-govblue":
        it += [
            {"type": "card", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.052,
             "fill": T["deep"], "radius": 0.0},
            {"type": "card", "x": 0.0, "y": 0.052, "w": 1.0, "h": 0.008,
             "fill": T["accent"], "radius": 0.0},
            {"type": "text", "text": "대구광역시 지역성장 인재양성체계(앵커) 사업",
             "x": L, "y": vc(0.0, 0.052, 9.5), "w": 0.7, "style": "cardtitle",
             "size": 9.5, "color": "FFFFFF"},
            {"type": "text", "text": "문서번호  2026-지식재산-0630", "x": 0.5,
             "y": vc(0.0, 0.052, 8.5), "w": W - 0.425, "align": "right",
             "style": "caption", "size": 8.5, "color": T["dark_sub"]},
            {"type": "card", "x": L, "y": 0.175, "w": W, "h": 0.0045,
             "fill": T["deep"], "radius": 0.0},
            {"type": "text", "text": f"「{EVENT}」", "x": L, "y": 0.212, "w": W,
             "align": "center", "style": "cardtitle", "size": 14,
             "color": T["accent"]},
            {"type": "text", "text": "역량강화 프로그램 운영", "x": L, "y": 0.243,
             "w": W, "align": "center", "style": "body", "size": 11.5,
             "color": T["gray"]},
            {"type": "headline", "lines": ["결 과 보 고 서"], "x": L, "y": 0.300,
             "w": W, "align": "center", "size": 38, "color": T["deep"]},
            {"type": "card", "x": 0.38, "y": 0.398, "w": 0.24, "h": 0.005,
             "fill": T["accent"], "radius": 0.0},
            {"type": "card", "x": L, "y": 0.430, "w": W, "h": 0.0045,
             "fill": T["deep"], "radius": 0.0},
            {"type": "image", "path": f"assets/brand/{T['emblem_wm']}",
             "x": 0.5 - 0.085, "y": 0.487, "w": 0.17, "h": 0.17 * SQ},
        ]
        rows = [("주    최", "대구광역시"), ("주    관", ORG),
                ("수 행 기 관", "모드어스 스튜디오"),
                ("운 영 기 간", "2026. 05. 12.(화) ~ 06. 20.(금)"),
                ("제 출 일", "2026. 06. 30.")]
        ty = 0.660
        it.append({"type": "card", "x": 0.16, "y": ty, "w": 0.68, "h": 0.0045,
                   "fill": T["deep"], "radius": 0.0})
        ry = ty + 0.0125
        for lab, val in rows:
            it += [
                {"type": "card", "x": 0.16, "y": ry, "w": 0.20, "h": 0.036,
                 "fill": T["tint"], "radius": 0.0},
                {"type": "text", "text": lab, "x": 0.16, "y": vc(ry, 0.036, 9.5),
                 "w": 0.20, "align": "center", "style": "cardtitle", "size": 9.5,
                 "color": T["deep"]},
                {"type": "text", "text": val, "x": 0.378, "y": vc(ry, 0.036, 9.5),
                 "w": 0.45, "style": "body", "size": 9.5, "color": T["body"]},
                {"type": "hairline", "x": 0.16, "y": ry + 0.036, "w": 0.68,
                 "color": T["hair"]},
            ]
            ry += 0.036
        it += [
            {"type": "card", "x": 0.16, "y": ry + 0.001, "w": 0.68, "h": 0.0045,
             "fill": T["deep"], "radius": 0.0},
            {"type": "text", "text": "2026.  06.", "x": L, "y": 0.880, "w": W,
             "align": "center", "style": "cardtitle", "size": 11,
             "color": T["deep"]},
            {"type": "text", "text": ORG, "x": L, "y": 0.906, "w": W,
             "align": "center", "style": "headline", "size": 15,
             "color": T["deep"]},
        ]
        return it

    # s5-teal — 페트롤 상단 블록 2분할
    it += [
        {"type": "card", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.56,
         "fill": T["deep"], "radius": 0.0},
        {"type": "card", "x": 0.0, "y": 0.526, "w": 0.42, "h": 0.034,
         "fill": T["accent"], "radius": 0.0},
        {"type": "image", "path": f"assets/brand/{T['emblem_white']}", "x": L,
         "y": 0.078, "w": 0.082, "h": 0.082 * SQ},
        {"type": "text", "text": "경북대학교", "x": L + 0.098, "y": 0.090, "w": 0.4,
         "style": "cardtitle", "size": 12.5, "color": "FFFFFF"},
        {"type": "text", "text": ORG_SHORT, "x": L + 0.099, "y": 0.111, "w": 0.5,
         "style": "caption", "size": 8, "color": T["dark_sub"]},
        {"type": "pill", "x": L, "y": 0.238, "h": 0.030, "w": 0.175,
         "text": "RESULT REPORT", "size": 9, "fill": T["accent"],
         "text_color": "FFFFFF"},
        {"type": "text", "text": f"「{EVENT}」", "x": L, "y": 0.288, "w": 0.8,
         "style": "cardtitle", "size": 13.5, "color": T["dark_sub"]},
        {"type": "headline", "lines": ["결과보고서"], "x": L - 0.006, "y": 0.322,
         "w": 0.8, "size": 44, "color": "FFFFFF"},
        {"type": "text", "text": "함께 배우고 함께 성장한 6주간의 기록",
         "x": L, "y": 0.432, "w": 0.7, "style": "body", "size": 11,
         "color": T["dark_sub"]},
    ]
    ry = 0.640
    rows = [("주최", "대구광역시"), ("주관", ORG),
            ("수행", "모드어스 스튜디오"), ("기간", "2026. 05. 12. ~ 06. 20.")]
    for lab, val in rows:
        it += [
            {"type": "pill", "x": L, "y": ry, "h": 0.030, "w": 0.050,
             "text": lab, "size": 8.5, "fill": T["tint2"],
             "text_color": T["deep"]},
            {"type": "text", "text": val, "x": L + 0.068, "y": vc(ry, 0.030, 10),
             "w": 0.62, "style": "body", "size": 10, "color": T["body"]},
        ]
        ry += 0.044
    it += [
        {"type": "hairline", "x": L, "y": 0.842, "w": W, "color": T["hair"]},
        {"type": "text", "text": "2026. 06.", "x": L, "y": 0.862, "w": 0.4,
         "style": "cardtitle", "size": 10.5, "color": T["deep"]},
        {"type": "text", "text": ORG, "x": 0.4, "y": 0.864, "w": W - 0.325,
         "align": "right", "style": "body", "size": 9.5, "color": T["gray"]},
    ]
    return it


def page_toc(T):
    """목차."""
    s = T["slug"]
    it = running_head(T, "", "목  차", "2")
    y = 0.088
    if s == "s5-crimson":
        it += [
            {"type": "text", "text": "CONTENTS", "x": L, "y": y, "w": 0.5,
             "style": "caption", "size": 9, "color": T["accent"]},
            {"type": "headline", "lines": ["목  차"], "x": L - 0.005, "y": y + 0.022,
             "w": 0.5, "size": 28, "color": T["ink"]},
            {"type": "hairline", "x": L, "y": y + 0.086, "w": W, "color": T["accent"],
             "thick": 2.2},
        ]
    elif s == "s5-navygold":
        it += [
            {"type": "text", "text": "C O N T E N T S", "x": L, "y": y, "w": 0.5,
             "style": "caption", "size": 9, "color": T["accent"]},
            {"type": "headline", "lines": ["목  차"], "x": L - 0.005, "y": y + 0.024,
             "w": 0.5, "size": 27, "color": T["ink"]},
            {"type": "hairline", "x": L, "y": y + 0.088, "w": 0.052,
             "color": T["accent"], "thick": 2.6},
            {"type": "hairline", "x": L + 0.058, "y": y + 0.0887, "w": W - 0.058,
             "color": T["hair"]},
        ]
    elif s == "s5-govblue":
        it += [
            {"type": "headline", "lines": ["목  차"], "x": L, "y": y + 0.012,
             "w": W, "align": "center", "size": 26, "color": T["deep"]},
            {"type": "hairline", "x": L, "y": y + 0.076, "w": W, "color": T["deep"],
             "thick": 1.6},
            {"type": "hairline", "x": L, "y": y + 0.0788, "w": W,
             "color": T["accent2"]},
        ]
    else:
        it += [
            {"type": "pill", "x": L, "y": y, "h": 0.028, "w": 0.125,
             "text": "CONTENTS", "size": 9, "fill": T["accent"],
             "text_color": "FFFFFF"},
            {"type": "headline", "lines": ["목  차"], "x": L - 0.005, "y": y + 0.040,
             "w": 0.5, "size": 27, "color": T["deep"]},
            {"type": "hairline", "x": L, "y": y + 0.104, "w": W, "color": T["hair"]},
        ]
    ry = y + 0.128
    subs = [
        ["1. 과업 개요 및 핵심 성과", "2. 추진 일정 및 인력 구성"],
        ["1. 모집 · 홍보 실적", "2. 사전 준비 사항", "3. 현장 운영 내역"],
        ["1. 참여 현황 및 목표 달성률", "2. 만족도 조사 결과", "3. 증빙 자료"],
        ["1. 예산 집행 내역", "2. 정산 결과 및 제출 서류"],
    ]
    pages = [["3", "4"], ["5", "5", "6"], ["7", "7", "8"], ["9", "9"]]
    for ci, (num, roman, title, cap, _lead) in enumerate(CHAPTERS):
        block_h = 0.028 + len(subs[ci]) * 0.030 + 0.030
        if s == "s5-crimson":
            it += [
                {"type": "text", "text": num, "x": L, "y": ry - 0.008, "w": 0.10,
                 "style": "num_xl", "size": 26, "color": T["accent"]},
                {"type": "text", "text": title, "x": L + 0.085, "y": ry,
                 "w": 0.5, "style": "cardtitle", "size": 14, "color": T["ink"]},
                {"type": "hairline", "x": L + 0.085, "y": ry + 0.030, "w": W - 0.085,
                 "color": T["hair"]},
            ]
        elif s == "s5-navygold":
            it += [
                {"type": "text", "text": f"CHAPTER {num}", "x": L, "y": ry - 0.014,
                 "w": 0.3, "style": "caption", "size": 7.5, "color": T["accent"]},
                {"type": "text", "text": title, "x": L, "y": ry + 0.002, "w": 0.5,
                 "style": "cardtitle", "size": 14, "color": T["ink"]},
                {"type": "hairline", "x": L, "y": ry + 0.034, "w": W,
                 "color": T["hair"]},
            ]
        elif s == "s5-govblue":
            it += [
                {"type": "card", "x": L, "y": ry - 0.004, "w": 0.052, "h": 0.030,
                 "fill": T["deep"], "radius": 0.0},
                {"type": "text", "text": roman, "x": L, "y": vc(ry - 0.004, 0.030, 11),
                 "w": 0.052, "align": "center", "style": "cardtitle", "size": 11,
                 "color": "FFFFFF"},
                {"type": "text", "text": title, "x": L + 0.070, "y": ry, "w": 0.5,
                 "style": "cardtitle", "size": 13.5, "color": T["deep"]},
                {"type": "hairline", "x": L, "y": ry + 0.034, "w": W,
                 "color": T["hair"]},
            ]
        else:
            it += [
                {"type": "chip", "x": L, "y": ry - 0.006, "d": 0.038, "text": num,
                 "fill": T["deep"], "text_color": "FFFFFF"},
                {"type": "text", "text": title, "x": L + 0.056, "y": ry, "w": 0.5,
                 "style": "cardtitle", "size": 14, "color": T["deep"]},
                {"type": "hairline", "x": L + 0.056, "y": ry + 0.032, "w": W - 0.056,
                 "color": T["hair"]},
            ]
        sy = ry + 0.044
        indent = L + 0.085 if s in ("s5-crimson",) else (
            L + 0.070 if s == "s5-govblue" else L + 0.056 if s == "s5-teal" else L + 0.014)
        for si, sub in enumerate(subs[ci]):
            it += [
                {"type": "text", "text": sub, "x": indent, "y": sy, "w": 0.55,
                 "style": "body", "size": 9.8, "color": T["body"]},
                {"type": "text", "text": pages[ci][si], "x": 0.80, "y": sy,
                 "w": R - 0.80, "align": "right", "style": "body", "size": 9.8,
                 "color": T["gray"]},
            ]
            sy += 0.030
        ry = sy + 0.036
    # 하단 첨부 안내
    it += [
        {"type": "band", "x": L, "y": 0.862, "w": W, "h": 0.040, "fill": T["tint"],
         "radius": 0.0 if s == "s5-govblue" else 0.5, "label": "별첨",
         "label_color": T["accent"],
         "text": "① 참여자 서명부  ② 만족도 설문 원본  ③ 예산 집행 증빙  ④ 현장 사진 자료",
         "text_color": T["body"], "size": 9.3, "align": "left", "pad": 0.020},
    ]
    return it


def page_ch1_overview(T):
    it = running_head(T, "01", "과업추진 개요", "3")
    head, y = chapter_head(T, 0)
    it += head
    sec, y = section(T, y, "1. 과업 개요", "※ 계약서 및 운영계획서 기준")
    it += sec
    tb, y = table(T, L, y, W, [0.20, 0.80], ["구    분", "내    용"],
                  OVERVIEW, row_h=0.0305, aligns=["center", "left"], tint_col=0)
    it += tb
    y += 0.030
    sec, y = section(T, y, "2. 핵심 성과 요약")
    it += sec
    kp, y = kpi_row(T, y)
    it += kp
    y += 0.028
    sec, y = section(T, y, "3. 추진 배경 및 목적")
    it += sec
    bullets = [
        ("추진 배경", "지역 재직자·시민의 실무 역량 격차가 확대되고 있으나, 접근 가능한 "
                   "실습 중심 교육이 부족하다는 수요 조사 결과에 따라 과업을 추진하였다."),
        ("과업 목적", "이론 전달에 그치지 않고 회차별 개인 과제와 첨삭을 결합해, "
                   "참여자가 종료 시점에 자신의 결과물을 보유하도록 설계하였다."),
        ("기대 효과", "지역 인재의 실무 적용력 향상과 후속 심화 과정 수요 확보, "
                   "사업단·지자체 간 협력 모델의 지속 운영 기반을 마련한다."),
    ]
    for lab, txt in bullets:
        it += [
            {"type": "card", "x": L, "y": y + 0.004, "w": 0.0035, "h": 0.040,
             "fill": T["accent"], "radius": 0.0},
            {"type": "text", "text": lab, "x": L + 0.016, "y": y, "w": 0.13,
             "style": "cardtitle", "size": 9.8, "color": T["ink"]},
            {"type": "text", "text": txt, "x": L + 0.135, "y": y + 0.001,
             "w": W - 0.135, "style": "body", "size": 9.3, "spacing": 1.55,
             "color": T["body"]},
        ]
        y += 0.049
    return it


def page_ch1_schedule(T):
    it = running_head(T, "01", "과업추진 개요", "4")
    y = 0.088
    sec, y = section(T, y, "4. 추진 일정", "단위: 주차 (■ 수행 구간)")
    it += sec
    tb, y = table(T, L, y, W, [0.18, 0.20, 0.22, 0.40],
                  ["단    계", "기    간", "주차별 일정", "주요 내용"],
                  SCHEDULE, row_h=0.029,
                  aligns=["center", "center", "center", "left"], tint_col=0)
    it += tb
    y += 0.026
    sec, y = section(T, y, "5. 인력 구성 및 역할")
    it += sec
    tb, y = table(T, L, y, W, [0.20, 0.24, 0.42, 0.14],
                  ["역    할", "소    속", "담당 업무", "인원"],
                  STAFF, row_h=0.029,
                  aligns=["center", "center", "left", "center"], tint_col=0)
    it += tb
    y += 0.012
    it.append({"type": "text",
               "text": "※ 강사진 4인은 분야별 전문가로 위촉하였으며, 위촉 공문과 강의계획서는 별첨 자료로 제출한다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8.3,
               "color": T["gray"]})
    y += 0.026
    sec, y = section(T, y, "6. 운영 체계")
    it += sec
    top_w, top_h = 0.30, 0.042
    tx = L + (W - top_w) / 2
    it += [
        {"type": "card", "x": tx, "y": y, "w": top_w, "h": top_h, "fill": T["deep"],
         "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06},
        {"type": "text", "text": "총괄 책임  (사업단 단장)", "x": tx,
         "y": vc(y, top_h, 9.8), "w": top_w, "align": "center", "style": "cardtitle",
         "size": 9.8, "color": "FFFFFF"},
        # 세로 커넥터는 hairline(가로 전용)이 아니라 얇은 card로 그린다
        {"type": "card", "x": 0.5 - 0.0011, "y": y + top_h, "w": 0.0022,
         "h": 0.020, "fill": T["arrow_gray"], "radius": 0.0},
    ]
    ly = y + top_h + 0.020
    it.append({"type": "hairline", "x": L + 0.10, "y": ly, "w": W - 0.20,
               "color": T["arrow_gray"], "thick": 1.2})
    cy = ly + 0.014
    cw, gap = 0.24, 0.05
    cells = [("운영 실무 (2명)", "일정 · 예산 · 현장 총괄"),
             ("강사진 (4명)", "회차별 강의 · 실습 지도"),
             ("현장 지원 (3명)", "출결 · 설문 · 기자재")]
    sx = L + (W - (cw * 3 + gap * 2)) / 2
    for i, (t1, t2) in enumerate(cells):
        cx = sx + i * (cw + gap)
        it += [
            {"type": "card", "x": cx + cw / 2 - 0.0011, "y": ly, "w": 0.0022,
             "h": cy - ly, "fill": T["arrow_gray"], "radius": 0.0},
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.046,
             "fill": T["tint"], "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06,
             "outline": T["hair"]},
            {"type": "text", "text": t1, "x": cx, "y": cy + 0.008, "w": cw,
             "align": "center", "style": "cardtitle", "size": 9.5,
             "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx, "y": cy + 0.027, "w": cw,
             "align": "center", "style": "caption", "size": 8,
             "color": T["gray"]},
        ]
    y = cy + 0.046 + 0.028
    sec, y = section(T, y, "7. 위험 요인 및 대응 계획")
    it += sec
    tb, y = table(T, L, y, W, [0.26, 0.32, 0.42],
                  ["위험 요인", "예상 영향", "대응 계획"],
                  [("중도 이탈 발생", "수료율 목표 미달", "예비 인원 8명 충원 · 보충 자료 발송"),
                   ("실습 기자재 장애", "회차 진행 지연", "예비 노트북 3대 · 사전 점검 운영"),
                   ("강사 일정 변경", "커리큘럼 순서 조정", "대체 강사 사전 협의 · 순서 교체")],
                  row_h=0.029, aligns=["center", "center", "left"], tint_col=0)
    it += tb
    return it


def page_ch2_promo(T):
    it = running_head(T, "02", "과업 수행 내역", "5")
    head, y = chapter_head(T, 1)
    it += head
    sec, y = section(T, y, "1. 모집 · 홍보 실적", "집계 기준: 2026. 05. 09.")
    it += sec
    tb, y = table(T, L, y, W, [0.34, 0.24, 0.18, 0.24],
                  ["홍보 채널", "게시 기간", "게시 건수", "도달 · 노출"],
                  PROMO, row_h=0.031,
                  aligns=["left", "center", "center", "center"], tint_col=0)
    it += tb
    y += 0.020
    it += [
        {"type": "band", "x": L, "y": y, "w": W, "h": 0.040, "fill": T["tint"],
         "radius": 0.0 if T["slug"] == "s5-govblue" else 0.5, "label": "모집 결과",
         "label_color": T["accent"],
         "text": "정원 40명 대비 신청 68명 (경쟁률 1.7:1) — 선발 40명, 예비 8명",
         "text_color": T["body"], "size": 9.5, "align": "left", "pad": 0.020},
    ]
    y += 0.062
    sec, y = section(T, y, "2. 사전 준비 사항")
    it += sec
    ch, y = number_chain(T, y, PREP)
    it += ch
    y += 0.028
    sec, y = section(T, y, "3. 신청 · 선발 절차")
    it += sec
    steps = [("접수", "온라인 신청서 접수 (05.01~05.09)"),
             ("검토", "지원 자격 및 참여 동기 검토"),
             ("선발", "선발 기준 적용, 40명 확정"),
             ("안내", "개별 문자·메일 안내 및 확정 회신")]
    for i, (lab, txt) in enumerate(steps):
        ry = y + i * 0.032
        it += [
            {"type": "text", "text": f"{i + 1})", "x": L + 0.004, "y": ry, "w": 0.03,
             "style": "cardtitle", "size": 9.3, "color": T["accent"]},
            {"type": "text", "text": lab, "x": L + 0.036, "y": ry, "w": 0.09,
             "style": "cardtitle", "size": 9.3, "color": T["ink"]},
            {"type": "text", "text": txt, "x": L + 0.135, "y": ry, "w": W - 0.135,
             "style": "body", "size": 9.3, "color": T["body"]},
            {"type": "hairline", "x": L, "y": ry + 0.026, "w": W,
             "color": T["hair"]},
        ]
    return it


def page_ch2_ops(T):
    it = running_head(T, "02", "과업 수행 내역", "6")
    y = 0.088
    sec, y = section(T, y, "4. 회차별 운영 시간표", "1일 2회차 · 회차당 3시간")
    it += sec
    hdr_h, row_h = 0.031, 0.0345
    it.append({"type": "card", "x": L, "y": y, "w": W, "h": hdr_h,
               "fill": T["hdr_grad"][0] if T["hdr_grad"] else T["hdr_fill"],
               "radius": 0.0,
               **({"grad": T["hdr_grad"]} if T["hdr_grad"] else {})})
    it += [
        {"type": "text", "text": "시    간", "x": L, "y": vc(y, hdr_h, 9.3),
         "w": 0.18, "align": "center", "style": "cardtitle", "size": 9.3,
         "color": T["hdr_fg"]},
        {"type": "text", "text": "운영 내용", "x": L + 0.19, "y": vc(y, hdr_h, 9.3),
         "w": W - 0.19, "style": "cardtitle", "size": 9.3, "color": T["hdr_fg"]},
    ]
    ry = y + hdr_h
    for tm, body in TIMETABLE:
        core = "휴식" not in body and "종료" not in body
        it += [
            {"type": "card", "x": L, "y": ry, "w": 0.18, "h": row_h,
             "fill": T["tint"] if core else T["bg"], "radius": 0.0},
            {"type": "text", "text": tm, "x": L, "y": vc(ry, row_h, 9.8), "w": 0.18,
             "align": "center", "style": "cardtitle", "size": 9.8,
             "color": T["accent"] if core else T["gray"]},
            {"type": "text", "text": body, "x": L + 0.202, "y": vc(ry, row_h, 9.3),
             "w": W - 0.21, "style": "body", "size": 9.3,
             "color": T["body"] if core else T["gray"]},
            {"type": "hairline", "x": L, "y": ry + row_h - 0.0006, "w": W,
             "color": T["hair"]},
        ]
        ry += row_h
    y = ry + 0.030
    sec, y = section(T, y, "5. 운영 지원 및 안전 관리")
    it += sec
    cards = [
        ("출결 · 수료 관리", "회차별 QR 출결과 서명부를 병행 기록하고, 12시간 이상 "
                        "이수자를 수료 대상으로 집계하였다. 결석자에게는 보충 자료를 "
                        "개별 발송하였다."),
        ("현장 안전 · 방역", "비상 연락망과 대피 동선을 사전 공지하고, 회차 시작 전 "
                        "기자재·전기 안전 점검을 실시하였다. 안전사고는 발생하지 "
                        "않았다."),
        ("만족도 · 의견 수렴", "회차 종료 시 설문을 실시하고 3회차 단위로 중간 점검 "
                          "회의를 열어 실습 시간 배분 등 운영 사항을 조정하였다."),
        ("기록 · 증빙 관리", "회차별 사진과 산출물을 표준 양식으로 정리하고, 개인정보 "
                        "동의서를 받아 증빙 자료로 보관하였다."),
    ]
    gap = 0.020
    cw = (W - gap) / 2
    ch_h = 0.098
    for i, (t1, t2) in enumerate(cards):
        r, c = divmod(i, 2)
        cx = L + c * (cw + gap)
        cy = y + r * (ch_h + gap)
        it += [
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": ch_h, "fill": T["tint"],
             "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06},
            {"type": "card", "x": cx, "y": cy, "w": 0.0035, "h": ch_h,
             "fill": T["accent"], "radius": 0.0},
            {"type": "text", "text": t1, "x": cx + 0.020, "y": cy + 0.013,
             "w": cw - 0.036, "style": "cardtitle", "size": 10, "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx + 0.020, "y": cy + 0.038,
             "w": cw - 0.038, "style": "body", "size": 8.8, "spacing": 1.5,
             "color": T["body"]},
        ]
    y = y + ch_h * 2 + gap + 0.036
    sec, y = section(T, y, "6. 회차별 운영 실적", "정원 20명 / 회차당 3시간")
    it += sec
    tb, y = table(T, L, y, W, [0.22, 0.24, 0.18, 0.18, 0.18],
                  ["구    분", "운영 기간", "회차", "연인원", "평균 출석률"],
                  [("1주차 ~ 2주차", "05.12 ~ 05.23", "4회차", "152명", "95.0%"),
                   ("3주차 ~ 4주차", "05.26 ~ 06.06", "4회차", "148명", "92.5%"),
                   ("5주차 ~ 6주차", "06.09 ~ 06.20", "4회차", "141명", "88.1%")],
                  row_h=0.031,
                  aligns=["center", "center", "center", "center", "center"],
                  tint_col=0)
    it += tb
    y += 0.016
    it.append({"type": "band", "x": L, "y": y, "w": W, "h": 0.040,
               "fill": T["tint"],
               "radius": 0.0 if T["slug"] == "s5-govblue" else 0.5,
               "label": "운영 총계", "label_color": T["accent"],
               "text": "총 12회차 · 연인원 441명 · 평균 출석률 91.9% (목표 85% 대비 +6.9%p)",
               "text_color": T["body"], "size": 9.5, "align": "left", "pad": 0.020})
    return it


def page_ch3_result(T):
    it = running_head(T, "03", "과업 수행 결과", "7")
    head, y = chapter_head(T, 2)
    it += head
    sec, y = section(T, y, "1. 목표 대비 달성률")
    it += sec
    tb, y = table(T, L, y, W, [0.30, 0.22, 0.22, 0.26],
                  ["구    분", "목    표", "실    적", "달 성 률"],
                  RESULT_TBL, row_h=0.031,
                  aligns=["left", "center", "center", "center"], tint_col=0)
    it += tb
    y += 0.016
    it.append({"type": "text",
               "text": "※ 달성률은 실적 ÷ 목표 × 100 기준이며, 만족도는 5점 척도 환산값이다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8.3,
               "color": T["gray"]})
    y += 0.042
    sec, y = section(T, y, "2. 만족도 조사 결과", "응답 114부 / 5점 척도")
    it += sec
    bb, by = bars_block(T, L, y, W * 0.60, SATIS)
    it += bb
    # 우측 요약 카드
    cx = L + W * 0.64
    cw = W - W * 0.64
    it += [
        {"type": "card", "x": cx, "y": y - 0.004, "w": cw, "h": 0.152,
         "fill": T["deep"], "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06},
        {"type": "text", "text": "종합 만족도", "x": cx + 0.018, "y": y + 0.014,
         "w": cw - 0.036, "align": "center", "style": "caption", "size": 8.5,
         "color": T["dark_sub"]},
        {"type": "text", "runs": [[{"t": "4.6", "color": "FFFFFF",
                                    "font": "display_b", "size": 30},
                                   {"t": " / 5.0", "color": T["dark_sub"],
                                    "font": "body_sb", "size": 10}]],
         "x": cx + 0.018, "y": y + 0.037, "w": cw - 0.036, "align": "center",
         "style": "body"},
        {"type": "hairline", "x": cx + 0.028, "y": y + 0.090, "w": cw - 0.056,
         "color": T["accent2"]},
        {"type": "text", "text": "5점 만점 기준 상위 92%\n재참여 의향 4.5점",
         "x": cx + 0.014, "y": y + 0.101, "w": cw - 0.028, "align": "center",
         "style": "caption", "size": 8.3, "spacing": 1.5, "color": T["dark_sub"]},
    ]
    y = max(by, y + 0.152) + 0.030
    sec, y = section(T, y, "3. 참여자 의견")
    it += sec
    gap = 0.020
    cw2 = (W - gap) / 2
    for i, (quote, who) in enumerate(VOICES):
        cx = L + i * (cw2 + gap)
        it += [
            {"type": "card", "x": cx, "y": y, "w": cw2, "h": 0.106,
             "fill": T["tint"], "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06},
            {"type": "text", "text": "“", "x": cx + 0.016, "y": y + 0.004, "w": 0.06,
             "style": "num_xl", "size": 22, "color": T["accent2"]},
            {"type": "text", "text": quote, "x": cx + 0.040, "y": y + 0.022,
             "w": cw2 - 0.058, "style": "body", "size": 8.8, "spacing": 1.5,
             "color": T["body"]},
            {"type": "text", "text": f"— {who}", "x": cx + 0.018, "y": y + 0.080,
             "w": cw2 - 0.036, "align": "right", "style": "caption", "size": 8,
             "color": T["gray"]},
        ]
    return it


def page_ch3_photos(T):
    it = running_head(T, "03", "과업 수행 결과", "8")
    y = 0.088
    sec, y = section(T, y, "4. 증빙 사진", "촬영 동의 취득 / 원본 별첨")
    it += sec
    pg, y = photo_grid(T, y)
    it += pg
    y += 0.026
    sec, y = section(T, y, "5. 참여자 서명부 및 산출물")
    it += sec
    tb, y = table(T, L, y, W, [0.34, 0.22, 0.22, 0.22],
                  ["산 출 물", "형    태", "수    량", "보관 · 제출"],
                  [("참여자 서명부", "원본 스캔", "12회차분", "별첨 ①"),
                   ("만족도 설문지", "원본 · 집계표", "114부", "별첨 ②"),
                   ("회차별 교재 · 워크북", "PDF · 인쇄본", "12종", "사업단 보관"),
                   ("현장 사진 자료", "JPG", "246매", "별첨 ④")],
                  row_h=0.031, aligns=["left", "center", "center", "center"],
                  tint_col=0)
    it += tb
    return it


def page_ch4_budget(T):
    it = running_head(T, "04", "산출 내역", "9")
    head, y = chapter_head(T, 3)
    it += head
    sec, y = section(T, y, "1. 예산 집행 내역", "단위: 원 (부가세 포함)")
    it += sec
    tb, y = table(T, L, y, W, [0.24, 0.22, 0.19, 0.19, 0.16],
                  ["항    목", "산출 근거", "편성액", "집행액", "잔    액"],
                  BUDGET,
                  row_h=0.029, aligns=["left", "center", "right", "right", "right"],
                  tint_col=0, sum_row=BUDGET_SUM)
    it += tb
    y += 0.014
    it.append({"type": "text",
               "text": "※ 집행 잔액 100,000원은 정산 시 반납 예정이며, 세부 증빙(계약서·세금계산서·이체확인증)은 별첨 ③으로 제출한다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8.3,
               "spacing": 1.5, "color": T["gray"]})
    y += 0.030
    sec, y = section(T, y, "2. 정산 결과 요약")
    it += sec
    gap = 0.018
    cw = (W - gap * 2) / 3
    summ = [("편성액", "27,000,000", "원"), ("집행액", "26,900,000", "원"),
            ("집행률", "99.6", "%")]
    for i, (lab, val, unit) in enumerate(summ):
        cx = L + i * (cw + gap)
        last = i == 2
        it += [
            {"type": "card", "x": cx, "y": y, "w": cw, "h": 0.068,
             "fill": T["deep"] if last else T["tint"],
             "radius": 0.0 if T["slug"] == "s5-govblue" else 0.06},
            {"type": "text", "text": lab, "x": cx + 0.018, "y": y + 0.011,
             "w": cw - 0.036, "style": "caption", "size": 8.5,
             "color": T["dark_sub"] if last else T["gray"]},
            {"type": "text",
             "runs": [[{"t": val, "color": "FFFFFF" if last else T["ink"],
                        "font": "display_b", "size": 17},
                       {"t": " " + unit,
                        "color": T["dark_sub"] if last else T["gray"],
                        "font": "body_sb", "size": 9.5}]],
             "x": cx + 0.017, "y": y + 0.030, "w": cw - 0.03, "style": "body"},
        ]
    y += 0.068 + 0.022
    sec, y = section(T, y, "3. 제출 서류")
    it += sec
    it.append({"type": "band", "x": L, "y": y, "w": W, "h": 0.040,
               "fill": T["tint"],
               "radius": 0.0 if T["slug"] == "s5-govblue" else 0.5,
               "label": "별첨", "label_color": T["accent"],
               "text": "① 참여자 서명부  ② 만족도 설문 원본·집계표  ③ 예산 집행 증빙 일체  ④ 현장 사진 자료",
               "text_color": T["body"], "size": 9.3, "align": "left", "pad": 0.020})
    y += 0.050
    cb, y = closing_band(T, y)
    it += cb
    return it


PAGES = [page_cover, page_toc, page_ch1_overview, page_ch1_schedule,
         page_ch2_promo, page_ch2_ops, page_ch3_result, page_ch3_photos,
         page_ch4_budget]


def build(T):
    proj = PROJECTS / T["slug"]
    (proj / "pages").mkdir(parents=True, exist_ok=True)
    if T["slug"] == "s5-crimson" and COVER_SRC.exists():
        shutil.copy(COVER_SRC, proj / "assets" / "cover_bg.png")
    for i, fn in enumerate(PAGES, start=1):
        items = fn(T)
        # text 아이템의 \n은 마지막 줄만 행간이 벌어진다 — lines 배열로 변환
        for item in items:
            if item.get("type") == "text" and "\n" in item.get("text", ""):
                item["lines"] = item.pop("text").split("\n")
        spec = {"page": i, "theme": T["theme"], "variant": "paper",
                "page_size": "a4p", "items": items}
        d = proj / "pages" / f"p{i:02d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "layout_spec.json").write_text(
            json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {T['slug']:14s} {len(PAGES)}장 — {T['label']}")


if __name__ == "__main__":
    print("결보 A4 세로 템플릿 생성")
    for T in (CRIMSON, NAVYGOLD, GOVBLUE, TEAL):
        build(T)
