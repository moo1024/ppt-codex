#!/usr/bin/env python3
"""정렬·빈칸 기계 검수기 (v7 덱 완성 선언 전 필수 게이트).

layout_spec.json들을 읽어 눈대중 배치에서 반복된 4대 오류를 좌표로 잡는다:
  A. 카드 행 바닥 불일치   — 같은 y로 나란한 카드들의 h가 달라 바닥선이 안 맞음
  B. num_xl ↔ 헤어라인 겹침 — 빅넘버 바로 밑 밑줄이 숫자에 붙어 카드마다 어긋나 보임
  C. 행 y 미세 불일치       — 나란히 놓인(같은 style) 텍스트 행의 y가 미세하게 다름
  D. 하단 빈칸             — 본문 바닥과 SO WHAT/band 사이가 떠서 텅 빈 느낌

사용:  python3 tools/check_align.py <slug> [slug2 ...]
반환:  경고 있으면 종료코드 1 (완성 선언 금지). 0이면 통과.

임계값은 이번 세션 반려 사례(deepwork p02·p04, polaris p05)에 맞춰 보수적으로 잡음.
"""
from __future__ import annotations

import glob
import json
import os
import sys

# 본문 존(header/footer 제외) 및 오차 허용치
HEADER_Y = 0.25       # 이 위(라벨·헤드라인·sub)는 정렬 검사 제외
FOOTER_Y = 0.90       # 이 아래(meta·페이지번호·source)는 제외
CARD_ROW_TOL = 0.012  # 같은 "행"으로 볼 카드 y 근접
CARD_H_TOL = 0.006    # 카드 행 내 h 허용 편차
NUM_LINE_GAP = 0.045  # num_xl 아래 이 안에 헤어라인 있으면 겹침 위험
ROW_Y_TOL = 0.009     # 같은 행으로 볼 텍스트 y 근접
ROW_Y_MISMATCH = 0.004   # 이 이상 어긋나면 행 미정렬(눈에 보이는 ≥0.005만; 0.003 광학보정은 통과)
DEAD_GAP = 0.09       # 본문 바닥 → band 간격이 이 이상이면 빈칸("빈 구간 0.1 이상" 규칙 기준 여유)

_SIZED = ("card", "chart", "table", "image")


def _bottom(it):
    y = it.get("y")
    if y is None:
        return None
    if it.get("type") in _SIZED:
        return y + it.get("h", 0)
    return y + 0.028  # 텍스트 1줄 추정(보수적)


def check_page(items):
    warns = []

    # A. 카드 행 바닥 불일치
    cards = [it for it in items if it.get("type") == "card" and "h" in it]
    used = [False] * len(cards)
    for i, c in enumerate(cards):
        if used[i]:
            continue
        grp = [c]
        for j in range(i + 1, len(cards)):
            if not used[j] and abs(cards[j].get("y", 0) - c.get("y", 0)) < CARD_ROW_TOL:
                grp.append(cards[j])
                used[j] = True
        if len(grp) >= 2:
            hs = [round(g.get("h", 0), 3) for g in grp]
            if max(hs) - min(hs) > CARD_H_TOL:
                warns.append(f"[A] 카드 행 바닥 불일치: y≈{c.get('y'):.3f}에 {len(grp)}개, h={hs} — 바닥선 안 맞음")

    # B. num_xl ↔ 헤어라인 겹침
    nums = [it for it in items if it.get("type") == "text" and it.get("style") == "num_xl"]
    hairs = [it for it in items if it.get("type") == "hairline"]
    for n in nums:
        nx0 = n.get("x", 0); nx1 = nx0 + n.get("w", 0.2); ny = n.get("y", 0)
        for h in hairs:
            hx0 = h.get("x", 0); hx1 = hx0 + h.get("w", 0); hy = h.get("y", 0)
            if hx0 < nx1 and hx1 > nx0 and 0 <= hy - ny < NUM_LINE_GAP:
                warns.append(f"[B] num_xl '{n.get('text','')}' 밑 헤어라인 근접: 숫자 y{ny:.3f} → 라인 y{hy:.3f} (겹침위험, 라인을 ≥{NUM_LINE_GAP:.02f} 아래로)")

    # C. 행 y 미세 불일치 (같은 style, 나란히, x 다름)
    texts = [it for it in items
             if it.get("type") == "text" and "y" in it
             and HEADER_Y <= it["y"] < FOOTER_Y]
    used = [False] * len(texts)
    for i, t in enumerate(texts):
        if used[i]:
            continue
        grp = [t]
        for j in range(i + 1, len(texts)):
            tj = texts[j]
            if (not used[j] and tj.get("style") == t.get("style")
                    and abs(tj["y"] - t["y"]) < ROW_Y_TOL
                    and abs(tj.get("x", 0) - t.get("x", 0)) > 0.05):
                grp.append(tj)
                used[j] = True
        if len(grp) >= 2:
            ys = sorted({round(g["y"], 4) for g in grp})
            if len(ys) > 1 and (max(ys) - min(ys)) > ROW_Y_MISMATCH:
                warns.append(f"[C] 행 y 미세 불일치(style={t.get('style')}): {len(grp)}칸 y={ys} — 같은 값으로 통일")

    # D. 하단 빈칸
    bands = [it for it in items if it.get("type") in ("band", "sowhat")]
    band_y = min((b.get("y", 0.845) for b in bands), default=None)
    if band_y and band_y > 0.78:
        bottoms = []
        for it in items:
            if it.get("type") in ("band", "sowhat", "glow", "image", "scrim"):
                continue
            y = it.get("y")
            if y is None or y >= FOOTER_Y or y < HEADER_Y:
                continue
            b = _bottom(it)
            if b is not None and b < band_y + 0.001:
                bottoms.append(b)
        if bottoms:
            cb = max(bottoms)
            if band_y - cb > DEAD_GAP:
                warns.append(f"[D] 하단 빈칸: 본문 바닥 {cb:.3f} → 바 {band_y:.3f} (간격 {band_y-cb:.3f}) — 콘텐츠를 y0.79까지 채울 것")

    return warns


def check_slug(slug):
    base = f"projects/{slug}/pages"
    page_dirs = sorted(glob.glob(f"{base}/p[0-9][0-9]"))
    total = 0
    if not page_dirs:
        print(f"  (페이지 없음: {base})")
        return 0
    for d in page_dirs:
        sp = os.path.join(d, "layout_spec.json")
        if not os.path.exists(sp):
            continue
        spec = json.load(open(sp, encoding="utf-8"))
        warns = check_page(spec.get("items", []))
        pg = os.path.basename(d)
        if warns:
            total += len(warns)
            print(f"  {pg}:")
            for w in warns:
                print(f"    ✗ {w}")
        else:
            print(f"  {pg}: ✓")
    return total


def main(argv):
    if not argv:
        print("사용: python3 tools/check_align.py <slug> [slug2 ...]")
        return 2
    grand = 0
    for slug in argv:
        print(f"■ {slug}")
        grand += check_slug(slug)
    print()
    if grand:
        print(f"✗ 정렬 경고 {grand}건 — 완성 선언 금지, 좌표 수정 후 재검수")
        return 1
    print("✓ 정렬 검수 통과 (0건)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
