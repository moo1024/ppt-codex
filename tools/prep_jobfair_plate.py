"""잡페어 완성 포스터 — kie 인물컷 → 배경 투명 누끼 PNG + 배치 실측 좌표.

kie는 인물·조명·질감만 담당하고, **대각 컬러 패널은 layout_spec의 네이티브 poly**로
그린다 (5종 완전 동일한 각도). 그래서 여기서 할 일은 두 가지뿐이다:

  ① 순백 배경(+생성물에 딸려온 AI 컬러 패널)을 통째로 투명으로 날린 RGBA 누끼
  ② 랜야드·배지를 **브랜드 정색**으로 통일 (AI가 낸 근사색을 안 쓴다)

그리고 배치를 눈대중으로 하지 않도록 실측 좌표(cut-*.json)를 같이 뱉는다 —
머리 상단/좌우, 전체 bbox, 행별 실루엣 윤곽. 생성기가 이 숫자로
5종의 머리 크기·위치를 똑같이 맞추고 텍스트 충돌을 자동 검증한다.

주의: `밝은 옷` 함정. 흰 셔츠는 배경과 밝기가 같아서 테두리 flood fill에 그대로
빨려간다 (삼성 컷에서 블라우스가 통째로 날아갔다). lum<200 실루엣의 hole-fill로
감싸 보호한다.

사용:  python3 tools/prep_jobfair_plate.py [키 ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SPOTS = ROOT / "projects" / "knu-jobfair-final" / "assets" / "spots"

# 브랜드 정색 (브리프 5종 표)
BRAND = {
    "naver": "03C75A",
    "hyundai": "002C5F",
    "skhynix": "EA5514",
    "samsung": "1428A0",
    "kepco": "6B2C91",
}

WHITE_L = 232.0   # 이 이상 밝으면 배경 후보
COLOR_S = 45.0    # 이 이상 채도면 컬러(랜야드·배지·AI 패널)
DARK_L = 200.0    # 확실한 피사체 — 밝은 옷을 감싸 보호하는 울타리
MIN_ISLAND = 4000  # 이보다 작은 전경 섬은 디더링 노이즈로 보고 배경 처리
PROFILE_ROWS = 120


def _background(arr: np.ndarray) -> np.ndarray:
    lum = arr.mean(axis=2)
    sat = arr.max(axis=2) - arr.min(axis=2)
    cand = (lum >= WHITE_L) | (sat >= COLOR_S)

    lab, _ = ndimage.label(cand)
    border = np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])
    bg = np.isin(lab, np.unique(border[border > 0]))
    ai_panel = bg & (sat >= COLOR_S)   # 생성물에 딸려온 AI 컬러 패널 — 통째로 버린다

    # 패널↔흰배경 경계의 반투명 띠는 흰색도 컬러도 아니라 배경에서 빠진다 →
    # 그냥 두면 화면을 가로지르는 가느다란 대각 '전경 실선'으로 남는다. 국소 팽창으로 흡수.
    band = ndimage.binary_dilation(ai_panel, iterations=4) & (sat >= 12) & ~cand
    dropped = ai_panel | band
    bg = ndimage.binary_closing(bg | band, structure=np.ones((7, 7)), border_value=1)

    # 밝은 옷 보호 — 아래 테두리를 막아 '어두운 실루엣에 둘러싸인 밝은 영역'을 hole로 만든다.
    # AI 패널도 울타리에 넣어야 (패널에 접한 흰 셔츠가 새지 않는다) 하고,
    # 넣었으면 반드시 다시 빼야 한다 (안 빼면 패널이 전경으로 되살아난다).
    fence = lum < DARK_L
    fence = np.vstack([fence, np.ones((1, fence.shape[1]), bool)])
    protect = ndimage.binary_fill_holes(fence)[:-1] & ~dropped
    bg &= ~protect

    # 색면 속 깨알 노이즈 섬 흡수
    fl, fn = ndimage.label(~bg)
    if fn:
        sizes = np.bincount(fl.ravel())
        small = np.flatnonzero(sizes < MIN_ISLAND)
        bg |= np.isin(fl, small[small > 0])
    return bg


def run(key: str) -> tuple[Path, dict]:
    arr = np.asarray(Image.open(SPOTS / f"person-{key}1.png").convert("RGB")).astype(np.float32)
    h, w, _ = arr.shape
    lum = arr.mean(axis=2)
    sat = arr.max(axis=2) - arr.min(axis=2)

    bg = _background(arr)
    solid = ~bg

    out = arr.copy()
    brand = np.array([int(BRAND[key][i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)
    tag = solid & (sat >= COLOR_S)          # 랜야드·배지
    if tag.any():
        f = (lum[tag] / max(float(lum[tag].mean()), 1.0))[:, None]
        out[tag] = np.clip(brand[None, :] * f, 0, 255)

    alpha = ndimage.gaussian_filter(solid.astype(np.float32), 0.8)  # 1px 페더
    alpha[solid] = np.maximum(alpha[solid], 1.0)
    rgba = np.dstack([np.clip(out, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)

    dst = SPOTS / f"cut-{key}.png"
    Image.fromarray(rgba, "RGBA").save(dst)

    # ── 실측 좌표 ────────────────────────────────────────────────────────────
    m = alpha > 0.5
    ys, xs = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    y0, y1 = ys[0] / h, (ys[-1] + 1) / h
    band = m[ys[0]:ys[0] + int(0.13 * (ys[-1] - ys[0])) + 1]
    hxs = np.flatnonzero(band.any(axis=0))

    prof = []
    for i in range(PROFILE_ROWS):
        row = m[min(int((i + 0.5) / PROFILE_ROWS * h), h - 1)]
        rx = np.flatnonzero(row)
        prof.append([rx[0] / w, (rx[-1] + 1) / w] if rx.size else None)

    meta = {"bbox": [xs[0] / w, y0, (xs[-1] + 1) / w, y1],
            "head": [hxs[0] / w, hxs[-1] / w],
            "profile": prof}
    (SPOTS / f"cut-{key}.json").write_text(json.dumps(meta), encoding="utf-8")
    return dst, meta


if __name__ == "__main__":
    for k in (sys.argv[1:] or list(BRAND)):
        p, meta = run(k)
        print(f"✓ {p.name}  머리상단 y={meta['bbox'][1]:.3f}  "
              f"머리 x={meta['head'][0]:.3f}~{meta['head'][1]:.3f}  "
              f"bbox={[round(v, 3) for v in meta['bbox']]}")
