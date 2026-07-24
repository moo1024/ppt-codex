#!/usr/bin/env python3
"""결과보고서(결보) A4 세로 — 산학협력 브로슈어 문법 판(v2).

레퍼런스: '디자인 레퍼런스/기업제안서'의 LINC 3.0 브로슈어들(한양여대·울산대).
v1(문서형 표 나열)이 반려되어, 아래 문법을 이식했다.
  ① 초대형 챕터 숫자 + CHAPTER → + 우측 2줄 컬러 타이틀 + 이중 룰
  ② 좌측 라벨 레일 + 계층별 색이 다른 셀 그리드 (비전→핵심가치→전략→과제)
  ③ 목표 ▶▶▶ 실적 비교 카드
  ④ 원형 노드 그룹 / STEP 체인 / 다층 조직도
  ⑤ 컬러 원형 불릿(◉) 섹션 헤더 + 하위 · 캡션
  ⑥ 페이지당 도식 2개 이상, 하단까지 채운다

좌표 0~1 (A4 세로 540×780pt). 정사각 보정 SQ.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"

SQ = 540 / 780
PT = 1 / 780
L, R = 0.072, 0.928
W = R - L
RAIL_W = 0.108          # 좌측 라벨 레일 폭
CX = L + RAIL_W + 0.016  # 레일 우측 콘텐츠 시작
CW = R - CX

COVER_SRC = Path("/mnt/c/Users/hansb/Desktop/결보 템플릿/결보 표지 디자인/"
                 "ChatGPT Image 2026년 4월 28일 오후 01_36_47.png")


def vc(y, h, size, spacing=1.45):
    return y + (h - size * spacing * PT) / 2


def pill_w(text, size, pad_pt=24):
    em = sum(1.0 if ord(ch) > 0x1100 else 0.55 for ch in text)
    return (em * size + pad_pt) / 540


# ────────────────────────────────────────────────────────────── 팔레트
CRIMSON = dict(
    slug="s5-crimson", theme="gyeolbo", label="KNU 크림슨 브로슈어",
    main="D80C18", main_d="8C0A12", main_l="FC3E31",
    sub="25446A", sub_l="41628C",            # 계층 2색 (네이비)
    tint="FDF0F0", tint2="F9DCDD", neutral="F1F2F4", neutral2="E4E6EA",
    ink="1A1A1A", body="3A3A3A", gray="76767A", hair="E1E3E7",
    dark_sub="F5B9BC", bg="FFFFFF", rail="EDEFF3", rail_ink="25446A",
    emblem="emblem_crimson.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png", cover_img=True,
)
NAVYGOLD = dict(
    slug="s5-navygold", theme="goldnavy", label="네이비·골드 브로슈어",
    main="C8912F", main_d="9A6E22", main_l="E0B25C",
    sub="1B2A4A", sub_l="3D5378",
    tint="F7F1E3", tint2="EFE9DA", neutral="F3F1EC", neutral2="E2DCCB",
    ink="1B2A4A", body="3A4358", gray="7A7E8C", hair="E2DCCB",
    dark_sub="B9A67C", bg="FDFBF6", rail="EDE8DC", rail_ink="1B2A4A",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png", cover_img=False,
)
GOVBLUE = dict(
    slug="s5-govblue", theme="govblue", label="공공 블루 브로슈어",
    main="2E75B6", main_d="1F4E79", main_l="5B9BD5",
    sub="1C3D5E", sub_l="3A6089",
    tint="EBF3FA", tint2="D7E7F5", neutral="F1F4F8", neutral2="DDE4EE",
    ink="1F4E79", body="333333", gray="6E7787", hair="DDE4EE",
    dark_sub="9FC0E0", bg="FFFFFF", rail="E7EEF7", rail_ink="1F4E79",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png", cover_img=False,
)
TEAL = dict(
    slug="s5-teal", theme="tealcoral", label="페트롤·코랄 브로슈어",
    main="10577D", main_d="0B3C58", main_l="3E7FA3",
    sub="EF7B68", sub_l="F5A492",
    tint="E9F1F5", tint2="D9E5EB", neutral="F3F1EA", neutral2="E4DFD1",
    ink="143B4E", body="2E4653", gray="7C8890", hair="E1E0D8",
    dark_sub="9FC3D4", bg="FAF7EF", rail="E4EDF2", rail_ink="10577D",
    emblem="emblem_accent.png", emblem_white="emblem_white.png",
    emblem_wm="emblem_watermark.png", cover_img=False,
)

# ────────────────────────────────────────────────────────────── 내용
EVENT = "2026 지역 상생 아카데미"
ORG = "경북대학교 지식재산전문인력양성사업단"
ORG_SHORT = "지식재산전문인력양성사업단"

CH = [
    ("01", "과업추진", "개요",
     "본 장에서는 과업의 목적과 추진 체계, 운영 개요와 핵심 성과 지표를 요약한다. "
     "세부 일정과 인력 구성, 운영 조직은 이어지는 절에 정리하였다."),
    ("02", "과업", "수행 내역",
     "모집·홍보부터 사전 준비, 현장 운영까지 과업 수행의 전 과정을 시간 순으로 기술한다. "
     "각 단계의 산출물과 점검 결과를 함께 제시한다."),
    ("03", "과업", "수행 결과",
     "참여 현황과 목표 대비 달성률, 만족도 조사 결과와 참여자 의견을 정리하고 "
     "증빙 자료를 첨부한다."),
    ("04", "산출", "내역",
     "과업 수행에 소요된 예산의 집행 내역과 정산 결과를 항목별로 제시한다. "
     "증빙 서류는 별첨으로 제출한다."),
]

TOC = [("01", "과업추진 개요", "3"), ("02", "추진 체계 및 인력", "4"),
       ("03", "모집 · 홍보 및 사전 준비", "5"), ("04", "현장 운영 내역", "6"),
       ("05", "목표 대비 수행 결과", "7"), ("06", "증빙 자료 및 산출물", "8"),
       ("07", "예산 집행 및 정산", "9")]

OVERVIEW = [("행 사 명", "「2026 지역 상생 아카데미」 역량강화 프로그램"),
            ("운영 기간", "2026. 05. 12.(화) ~ 06. 20.(금) / 총 6주 12회차"),
            ("운영 장소", "경북대학교 글로벌플라자 2층 세미나실"),
            ("참여 대상", "지역 시민 및 재직자 40명 (1일 2회차, 회차당 20명)"),
            ("주최·주관", "대구광역시 · 경북대학교 지식재산전문인력양성사업단"),
            ("수행 기관", "모드어스 스튜디오 (계약 제2026-0512호)")]

NODES = [("Edu", "실무 역량", "현장에 바로 쓰는\n실습 중심 커리큘럼"),
         ("Link", "지역 연계", "지역 기업·기관과\n연계한 과제 수행"),
         ("Grow", "지속 성장", "수료 후 심화 과정\n연계 및 네트워크"),
         ("Share", "성과 확산", "산출물 공유와\n우수사례 확산")]

GOALS = [("참여 인원", "120명", "128명", "106.7%"),
         ("수료 인원", "100명", "114명", "114.0%"),
         ("운영 회차", "12회차", "12회차", "100.0%"),
         ("종합 만족도", "4.0점", "4.6점", "115.0%")]

STRATEGY = [
    ("과업 목표", 1, ["시민·재직자의 실무 역량을 실습으로 끌어올린다"]),
    ("핵심 가치", 2, ["실습 중심 Practice", "지역 연계 Local", "지속 성장 Growth",
                   "성과 확산 Sharing"]),
    ("추진 전략", 3, ["수준별 맞춤 커리큘럼", "회차별 개인 첨삭", "지역 과제 연계 실습",
                   "수료 후 네트워크"]),
    ("실행 과제", 4, ["사전 진단 후 반 편성\n워크북 12종 제작",
                   "회차별 과제 첨삭\n보충 자료 개별 발송",
                   "지역 기업 사례 과제\n현장 전문가 특강",
                   "수료생 커뮤니티 운영\n심화 과정 우선 안내"]),
]

SCHEDULE = [("기획 · 계약", "04.14 ~ 04.30", 0, 2, "운영계획 수립, 계약 체결"),
            ("모집 · 홍보", "05.01 ~ 05.09", 1, 2, "채널 게시, 신청 접수·선발"),
            ("사전 준비", "05.04 ~ 05.11", 1, 2, "교재 제작, 강사 계약, 장소 점검"),
            ("현장 운영", "05.12 ~ 06.20", 2, 3, "12회차 강의 운영, 출결 관리"),
            ("결과 정리", "06.21 ~ 06.30", 4, 2, "만족도 분석, 결과보고서 제출")]

STAFF = [("총괄 책임", "사업단 단장", "과업 총괄 및 대외 협의", "1명"),
         ("운영 실무", "사업단 전임연구원", "일정 · 예산 관리, 현장 총괄", "2명"),
         ("강사진", "외부 전문가 4인", "회차별 강의 및 실습 지도", "4명"),
         ("현장 지원", "학부 근로장학생", "출결 · 설문 · 기자재 지원", "3명")]

PROMO = [("기관 누리집", "05.01 ~ 05.09", "3건", "1,240회"),
         ("SNS (인스타그램)", "05.01 ~ 05.09", "6건", "3,870회"),
         ("지역 커뮤니티 카페", "05.02 ~ 05.08", "4건", "2,150회"),
         ("현수막 · 포스터", "05.01 ~ 05.12", "12개소", "—")]

STEPS = [("접수", "온라인 신청서 접수", "05.01 ~ 05.09"),
         ("검토", "자격 · 참여 동기 검토", "05.10"),
         ("선발", "선발 기준 적용 40명 확정", "05.11"),
         ("안내", "개별 문자 · 메일 회신", "05.11")]

PREP = [("교재 · 실습자료", "회차별 워크북 12종, 실습 데이터셋 4종 사전 검수"),
        ("강사 섭외 · 계약", "분야별 전문가 4인 위촉, 강의계획서 사전 검토"),
        ("장소 · 기자재", "좌석 20석, 노트북 20대, 네트워크 사전 테스트"),
        ("안전 · 매뉴얼", "비상 연락망, 출결 · 설문 절차 표준화 및 사전 교육")]

TIMETABLE = [("13:00", "등록 및 오리엔테이션", "출결 확인, 교재 배부", 0),
             ("13:20", "1교시 이론 강의", "주제별 핵심 개념과 사례 분석", 1),
             ("14:20", "휴식", "10분", 0),
             ("14:30", "2교시 실습", "개인별 과제 수행 및 강사 첨삭", 1),
             ("15:40", "질의응답 · 정리", "만족도 설문 작성", 0),
             ("16:00", "종료", "차시 안내", 0)]

OPS = [("출결 · 수료 관리", "QR 출결과 서명부를 병행 기록하고 12시간 이상 이수자를 "
                      "수료 대상으로 집계하였다."),
       ("현장 안전 · 방역", "비상 연락망과 대피 동선을 사전 공지하고 회차 시작 전 "
                      "기자재 안전 점검을 실시하였다."),
       ("만족도 · 의견 수렴", "회차 종료 시 설문을 실시하고 3회차 단위 중간 점검 회의로 "
                        "운영 사항을 조정하였다."),
       ("기록 · 증빙 관리", "회차별 사진과 산출물을 표준 양식으로 정리하고 개인정보 "
                      "동의서를 받아 보관하였다.")]

ROUNDS = [("1주차 ~ 2주차", "05.12 ~ 05.23", "4회차", "152명", "95.0%"),
          ("3주차 ~ 4주차", "05.26 ~ 06.06", "4회차", "148명", "92.5%"),
          ("5주차 ~ 6주차", "06.09 ~ 06.20", "4회차", "141명", "88.1%")]

SATIS = [("강의 내용의 유익성", 4.7), ("강사의 전달력", 4.8),
         ("실습 시간의 적정성", 4.4), ("운영 · 안내의 원활함", 4.6),
         ("재참여 의향", 4.5)]

VOICES = [("실습 위주로 진행되어 바로 업무에 적용해 볼 수 있었습니다. 회차마다 첨삭을 "
           "받은 점이 가장 도움이 되었습니다.", "3회차 참여자 A"),
          ("처음에는 어렵게 느껴졌지만 단계별로 따라가니 끝까지 완주할 수 있었습니다. "
           "심화 과정도 개설되면 다시 참여하고 싶습니다.", "8회차 참여자 B")]

PHOTOS = ["개강식 및 오리엔테이션", "회차별 이론 강의 운영",
          "조별 실습 및 강사 첨삭", "수료식 및 기념 촬영"]

OUTPUTS = [("참여자 서명부", "원본 스캔", "12회차분", "별첨 ①"),
           ("만족도 설문지", "원본 · 집계표", "114부", "별첨 ②"),
           ("회차별 교재 · 워크북", "PDF · 인쇄본", "12종", "사업단 보관"),
           ("현장 사진 자료", "JPG", "246매", "별첨 ④")]

PARTNERS = [("주최 · 대구광역시", "사업 총괄 및 예산 지원",
             "· 운영계획 승인\n· 중간 · 최종 점검"),
            ("주관 · 사업단", "프로그램 기획 및 운영 총괄",
             "· 커리큘럼 설계 · 강사 위촉\n· 예산 집행 및 정산"),
            ("수행 · 모드어스 스튜디오", "현장 운영 및 산출물 제작",
             "· 교재 제작 · 현장 지원\n· 결과보고서 작성")]

RISKS = [("중도 이탈 발생", "수료율 목표 미달", "예비 인원 8명 충원 · 보충 자료 발송"),
         ("실습 기자재 장애", "회차 진행 지연", "예비 노트북 3대 확보 · 사전 점검"),
         ("강사 일정 변경", "커리큘럼 순서 조정", "대체 강사 사전 협의 · 순서 교체")]

INSIGHT = [("실습 중심 설계의 효과", T_OK := None,
            "회차별 개인 첨삭을 결합한 결과 수료 인원이 목표 대비 114%를 기록하였다. "
            "이론 단독 회차보다 만족도가 0.3점 높게 나타났다."),
           ("보완이 필요한 지점", None,
            "실습 시간의 적정성이 4.4점으로 상대적으로 낮아, 차기 과정에서는 회차당 "
            "실습 시간을 20분 확대할 필요가 있다."),
           ("후속 과제", None,
            "수료생 대상 심화 과정 개설 수요가 확인되었으며, 지역 기업 연계 과제를 "
            "정규 커리큘럼에 포함하는 방안을 검토한다.")]

BUDGET = [("강사료", "4인 × 12회차", "14,400,000", "14,400,000", "—"),
          ("교재 · 실습자료", "40부 × 12종", "3,600,000", "3,540,000", "60,000"),
          ("장소 · 기자재 임차", "12회차", "2,400,000", "2,400,000", "—"),
          ("운영 인건비", "3인 × 6주", "5,400,000", "5,400,000", "—"),
          ("홍보 · 인쇄", "포스터 · 현수막", "1,200,000", "1,160,000", "40,000")]
BUDGET_SUM = ("합    계", "", "27,000,000", "26,900,000", "100,000")


# ────────────────────────────────────────────────────────────── 프리미티브
def page_frame(T, no, chapter, title):
    """상단 러닝헤드 + 하단 페이지 번호 (브로슈어식: 컬러 숫자 + 기관명)."""
    return [
        {"type": "card", "x": L, "y": 0.0295, "w": 0.0035, "h": 0.017,
         "fill": T["main"], "radius": 0.0},
        {"type": "text", "text": f"{ORG_SHORT}  {EVENT} 결과보고서", "x": L + 0.016,
         "y": 0.0285, "w": 0.62, "style": "caption", "size": 7.6,
         "color": T["gray"]},
        {"type": "text", "text": title, "x": 0.52, "y": 0.0285, "w": R - 0.52,
         "align": "right", "style": "caption", "size": 7.6, "color": T["main"]},
        {"type": "hairline", "x": L, "y": 0.0505, "w": W, "color": T["hair"]},
        {"type": "hairline", "x": L, "y": 0.944, "w": W, "color": T["hair"]},
        {"type": "text", "text": no, "x": L, "y": 0.9525, "w": 0.05,
         "style": "num_xl", "size": 13, "color": T["main"]},
        {"type": "text", "text": f"{ORG_SHORT}   |   {chapter}", "x": L + 0.048,
         "y": 0.9565, "w": 0.6, "style": "caption", "size": 7.6,
         "color": T["gray"]},
    ]


def chapter_head(T, idx, y=0.072):
    """초대형 숫자 + CHAPTER → + 우측 2줄 컬러 타이틀 + 이중 룰 + 리드."""
    num, t1, t2, lead = CH[idx]
    it = [
        {"type": "text", "text": num, "x": L - 0.004, "y": y - 0.012, "w": 0.20,
         "style": "num_xl", "size": 58, "color": T["main"]},
        {"type": "text", "text": "CHAPTER", "x": L, "y": y + 0.094,
         "w": 0.12, "style": "caption", "size": 8, "color": T["gray"]},
        {"type": "hairline", "x": L, "y": y + 0.1175, "w": 0.111,
         "color": T["main"], "thick": 1.4},
        {"type": "arrow", "x": L + 0.111, "y": y + 0.1133, "w": 0.026,
         "h": 0.0085, "color": T["main"]},
        {"type": "headline", "lines": [t1, t2], "x": 0.255, "y": y - 0.004,
         "w": 0.68, "size": 27, "spacing": 1.18, "color": T["main"]},
        {"type": "hairline", "x": 0.255, "y": y + 0.088, "w": R - 0.255,
         "color": T["main"], "thick": 1.6},
        {"type": "hairline", "x": 0.255, "y": y + 0.0912, "w": R - 0.255,
         "color": T["hair"]},
        {"type": "text", "text": lead, "x": 0.255, "y": y + 0.100, "w": R - 0.255,
         "style": "body", "size": 9, "spacing": 1.6, "color": T["body"]},
    ]
    return it, y + 0.166


def sec(T, y, title, note=None):
    """◉ 컬러 원형 불릿 섹션 헤더."""
    it = [
        {"type": "chip", "x": L, "y": y, "d": 0.020, "text": "", "fill": T["main"]},
        {"type": "chip", "x": L + 0.0062, "y": y + 0.0062 * SQ, "d": 0.0076,
         "text": "", "fill": T["bg"]},
        {"type": "text", "text": title, "x": L + 0.030, "y": vc(y, 0.020 * SQ, 11.5),
         "w": 0.56, "style": "cardtitle", "size": 11.5, "color": T["ink"]},
    ]
    if note:
        it.append({"type": "text", "text": note, "x": 0.50,
                   "y": vc(y, 0.020 * SQ, 8), "w": R - 0.50, "align": "right",
                   "style": "caption", "size": 8, "color": T["gray"]})
    return it, y + 0.032


def subcap(T, y, text):
    """섹션 아래 · 한 줄 캡션."""
    return [{"type": "text", "text": "· " + text, "x": L + 0.030, "y": y,
             "w": W - 0.030, "style": "body", "size": 8.6,
             "color": T["gray"]}], y + 0.026


def rail_label(T, x, y, w, h, text, fill=None, ink=None, size=8.8):
    """좌측 라벨 레일 칸."""
    return [
        {"type": "card", "x": x, "y": y, "w": w, "h": h,
         "fill": fill or T["rail"], "radius": 0.35},
        {"type": "text", "text": text, "x": x, "y": vc(y, h, size), "w": w,
         "align": "center", "style": "cardtitle", "size": size,
         "color": ink or T["rail_ink"]},
    ]


def cells_row(T, x, y, w, h, cells, level, gap=0.008):
    """계층 색이 다른 셀 그리드 한 줄."""
    styles = {
        1: dict(fill=T["main"], ink="FFFFFF", outline=None, size=10.5, bold=True),
        2: dict(fill=T["sub"], ink="FFFFFF", outline=None, size=9.2, bold=True),
        3: dict(fill=T["tint"], ink=T["main"], outline=T["main"], size=9.0,
                bold=True),
        4: dict(fill=T["neutral"], ink=T["body"], outline=None, size=8.3,
                bold=False),
    }[level]
    n = len(cells)
    cw = (w - gap * (n - 1)) / n
    it = []
    for i, c in enumerate(cells):
        cx = x + i * (cw + gap)
        card = {"type": "card", "x": cx, "y": y, "w": cw, "h": h,
                "fill": styles["fill"], "radius": 0.30}
        if styles["outline"]:
            card["outline"] = styles["outline"]
        it.append(card)
        lines = c.split("\n")
        th = len(lines) * styles["size"] * 1.45 * PT
        it.append({"type": "text", "lines": lines, "x": cx + 0.008,
                   "y": y + (h - th) / 2, "w": cw - 0.016, "align": "center",
                   "style": "cardtitle" if styles["bold"] else "body",
                   "size": styles["size"], "spacing": 1.45,
                   "color": styles["ink"]})
    return it


def strategy_rail(T, y):
    """비전→핵심가치→전략→과제 계층 레일 (브로슈어 핵심 문법)."""
    it = []
    heights = {1: 0.036, 2: 0.032, 3: 0.032, 4: 0.062}
    for label, level, cells in STRATEGY:
        h = heights[level]
        it += rail_label(T, L, y, RAIL_W, h, label)
        it += cells_row(T, CX, y, CW, h, cells, level)
        # 레일과 셀을 잇는 점선
        it.append({"type": "hairline", "x": L + RAIL_W, "y": y + h / 2,
                   "w": 0.016, "color": T["hair"]})
        y += h + 0.009
    return it, y


def table(T, x, y, w, colw, header, rows, row_h=0.0275, hdr_h=0.030,
          aligns=None, size=8.8, tint_col=None, sum_row=None, dashed=True):
    """컬러 헤더 + 세로 구분선 + 점선 가로선 (브로슈어식 표)."""
    aligns = aligns or ["left"] * len(colw)
    xs, acc = [], 0.0
    for cwf in colw:
        xs.append(x + acc * w)
        acc += cwf
    it = [{"type": "card", "x": x, "y": y, "w": w, "h": hdr_h,
           "fill": T["sub"], "radius": 0.0}]
    for i, (cx, cwf, hd) in enumerate(zip(xs, colw, header)):
        pad = 0.016 if aligns[i] == "left" else 0.0
        it.append({"type": "text", "text": hd, "x": cx + pad,
                   "y": vc(y, hdr_h, size), "w": cwf * w - pad * 2,
                   "align": aligns[i], "style": "cardtitle", "size": size,
                   "color": "FFFFFF"})
        if i:
            it.append({"type": "card", "x": cx - 0.0006, "y": y + 0.006,
                       "w": 0.0012, "h": hdr_h - 0.012, "fill": T["sub_l"],
                       "radius": 0.0})
    ry = y + hdr_h
    body = list(rows) + ([sum_row] if sum_row else [])
    for r_i, row in enumerate(body):
        is_sum = sum_row is not None and r_i == len(body) - 1
        if is_sum:
            it.append({"type": "card", "x": x, "y": ry, "w": w, "h": row_h,
                       "fill": T["tint2"], "radius": 0.0})
        elif tint_col is not None:
            it.append({"type": "card", "x": xs[tint_col], "y": ry,
                       "w": colw[tint_col] * w, "h": row_h, "fill": T["neutral"],
                       "radius": 0.0})
        for i, (cx, cwf, cell) in enumerate(zip(xs, colw, row)):
            pad = 0.016 if aligns[i] == "left" else 0.0
            strong = is_sum or (tint_col is not None and i == tint_col)
            it.append({"type": "text", "text": cell, "x": cx + pad,
                       "y": vc(ry, row_h, size), "w": cwf * w - pad * 2,
                       "align": aligns[i],
                       "style": "cardtitle" if strong else "body", "size": size,
                       "color": T["ink"] if strong else T["body"]})
        it.append({"type": "hairline", "x": x, "y": ry + row_h - 0.0006, "w": w,
                   "color": T["gray"] if is_sum else T["hair"],
                   "dash": "dash" if (dashed and not is_sum) else None})
        ry += row_h
    return it, ry


def node_row(T, y, d=0.088):
    """원형 노드 4개 + 아래 캡션 (브로슈어 Change Together 문법)."""
    it = []
    span = W / 4
    it.append({"type": "hairline", "x": L + span / 2, "y": y + d * SQ / 2,
               "w": W - span, "color": T["hair"], "thick": 1.4})
    for i, (en, ko, desc) in enumerate(NODES):
        cx = L + i * span + span / 2
        fill = T["main"] if i % 2 == 0 else T["sub"]
        it += [
            {"type": "shape", "shape": "oval", "x": cx - d / 2, "y": y,
             "w": d, "h": d * SQ, "fill": fill},
            {"type": "text", "text": en, "x": cx - d / 2, "y": y + 0.014,
             "w": d, "align": "center", "style": "caption", "size": 8,
             "color": "FFFFFF"},
            {"type": "text", "text": ko, "x": cx - d / 2, "y": y + 0.030,
             "w": d, "align": "center", "style": "cardtitle", "size": 10.5,
             "color": "FFFFFF"},
            {"type": "text", "lines": desc.split("\n"), "x": cx - span / 2 + 0.010,
             "y": y + d * SQ + 0.010, "w": span - 0.020, "align": "center",
             "style": "body", "size": 8.3, "spacing": 1.5, "color": T["body"]},
        ]
    return it, y + d * SQ + 0.010 + 0.048


def goal_cards(T, y, h=0.080):
    """목표 ▶▶▶ 실적 비교 카드."""
    it = []
    gap = 0.012
    cw = (W - gap * 3) / 4
    for i, (name, goal, real, rate) in enumerate(GOALS):
        cx = L + i * (cw + gap)
        it += [
            {"type": "card", "x": cx, "y": y, "w": cw, "h": h,
             "fill": T["neutral"], "radius": 0.10},
            {"type": "card", "x": cx, "y": y, "w": cw, "h": 0.021,
             "fill": T["sub"], "radius": 0.10},
            {"type": "text", "text": name, "x": cx, "y": vc(y, 0.021, 8.4),
             "w": cw, "align": "center", "style": "cardtitle", "size": 8.4,
             "color": "FFFFFF"},
            {"type": "text",
             "runs": [[{"t": goal, "color": T["gray"], "font": "body_sb",
                        "size": 9.5},
                       {"t": "  ▶▶▶  ", "color": T["main_l"], "font": "body",
                        "size": 7.5},
                       {"t": real, "color": T["main"], "font": "display_b",
                        "size": 12}]],
             "x": cx, "y": y + 0.032, "w": cw, "align": "center",
             "style": "body"},
            {"type": "hairline", "x": cx + 0.016, "y": y + 0.058,
             "w": cw - 0.032, "color": T["hair"]},
            {"type": "text", "text": "달성률 " + rate, "x": cx,
             "y": y + 0.062, "w": cw, "align": "center", "style": "caption",
             "size": 8, "color": T["sub"]},
        ]
    return it, y + h


def gantt(T, y, weeks=6, row_h=0.030):
    """주차 그리드 간트 — 그룹 라벨 + 주 서브컬럼."""
    it = []
    lw = 0.20          # 단계명
    dw = 0.17          # 기간
    gx = L + lw + dw
    gw = W - lw - dw - 0.30
    tw = 0.30          # 주요 내용
    cw = gw / weeks
    hdr_h = 0.028
    it.append({"type": "card", "x": L, "y": y, "w": W, "h": hdr_h,
               "fill": T["sub"], "radius": 0.0})
    it += [
        {"type": "text", "text": "단    계", "x": L, "y": vc(y, hdr_h, 8.8),
         "w": lw, "align": "center", "style": "cardtitle", "size": 8.8,
         "color": "FFFFFF"},
        {"type": "text", "text": "기    간", "x": L + lw, "y": vc(y, hdr_h, 8.8),
         "w": dw, "align": "center", "style": "cardtitle", "size": 8.8,
         "color": "FFFFFF"},
        {"type": "text", "text": "주요 내용", "x": gx + gw, "y": vc(y, hdr_h, 8.8),
         "w": tw, "align": "center", "style": "cardtitle", "size": 8.8,
         "color": "FFFFFF"},
    ]
    for w_i in range(weeks):
        it.append({"type": "text", "text": f"{w_i + 1}주", "x": gx + w_i * cw,
                   "y": vc(y, hdr_h, 7.8), "w": cw, "align": "center",
                   "style": "caption", "size": 7.8, "color": "FFFFFF"})
    ry = y + hdr_h
    for name, period, start, span, desc in SCHEDULE:
        it += [
            {"type": "card", "x": L, "y": ry, "w": lw, "h": row_h,
             "fill": T["neutral"], "radius": 0.0},
            {"type": "text", "text": name, "x": L, "y": vc(ry, row_h, 8.8),
             "w": lw, "align": "center", "style": "cardtitle", "size": 8.8,
             "color": T["ink"]},
            {"type": "text", "text": period, "x": L + lw, "y": vc(ry, row_h, 8.5),
             "w": dw, "align": "center", "style": "body", "size": 8.5,
             "color": T["body"]},
            {"type": "text", "text": desc, "x": gx + gw + 0.010,
             "y": vc(ry, row_h, 8.3), "w": tw - 0.014, "style": "body",
             "size": 8.3, "color": T["body"]},
        ]
        for w_i in range(weeks):
            it.append({"type": "card", "x": gx + w_i * cw + 0.0008, "y": ry + 0.004,
                       "w": cw - 0.0016, "h": row_h - 0.008,
                       "fill": T["bg"], "radius": 0.0})
        bx = gx + start * cw + 0.002
        bw = span * cw - 0.004
        it.append({"type": "card", "x": bx, "y": ry + 0.0075, "w": bw,
                   "h": row_h - 0.015, "fill": T["main"], "radius": 0.18})
        for w_i in range(1, weeks):
            it.append({"type": "card", "x": gx + w_i * cw - 0.0004, "y": ry,
                       "w": 0.0008, "h": row_h, "fill": T["hair"], "radius": 0.0})
        it.append({"type": "hairline", "x": L, "y": ry + row_h - 0.0006, "w": W,
                   "color": T["hair"]})
        ry += row_h
    return it, ry


def step_chain(T, y, d=0.052):
    """STEP 원형 체인 + 라벨 박스."""
    it = []
    n = len(STEPS)
    span = W / n
    it.append({"type": "hairline", "x": L + span / 2, "y": y + d * SQ / 2,
               "w": W - span, "color": T["hair"], "thick": 2.2, "dash": "dash"})
    for i, (name, desc, when) in enumerate(STEPS):
        cx = L + i * span + span / 2
        it += [
            {"type": "shape", "shape": "oval", "x": cx - d / 2, "y": y, "w": d,
             "h": d * SQ, "fill": T["main"] if i == n - 1 else T["sub"]},
            {"type": "text", "text": f"0{i + 1}", "x": cx - d / 2,
             "y": vc(y, d * SQ, 11), "w": d, "align": "center",
             "style": "cardtitle", "size": 11, "color": "FFFFFF"},
            {"type": "card", "x": cx - span / 2 + 0.010, "y": y + d * SQ + 0.012,
             "w": span - 0.020, "h": 0.046, "fill": T["neutral"], "radius": 0.20},
            {"type": "text", "text": name, "x": cx - span / 2 + 0.010,
             "y": y + d * SQ + 0.019, "w": span - 0.020, "align": "center",
             "style": "cardtitle", "size": 9.2, "color": T["ink"]},
            {"type": "text", "text": desc, "x": cx - span / 2 + 0.006,
             "y": y + d * SQ + 0.036, "w": span - 0.012, "align": "center",
             "style": "caption", "size": 7.6, "color": T["gray"]},
            {"type": "text", "text": when, "x": cx - span / 2 + 0.010,
             "y": y + d * SQ + 0.064, "w": span - 0.020, "align": "center",
             "style": "caption", "size": 7.6, "color": T["main"]},
        ]
    return it, y + d * SQ + 0.064 + 0.024


def org_chart(T, y):
    """다층 조직도 — 상위 1 + 좌우 사이드 + 하위 3."""
    it = []
    top_w, top_h = 0.26, 0.038
    tx = L + (W - top_w) / 2
    it += [
        {"type": "card", "x": tx, "y": y, "w": top_w, "h": top_h,
         "fill": T["main"], "radius": 0.25},
        {"type": "text", "text": "총괄 책임 (사업단 단장)", "x": tx,
         "y": vc(y, top_h, 9.2), "w": top_w, "align": "center",
         "style": "cardtitle", "size": 9.2, "color": "FFFFFF"},
    ]
    # 좌우 사이드 박스 (자문·점검)
    side_w, side_h = 0.185, 0.030
    for sx, label in ((L, "운영 자문 · 중간 점검"), (R - side_w, "정산 · 감사 대응")):
        it += [
            {"type": "card", "x": sx, "y": y + 0.004, "w": side_w, "h": side_h,
             "fill": T["bg"], "outline": T["sub_l"], "radius": 0.25},
            {"type": "text", "text": label, "x": sx, "y": vc(y + 0.004, side_h, 8.2),
             "w": side_w, "align": "center", "style": "body", "size": 8.2,
             "color": T["sub"]},
        ]
    it.append({"type": "hairline", "x": L + side_w, "y": y + 0.004 + side_h / 2,
               "w": tx - L - side_w, "color": T["hair"], "dash": "dash"})
    it.append({"type": "hairline", "x": tx + top_w, "y": y + 0.004 + side_h / 2,
               "w": R - side_w - tx - top_w, "color": T["hair"], "dash": "dash"})
    vy = y + top_h
    it.append({"type": "card", "x": 0.5 - 0.0011, "y": vy, "w": 0.0022,
               "h": 0.020, "fill": T["hair"], "radius": 0.0})
    ly = vy + 0.020
    cw, gap = 0.24, 0.05
    sx0 = L + (W - (cw * 3 + gap * 2)) / 2
    it.append({"type": "hairline", "x": sx0 + cw / 2, "y": ly,
               "w": cw * 2 + gap * 2, "color": T["hair"], "thick": 1.2})
    cy = ly + 0.014
    cells = [("운영 실무 (2명)", "일정 · 예산 · 현장 총괄"),
             ("강사진 (4명)", "회차별 강의 · 실습 지도"),
             ("현장 지원 (3명)", "출결 · 설문 · 기자재")]
    for i, (t1, t2) in enumerate(cells):
        cx = sx0 + i * (cw + gap)
        it += [
            {"type": "card", "x": cx + cw / 2 - 0.0011, "y": ly, "w": 0.0022,
             "h": cy - ly, "fill": T["hair"], "radius": 0.0},
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.048,
             "fill": T["neutral"], "radius": 0.16},
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.0045,
             "fill": T["main"] if i == 0 else T["sub"], "radius": 0.0},
            {"type": "text", "text": t1, "x": cx, "y": cy + 0.010, "w": cw,
             "align": "center", "style": "cardtitle", "size": 9,
             "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx, "y": cy + 0.028, "w": cw,
             "align": "center", "style": "caption", "size": 7.8,
             "color": T["gray"]},
        ]
    return it, cy + 0.048


def bars_block(T, x, y, w, rows, row_h=0.028, maxv=5.0):
    it = []
    label_w = 0.19
    span = w - label_w - 0.056
    for i, (label, v) in enumerate(rows):
        ry = y + i * row_h
        it.append({"type": "text", "text": label, "x": x, "y": vc(ry, row_h, 8.6),
                   "w": label_w - 0.008, "style": "body", "size": 8.6,
                   "color": T["body"]})
        bh = 0.0125
        by = ry + (row_h - bh) / 2
        it += [
            {"type": "card", "x": x + label_w, "y": by, "w": span, "h": bh,
             "fill": T["neutral2"], "radius": 0.5},
            {"type": "card", "x": x + label_w, "y": by, "w": span * v / maxv,
             "h": bh, "fill": T["main"] if v >= 4.6 else T["sub"], "radius": 0.5},
            {"type": "text", "text": f"{v:.1f}", "x": x + label_w + span + 0.008,
             "y": vc(ry, row_h, 8.6), "w": 0.045, "style": "cardtitle",
             "size": 8.6, "color": T["main"]},
        ]
    return it, y + row_h * len(rows)


def photo_grid(T, y, cols=2, rows=2):
    it = []
    gap = 0.020
    cw = (W - gap * (cols - 1)) / cols
    ch = cw * (2 / 3) * SQ
    cap_h = 0.024
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        cx = L + c * (cw + gap)
        cy = y + r * (ch + cap_h + 0.022)
        it += [
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": ch,
             "fill": T["neutral"], "radius": 0.05, "outline": T["hair"]},
            {"type": "image", "path": f"assets/brand/{T['emblem_wm']}",
             "x": cx + cw / 2 - 0.050, "y": cy + ch / 2 - 0.050 * SQ,
             "w": 0.10, "h": 0.10 * SQ},
            {"type": "text", "text": "사진 삽입 영역", "x": cx,
             "y": cy + ch - 0.026, "w": cw, "align": "center", "style": "caption",
             "size": 7.4, "color": T["gray"]},
            {"type": "card", "x": cx, "y": cy + ch + 0.005, "w": cw, "h": cap_h,
             "fill": T["sub"], "radius": 0.20},
            {"type": "text", "text": f"[사진 {i + 1}] {PHOTOS[i]}", "x": cx,
             "y": vc(cy + ch + 0.005, cap_h, 8.2), "w": cw, "align": "center",
             "style": "cardtitle", "size": 8.2, "color": "FFFFFF"},
        ]
    return it, y + rows * (ch + cap_h + 0.022)


# ────────────────────────────────────────────────────────────── 페이지
def p01_cover(T):
    it = []
    on_band = False
    if T["cover_img"] and (PROJECTS / T["slug"] / "assets" / "cover_bg.png").exists():
        it.append({"type": "image", "path": "assets/cover_bg.png", "x": 0.0,
                   "y": 0.0, "w": 1.0, "h": 1.0})
    else:
        it += [
            {"type": "card", "x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0,
             "fill": T["bg"], "radius": 0.0},
            {"type": "card", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.26,
             "fill": T["sub"], "grad": [T["sub_l"], T["sub"]], "radius": 0.0},
            {"type": "card", "x": 0.0, "y": 0.26, "w": 1.0, "h": 0.006,
             "fill": T["main"], "radius": 0.0},
            {"type": "card", "x": 0.0, "y": 0.26, "w": 0.24, "h": 0.006,
             "fill": T["main_l"], "radius": 0.0},
        ]
        on_band = True
    # 상단 기관 로크업 — 밴드 위에서는 백색 교표·백색 텍스트
    emb = T["emblem_white"] if on_band else T["emblem"]
    it += [
        {"type": "image", "path": f"assets/brand/{emb}", "x": L,
         "y": 0.066, "w": 0.080, "h": 0.080 * SQ},
        {"type": "text", "text": "경북대학교", "x": L + 0.094, "y": 0.078,
         "w": 0.4, "style": "cardtitle", "size": 12.5,
         "color": "FFFFFF" if on_band else T["ink"]},
        {"type": "text", "text": ORG_SHORT, "x": L + 0.095, "y": 0.099, "w": 0.5,
         "style": "caption", "size": 8,
         "color": T["dark_sub"] if on_band else T["gray"]},
    ]
    # 타이틀 블록
    it += [
        {"type": "text", "text": f"「{EVENT}」", "x": L, "y": 0.395, "w": 0.7,
         "style": "cardtitle", "size": 12.5, "color": T["main"]},
        {"type": "text", "text": "역량강화 프로그램", "x": L, "y": 0.421, "w": 0.7,
         "style": "body", "size": 11, "color": T["gray"]},
        {"type": "headline", "lines": ["결과보고서"], "x": L - 0.006, "y": 0.452,
         "w": 0.8, "size": 44, "color": T["ink"]},
        {"type": "card", "x": L, "y": 0.548, "w": 0.075, "h": 0.006,
         "fill": T["main"], "radius": 0.0},
        {"type": "card", "x": L + 0.083, "y": 0.5495, "w": 0.038, "h": 0.003,
         "fill": T["sub"], "radius": 0.0},
        {"type": "text", "text": "RESULT  REPORT", "x": L, "y": 0.566, "w": 0.5,
         "style": "caption", "size": 8.5, "color": T["gray"]},
    ]
    # 하단 정보 — 라벨 레일식
    ry = 0.690
    rows = [("주    최", "대구광역시"), ("주    관", ORG),
            ("수행기관", "모드어스 스튜디오"),
            ("운영기간", "2026. 05. 12. ~ 06. 20.")]
    it.append({"type": "hairline", "x": L, "y": ry - 0.018, "w": 0.60,
               "color": T["main"], "thick": 1.6})
    for lab, val in rows:
        it += rail_label(T, L, ry, 0.095, 0.028, lab, size=8.4)
        it.append({"type": "text", "text": val, "x": L + 0.113,
                   "y": vc(ry, 0.028, 9.6), "w": 0.6, "style": "body",
                   "size": 9.6, "color": T["body"]})
        ry += 0.036
    it += [
        {"type": "hairline", "x": L, "y": ry + 0.004, "w": 0.60,
         "color": T["hair"]},
        {"type": "text", "text": "2026.  06.", "x": L, "y": 0.888, "w": 0.4,
         "style": "cardtitle", "size": 10.5, "color": T["main"]},
        {"type": "text", "text": ORG, "x": 0.42, "y": 0.890, "w": R - 0.42,
         "align": "right", "style": "body", "size": 9, "color": T["gray"]},
    ]
    return it


def p02_toc(T):
    it = page_frame(T, "02", "목  차", "CONTENTS")
    y = 0.086
    it += [
        {"type": "text", "text": f"{EVENT} 결과보고서", "x": L, "y": y, "w": 0.7,
         "style": "caption", "size": 8.6, "color": T["gray"]},
        {"type": "headline", "lines": ["Contents"], "x": L - 0.004, "y": y + 0.020,
         "w": 0.7, "size": 32, "color": T["main"]},
        {"type": "hairline", "x": L, "y": y + 0.094, "w": 0.07,
         "color": T["main"], "thick": 2.6},
        {"type": "hairline", "x": L + 0.078, "y": y + 0.0952, "w": W - 0.078,
         "color": T["hair"]},
    ]
    ry = y + 0.126
    for i, (no, title, pg) in enumerate(TOC):
        it += [
            {"type": "card", "x": L, "y": ry, "w": 0.034, "h": 0.024,
             "fill": T["main"] if i % 2 == 0 else T["sub"], "radius": 0.30},
            {"type": "text", "text": no, "x": L, "y": vc(ry, 0.024, 8.6),
             "w": 0.034, "align": "center", "style": "cardtitle", "size": 8.6,
             "color": "FFFFFF"},
            {"type": "text", "text": title, "x": L + 0.052,
             "y": vc(ry, 0.024, 11.5), "w": 0.6, "style": "cardtitle",
             "size": 11.5, "color": T["ink"]},
            {"type": "hairline", "x": L + 0.052, "y": ry + 0.030,
             "w": W - 0.052 - 0.05, "color": T["hair"], "dash": "dash"},
            {"type": "text", "text": pg, "x": R - 0.05,
             "y": vc(ry, 0.024, 10), "w": 0.05, "align": "right",
             "style": "cardtitle", "size": 10, "color": T["main"]},
        ]
        ry += 0.060
    # 하단 별첨 + 워터마크
    it += [
        {"type": "card", "x": L, "y": 0.700, "w": W, "h": 0.052,
         "fill": T["neutral"], "radius": 0.16},
        {"type": "card", "x": L, "y": 0.700, "w": 0.004, "h": 0.052,
         "fill": T["main"], "radius": 0.0},
        {"type": "text", "text": "별첨 자료", "x": L + 0.016, "y": 0.710,
         "w": 0.14, "style": "cardtitle", "size": 9, "color": T["main"]},
        {"type": "text",
         "text": "① 참여자 서명부   ② 만족도 설문 원본·집계표   "
                 "③ 예산 집행 증빙 일체   ④ 현장 사진 자료",
         "x": L + 0.016, "y": 0.729, "w": W - 0.032, "style": "body",
         "size": 8.6, "color": T["body"]},
        {"type": "image", "path": f"assets/brand/{T['emblem_wm']}",
         "x": 0.5 - 0.085, "y": 0.790, "w": 0.17, "h": 0.17 * SQ},
    ]
    return it


def p03_overview(T):
    it = page_frame(T, "03", "과업추진 개요", "CHAPTER 01")
    head, y = chapter_head(T, 0)
    it += head
    s, y = sec(T, y, "1. 과업 개요", "계약서 및 운영계획서 기준")
    it += s
    # 개요 — 라벨 레일 2열
    rh = 0.029
    half = (W - 0.020) / 2
    for i, (lab, val) in enumerate(OVERVIEW):
        r, c = divmod(i, 1)
        ry = y + i * (rh + 0.006)
        it += rail_label(T, L, ry, RAIL_W, rh, lab, size=8.6)
        it += [
            {"type": "card", "x": CX, "y": ry, "w": CW, "h": rh,
             "fill": T["neutral"], "radius": 0.20},
            {"type": "text", "text": val, "x": CX + 0.016, "y": vc(ry, rh, 8.8),
             "w": CW - 0.032, "style": "body", "size": 8.8, "color": T["body"]},
        ]
    y += len(OVERVIEW) * (rh + 0.006) + 0.016
    s, y = sec(T, y, "2. 과업 목표 체계")
    it += s
    sr, y = strategy_rail(T, y)
    it += sr
    y += 0.014
    s, y = sec(T, y, "3. 핵심 성과 요약", "2026. 06. 30. 집계")
    it += s
    gc, y = goal_cards(T, y)
    it += gc
    y += 0.020
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.040,
         "fill": T["tint"], "radius": 0.18, "outline": T["main"]},
        {"type": "text",
         "runs": [[{"t": "종합 평가   ", "color": T["main"], "font": "body_b",
                    "size": 9},
                   {"t": "4개 지표 전부 목표를 상회하였으며, 특히 수료 인원이 "
                         "목표 대비 114%로 가장 높은 달성률을 기록하였다.",
                    "color": T["body"], "font": "body", "size": 9}]],
         "x": L + 0.016, "y": vc(y, 0.040, 9), "w": W - 0.032, "style": "body"},
    ]
    return it


def p04_system(T):
    it = page_frame(T, "04", "과업추진 개요", "추진 체계")
    y = 0.078
    s, y = sec(T, y, "4. 추진 방향", "4대 축")
    it += s
    nr, y = node_row(T, y)
    it += nr
    s, y = sec(T, y, "5. 운영 조직 체계")
    it += s
    c, y = subcap(T, y, "총괄 책임 아래 운영 실무·강사진·현장 지원 3개 팀으로 운영하였다.")
    it += c
    oc, y = org_chart(T, y)
    it += oc
    y += 0.026
    s, y = sec(T, y, "6. 인력 구성 및 역할")
    it += s
    tb, y = table(T, L, y, W, [0.20, 0.24, 0.42, 0.14],
                  ["역    할", "소    속", "담당 업무", "인원"], STAFF,
                  aligns=["center", "center", "left", "center"], tint_col=0)
    it += tb
    y += 0.012
    it.append({"type": "text",
               "text": "※ 강사진 4인은 분야별 전문가로 위촉하였으며, 위촉 공문과 강의계획서는 별첨 자료로 제출한다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8,
               "color": T["gray"]})
    y += 0.036
    s, y = sec(T, y, "7. 협력 체계 및 역할 분담")
    it += s
    gap = 0.016
    cw = (W - gap * 2) / 3
    for i, (t1, t2, t3) in enumerate(PARTNERS):
        cx = L + i * (cw + gap)
        it += [
            {"type": "card", "x": cx, "y": y, "w": cw, "h": 0.082,
             "fill": T["neutral"], "radius": 0.14},
            {"type": "card", "x": cx, "y": y, "w": cw, "h": 0.024,
             "fill": T["main"] if i == 1 else T["sub"], "radius": 0.14},
            {"type": "text", "text": t1, "x": cx, "y": vc(y, 0.024, 8.6),
             "w": cw, "align": "center", "style": "cardtitle", "size": 8.6,
             "color": "FFFFFF"},
            {"type": "text", "text": t2, "x": cx + 0.016, "y": y + 0.031,
             "w": cw - 0.024, "align": "center", "style": "cardtitle",
             "size": 8.4, "color": T["ink"]},
            {"type": "text", "lines": t3.split("\n"), "x": cx + 0.016,
             "y": y + 0.050, "w": cw - 0.032, "style": "caption", "size": 7.8,
             "spacing": 1.5, "color": T["gray"]},
        ]
    y += 0.082 + 0.030
    s, y = sec(T, y, "8. 위험 요인 및 대응 계획")
    it += s
    tb, y = table(T, L, y, W, [0.26, 0.30, 0.44],
                  ["위험 요인", "예상 영향", "대응 계획"], RISKS,
                  aligns=["center", "center", "left"], tint_col=0)
    it += tb
    return it


def p05_promo(T):
    it = page_frame(T, "05", "과업 수행 내역", "CHAPTER 02")
    head, y = chapter_head(T, 1)
    it += head
    s, y = sec(T, y, "1. 추진 일정", "■ 수행 구간 / 총 6주")
    it += s
    g, y = gantt(T, y)
    it += g
    y += 0.020
    s, y = sec(T, y, "2. 모집 · 홍보 실적", "집계 기준 2026. 05. 09.")
    it += s
    tb, y = table(T, L, y, W, [0.34, 0.24, 0.18, 0.24],
                  ["홍보 채널", "게시 기간", "게시 건수", "도달 · 노출"], PROMO,
                  aligns=["left", "center", "center", "center"], tint_col=0)
    it += tb
    y += 0.012
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.038,
         "fill": T["tint"], "radius": 0.20, "outline": T["main"]},
        {"type": "text",
         "runs": [[{"t": "모집 결과   ", "color": T["main"], "font": "body_b",
                    "size": 9},
                   {"t": "정원 40명 대비 신청 68명 (경쟁률 1.7:1) — 선발 40명, 예비 8명",
                    "color": T["body"], "font": "body", "size": 9}]],
         "x": L + 0.016, "y": vc(y, 0.038, 9), "w": W - 0.032, "style": "body"},
    ]
    y += 0.056
    s, y = sec(T, y, "3. 신청 · 선발 절차")
    it += s
    sc, y = step_chain(T, y)
    it += sc
    y += 0.006
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.040,
         "fill": T["neutral"], "radius": 0.18},
        {"type": "card", "x": L, "y": y, "w": 0.004, "h": 0.040,
         "fill": T["main"], "radius": 0.0},
        {"type": "text",
         "runs": [[{"t": "선발 기준   ", "color": T["main"], "font": "body_b",
                    "size": 8.8},
                   {"t": "① 지역 거주·재직 여부  ② 참여 동기의 구체성  "
                         "③ 전 회차 참석 가능 여부 — 동점 시 선착순",
                    "color": T["body"], "font": "body", "size": 8.8}]],
         "x": L + 0.016, "y": vc(y, 0.040, 8.8), "w": W - 0.032,
         "style": "body"},
    ]
    return it


def p06_ops(T):
    it = page_frame(T, "06", "과업 수행 내역", "현장 운영")
    y = 0.078
    s, y = sec(T, y, "4. 사전 준비 사항")
    it += s
    # 준비 4항목 — 번호 박스 + 설명 (2×2)
    gap = 0.018
    cw = (W - gap) / 2
    for i, (t1, t2) in enumerate(PREP):
        r, c = divmod(i, 2)
        cx = L + c * (cw + gap)
        cy = y + r * 0.062
        it += [
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.054,
             "fill": T["neutral"], "radius": 0.16},
            {"type": "card", "x": cx, "y": cy, "w": 0.042, "h": 0.054,
             "fill": T["sub"] if i % 2 else T["main"], "radius": 0.16},
            {"type": "text", "text": f"0{i + 1}", "x": cx, "y": vc(cy, 0.054, 11),
             "w": 0.042, "align": "center", "style": "cardtitle", "size": 11,
             "color": "FFFFFF"},
            {"type": "text", "text": t1, "x": cx + 0.058, "y": cy + 0.010,
             "w": cw - 0.066, "style": "cardtitle", "size": 9.2,
             "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx + 0.058, "y": cy + 0.029,
             "w": cw - 0.062, "style": "caption", "size": 7.9,
             "color": T["gray"]},
        ]
    y += 0.062 * 2 + 0.010
    s, y = sec(T, y, "5. 회차별 운영 시간표", "1일 2회차 · 회차당 3시간")
    it += s
    hdr_h, row_h = 0.028, 0.031
    it.append({"type": "card", "x": L, "y": y, "w": W, "h": hdr_h,
               "fill": T["sub"], "radius": 0.0})
    it += [
        {"type": "text", "text": "시    간", "x": L, "y": vc(y, hdr_h, 8.8),
         "w": 0.15, "align": "center", "style": "cardtitle", "size": 8.8,
         "color": "FFFFFF"},
        {"type": "text", "text": "구    분", "x": L + 0.15, "y": vc(y, hdr_h, 8.8),
         "w": 0.25, "align": "center", "style": "cardtitle", "size": 8.8,
         "color": "FFFFFF"},
        {"type": "text", "text": "세부 내용", "x": L + 0.412,
         "y": vc(y, hdr_h, 8.8), "w": W - 0.412, "style": "cardtitle",
         "size": 8.8, "color": "FFFFFF"},
    ]
    ry = y + hdr_h
    for tm, name, desc, core in TIMETABLE:
        if core:
            it.append({"type": "card", "x": L, "y": ry, "w": W, "h": row_h,
                       "fill": T["tint"], "radius": 0.0})
        it += [
            {"type": "text", "text": tm, "x": L, "y": vc(ry, row_h, 9.2),
             "w": 0.15, "align": "center", "style": "cardtitle", "size": 9.2,
             "color": T["main"] if core else T["gray"]},
            {"type": "text", "text": name, "x": L + 0.15, "y": vc(ry, row_h, 8.8),
             "w": 0.25, "align": "center",
             "style": "cardtitle" if core else "body", "size": 8.8,
             "color": T["ink"] if core else T["gray"]},
            {"type": "text", "text": desc, "x": L + 0.412, "y": vc(ry, row_h, 8.5),
             "w": W - 0.42, "style": "body", "size": 8.5,
             "color": T["body"] if core else T["gray"]},
            {"type": "hairline", "x": L, "y": ry + row_h - 0.0006, "w": W,
             "color": T["hair"], "dash": "dash"},
        ]
        ry += row_h
    y = ry + 0.020
    s, y = sec(T, y, "6. 운영 지원 및 안전 관리")
    it += s
    for i, (t1, t2) in enumerate(OPS):
        r, c = divmod(i, 2)
        cx = L + c * (cw + gap)
        cy = y + r * 0.078
        it += [
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.070,
             "fill": T["bg"], "outline": T["hair"], "radius": 0.14},
            {"type": "card", "x": cx, "y": cy, "w": cw, "h": 0.004,
             "fill": T["main"] if i % 2 == 0 else T["sub"], "radius": 0.0},
            {"type": "text", "text": t1, "x": cx + 0.016, "y": cy + 0.012,
             "w": cw - 0.030, "style": "cardtitle", "size": 9,
             "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx + 0.016, "y": cy + 0.030,
             "w": cw - 0.030, "style": "caption", "size": 7.9, "spacing": 1.45,
             "color": T["gray"]},
        ]
    y += 0.078 * 2 + 0.006
    tb, y = table(T, L, y, W, [0.22, 0.24, 0.18, 0.18, 0.18],
                  ["구    분", "운영 기간", "회차", "연인원", "평균 출석률"], ROUNDS,
                  aligns=["center"] * 5, tint_col=0)
    it += tb
    y += 0.014
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.040,
         "fill": T["tint"], "radius": 0.18, "outline": T["main"]},
        {"type": "text",
         "runs": [[{"t": "운영 총계   ", "color": T["main"], "font": "body_b",
                    "size": 9},
                   {"t": "총 12회차 · 연인원 441명 · 평균 출석률 91.9% "
                         "(목표 85% 대비 +6.9%p)", "color": T["body"],
                    "font": "body", "size": 9}]],
         "x": L + 0.016, "y": vc(y, 0.040, 9), "w": W - 0.032, "style": "body"},
    ]
    y += 0.052
    it.append({"type": "text",
               "text": "※ 연인원은 회차별 출석 인원의 합계이며, 평균 출석률은 회차별 출석률의 산술평균이다. "
                       "회차별 출결 원본은 별첨 ①로 제출한다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8,
               "spacing": 1.5, "color": T["gray"]})
    return it


def p07_result(T):
    it = page_frame(T, "07", "과업 수행 결과", "CHAPTER 03")
    head, y = chapter_head(T, 2)
    it += head
    s, y = sec(T, y, "1. 목표 대비 달성률", "목표 ▶ 실적")
    it += s
    gc, y = goal_cards(T, y)
    it += gc
    y += 0.016
    it.append({"type": "text",
               "text": "※ 달성률은 실적 ÷ 목표 × 100 기준이며, 만족도는 5점 척도 환산값이다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8,
               "color": T["gray"]})
    y += 0.036
    s, y = sec(T, y, "2. 만족도 조사 결과", "응답 114부 / 5점 척도")
    it += s
    bb, by = bars_block(T, L, y, W * 0.615, SATIS)
    it += bb
    cx = L + W * 0.655
    cwid = R - cx
    it += [
        {"type": "card", "x": cx, "y": y - 0.004, "w": cwid, "h": 0.148,
         "fill": T["main"], "radius": 0.14},
        {"type": "text", "text": "종합 만족도", "x": cx, "y": y + 0.014,
         "w": cwid, "align": "center", "style": "caption", "size": 8.4,
         "color": T["dark_sub"]},
        {"type": "text",
         "runs": [[{"t": "4.6", "color": "FFFFFF", "font": "display_b",
                    "size": 30},
                   {"t": " / 5.0", "color": T["dark_sub"], "font": "body_sb",
                    "size": 10}]],
         "x": cx, "y": y + 0.036, "w": cwid, "align": "center", "style": "body"},
        {"type": "hairline", "x": cx + 0.026, "y": y + 0.088, "w": cwid - 0.052,
         "color": T["main_l"]},
        {"type": "text", "lines": ["5점 만점 기준 상위 92%", "재참여 의향 4.5점"],
         "x": cx + 0.012, "y": y + 0.100, "w": cwid - 0.024, "align": "center",
         "style": "caption", "size": 8.2, "spacing": 1.5,
         "color": T["dark_sub"]},
    ]
    y = max(by, y + 0.148) + 0.024
    s, y = sec(T, y, "3. 참여자 의견", "회차 종료 설문 자유기술 발췌")
    it += s
    gap = 0.018
    cw = (W - gap) / 2
    for i, (quote, who) in enumerate(VOICES):
        cx2 = L + i * (cw + gap)
        it += [
            {"type": "card", "x": cx2, "y": y, "w": cw, "h": 0.098,
             "fill": T["neutral"], "radius": 0.14},
            {"type": "text", "text": "“", "x": cx2 + 0.016, "y": y + 0.002,
             "w": 0.06, "style": "num_xl", "size": 22, "color": T["main_l"]},
            {"type": "text", "text": quote, "x": cx2 + 0.040, "y": y + 0.020,
             "w": cw - 0.054, "style": "body", "size": 8.4, "spacing": 1.5,
             "color": T["body"]},
            {"type": "text", "text": f"— {who}", "x": cx2 + 0.016, "y": y + 0.076,
             "w": cw - 0.032, "align": "right", "style": "caption", "size": 7.8,
             "color": T["gray"]},
        ]
    y += 0.098 + 0.030
    s, y = sec(T, y, "4. 성과 분석 및 시사점")
    it += s
    gap3 = 0.016
    cw3 = (W - gap3 * 2) / 3
    for i, (t1, _x, t2) in enumerate(INSIGHT):
        cx3 = L + i * (cw3 + gap3)
        it += [
            {"type": "card", "x": cx3, "y": y, "w": cw3, "h": 0.116,
             "fill": T["bg"], "outline": T["hair"], "radius": 0.14},
            {"type": "card", "x": cx3, "y": y, "w": cw3, "h": 0.004,
             "fill": T["main"] if i == 0 else T["sub"], "radius": 0.0},
            {"type": "card", "x": cx3 + 0.016, "y": y + 0.013, "w": 0.030,
             "h": 0.020, "fill": T["main"] if i == 0 else T["sub"],
             "radius": 0.30},
            {"type": "text", "text": f"0{i + 1}", "x": cx3 + 0.016,
             "y": vc(y + 0.013, 0.020, 8.4), "w": 0.030, "align": "center",
             "style": "cardtitle", "size": 8.4, "color": "FFFFFF"},
            {"type": "text", "text": t1, "x": cx3 + 0.054, "y": y + 0.015,
             "w": cw3 - 0.064, "style": "cardtitle", "size": 9,
             "color": T["ink"]},
            {"type": "text", "text": t2, "x": cx3 + 0.016, "y": y + 0.046,
             "w": cw3 - 0.032, "style": "body", "size": 8.1, "spacing": 1.5,
             "color": T["body"]},
        ]
    return it


def p08_evidence(T):
    it = page_frame(T, "08", "과업 수행 결과", "증빙 자료")
    y = 0.078
    s, y = sec(T, y, "4. 증빙 사진", "촬영 동의 취득 / 원본 별첨")
    it += s
    pg, y = photo_grid(T, y)
    it += pg
    y += 0.024
    s, y = sec(T, y, "5. 산출물 및 제출 자료")
    it += s
    tb, y = table(T, L, y, W, [0.34, 0.22, 0.22, 0.22],
                  ["산 출 물", "형    태", "수    량", "보관 · 제출"], OUTPUTS,
                  aligns=["left", "center", "center", "center"], tint_col=0)
    it += tb
    y += 0.020
    s, y = sec(T, y, "6. 개인정보 및 증빙 관리")
    it += s
    notes = [("촬영 · 활용 동의", "참여자 전원에게 사진 촬영 및 활용 동의서를 받아 보관하였다."),
             ("설문 원본 보관", "만족도 설문 원본 114부는 사업단에서 3년간 보관한다."),
             ("서명부 관리", "회차별 참여자 서명부는 스캔 후 원본과 함께 제출한다.")]
    for i, (t1, t2) in enumerate(notes):
        ry = y + i * 0.030
        it += [
            {"type": "card", "x": L, "y": ry + 0.004, "w": 0.0035, "h": 0.020,
             "fill": T["main"], "radius": 0.0},
            {"type": "text", "text": t1, "x": L + 0.016, "y": ry, "w": 0.17,
             "style": "cardtitle", "size": 8.8, "color": T["ink"]},
            {"type": "text", "text": t2, "x": L + 0.190, "y": ry, "w": W - 0.190,
             "style": "body", "size": 8.6, "color": T["body"]},
            {"type": "hairline", "x": L, "y": ry + 0.024, "w": W,
             "color": T["hair"], "dash": "dash"},
        ]
    return it


def p09_budget(T):
    it = page_frame(T, "09", "산출 내역", "CHAPTER 04")
    head, y = chapter_head(T, 3)
    it += head
    s, y = sec(T, y, "1. 예산 집행 내역", "단위: 원 (부가세 포함)")
    it += s
    tb, y = table(T, L, y, W, [0.24, 0.22, 0.19, 0.19, 0.16],
                  ["항    목", "산출 근거", "편성액", "집행액", "잔    액"], BUDGET,
                  aligns=["left", "center", "right", "right", "right"],
                  tint_col=0, sum_row=BUDGET_SUM)
    it += tb
    y += 0.012
    it.append({"type": "text",
               "text": "※ 집행 잔액 100,000원은 정산 시 반납 예정이며, 세부 증빙(계약서·세금계산서·이체확인증)은 별첨 ③으로 제출한다.",
               "x": L, "y": y, "w": W, "style": "caption", "size": 8,
               "spacing": 1.5, "color": T["gray"]})
    y += 0.034
    s, y = sec(T, y, "2. 정산 결과 요약")
    it += s
    gap = 0.016
    cw = (W - gap * 2) / 3
    summ = [("편성액", "27,000,000", "원", False), ("집행액", "26,900,000", "원", False),
            ("집행률", "99.6", "%", True)]
    for i, (lab, val, unit, hi) in enumerate(summ):
        cx = L + i * (cw + gap)
        it += [
            {"type": "card", "x": cx, "y": y, "w": cw, "h": 0.064,
             "fill": T["main"] if hi else T["neutral"], "radius": 0.14},
            {"type": "text", "text": lab, "x": cx + 0.016, "y": y + 0.010,
             "w": cw - 0.032, "style": "caption", "size": 8.2,
             "color": T["dark_sub"] if hi else T["gray"]},
            {"type": "text",
             "runs": [[{"t": val, "color": "FFFFFF" if hi else T["ink"],
                        "font": "display_b", "size": 16},
                       {"t": " " + unit,
                        "color": T["dark_sub"] if hi else T["gray"],
                        "font": "body_sb", "size": 9}]],
             "x": cx + 0.016, "y": y + 0.030, "w": cw - 0.032, "style": "body"},
        ]
    y += 0.064 + 0.022
    s, y = sec(T, y, "3. 제출 서류")
    it += s
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.038,
         "fill": T["neutral"], "radius": 0.16},
        {"type": "card", "x": L, "y": y, "w": 0.004, "h": 0.038,
         "fill": T["main"], "radius": 0.0},
        {"type": "text",
         "runs": [[{"t": "별첨   ", "color": T["main"], "font": "body_b",
                    "size": 8.8},
                   {"t": "① 참여자 서명부   ② 만족도 설문 원본·집계표   "
                         "③ 예산 집행 증빙 일체   ④ 현장 사진 자료",
                    "color": T["body"], "font": "body", "size": 8.8}]],
         "x": L + 0.016, "y": vc(y, 0.038, 8.8), "w": W - 0.032, "style": "body"},
    ]
    y += 0.058
    # 마무리 선언 밴드 + 서명
    it += [
        {"type": "card", "x": L, "y": y, "w": W, "h": 0.052,
         "fill": T["main"], "grad": [T["main_l"], T["main"]], "radius": 0.14},
        {"type": "text",
         "text": "위와 같이 과업을 계획된 일정과 범위에 따라 정상적으로 완료하였음을 보고합니다.",
         "x": L + 0.02, "y": vc(y, 0.052, 10.5), "w": W - 0.04,
         "align": "center", "style": "cardtitle", "size": 10.5,
         "color": "FFFFFF"},
    ]
    sy = y + 0.074
    it += [
        {"type": "text", "text": "2026.  06.  30.", "x": 0.40, "y": sy,
         "w": R - 0.40, "align": "right", "style": "cardtitle", "size": 10.5,
         "color": T["ink"]},
        {"type": "text", "text": ORG, "x": 0.40, "y": sy + 0.028, "w": R - 0.40,
         "align": "right", "style": "headline", "size": 13.5, "color": T["ink"]},
        {"type": "text", "text": "수행기관  모드어스 스튜디오        (인)", "x": 0.40,
         "y": sy + 0.058, "w": R - 0.40, "align": "right", "style": "body",
         "size": 9, "color": T["gray"]},
    ]
    return it


PAGES = [p01_cover, p02_toc, p03_overview, p04_system, p05_promo, p06_ops,
         p07_result, p08_evidence, p09_budget]


def build(T):
    proj = PROJECTS / T["slug"]
    (proj / "pages").mkdir(parents=True, exist_ok=True)
    (proj / "assets").mkdir(parents=True, exist_ok=True)
    if T["cover_img"] and COVER_SRC.exists():
        shutil.copy(COVER_SRC, proj / "assets" / "cover_bg.png")
    for i, fn in enumerate(PAGES, start=1):
        items = fn(T)
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
    import sys
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("결보 브로슈어 템플릿 생성")
    for T in (CRIMSON, NAVYGOLD, GOVBLUE, TEAL):
        if only and T["slug"] != only:
            continue
        build(T)
