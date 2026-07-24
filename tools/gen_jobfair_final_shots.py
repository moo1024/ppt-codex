"""잡페어 완성 포스터 5종 — 우측 인물컷만 kie로 생성 (nano-banana-pro, 3:4, 2K).

브리프: 키비주얼-캠페인/브리프-완성포스터-ppt디테일.md

**대각 컬러 패널은 여기서 만들지 않는다.** 초기엔 이미지 안에 같이 주문했는데 5종 중
① 패널이 인물 위에 반투명으로 덮이거나 ② 경계가 디더링으로 지저분하거나 ③ 각도가
매번 달라 5종이 시리즈로 안 붙었다. 그래서 패널은 layout_spec의 네이티브 poly로 빼고
(5종 완전 동일), kie는 **순백 배경 위 인물 한 사람**만 뽑는다 — 지시가 단순해질수록
프레이밍 준수율이 올라간다. 누끼는 tools/prep_jobfair_plate.py 가 딴다.

색은 랜야드·배지에만. 배경엔 그림자조차 없어야 누끼가 깨끗하다.

사용:  python3 tools/gen_jobfair_final_shots.py [키 ...]   (기본 5종 전부)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pptm.cli import _load_kie, _simple_dotenv, _ROOT  # noqa: E402
from pptm.spot import run_spot  # noqa: E402

PROJ = _ROOT / "projects" / "knu-jobfair-final"

# 배치는 전부 내가 한다 — kie엔 '머리 위 여백 확보 + 하단 잘림'만 요구한다.
# (좌우 여백을 넉넉히 둬야 누끼 후 확대 배치할 때 팔·어깨가 안 잘린다)
FRAME = (
    "the figure sits in the middle of the frame with a generous empty margin of plain "
    "white on both the left and the right so nothing is cut off at the sides, "
    "the top of the head sits about one fifth of the way down from the top edge, "
    "leaving clear empty headroom above the head, "
    "the body is cropped by the bottom edge of the frame"
)

LOOK = (
    "clean bright commercial studio photography, seamless plain pure white background "
    "with absolutely nothing on it, no coloured panel, no shape, no graphic, no "
    "gradient, no cast shadow on the backdrop, soft even key light, sharp focus, "
    "natural skin texture, true photographic look, no props, no desk, no plants"
)

NEG = (
    "not a 3D render, not CGI, not an illustration, no cartoon, no plastic skin, "
    "no heavy retouching, no vignette, no lens flare, no colour cast on the skin, "
    "no printing or pattern or emblem on the lanyard or the badge, "
    "no logo, no brand mark, no symbol, no icon, no id photo on the badge, "
    "no second person, no crowd"
)


def build(color: str, gender: str, outfit: str, hair: str) -> str:
    return (
        f"a black and white monochrome studio portrait photograph of a friendly Korean "
        f"{gender} professional in their late twenties, seated on a modern mesh office "
        f"chair, upper body three quarter view turned slightly toward the camera, calm "
        f"confident closed lip smile, looking straight at the camera, {hair}, wearing "
        f"{outfit}, the skin hair clothing chair and background are entirely desaturated "
        f"greyscale with no colour at all, "
        f"the one and only colour anywhere in the picture is {color}, and it appears in "
        f"exactly two places: the plain unprinted {color} lanyard strap around the neck, "
        f"and the small plain blank {color} badge holder hanging from it, "
        f"{FRAME}, {LOOK}, {NEG}"
    )


SHOTS = {
    # key: (색 표현, 성별, 상의, 헤어)
    "naver": ("vivid bright grass green",
              "male", "a plain dark charcoal crew neck knit sweater",
              "short neat black hair"),
    "hyundai": ("deep navy blue",
                "male", "a crisp light grey button up shirt with the collar open",
                "short tidy side parted black hair"),
    "skhynix": ("vivid bright orange",
                "male", "a plain dark navy oxford shirt with the sleeves rolled up",
                "short cropped black hair"),
    "samsung": ("vivid royal blue",
                "female", "a soft mid grey knit top",
                "shoulder length straight dark hair"),
    "kepco": ("rich violet purple",
              "male", "a dark charcoal blazer over a plain shirt",
              "short neat black hair with a clean side part"),
}


def main(keys: list[str]) -> int:
    _simple_dotenv(_ROOT / ".env")
    kie = _load_kie()
    for key in keys:
        color, gender, outfit, hair = SHOTS[key]
        paths = run_spot(
            PROJ, kie=kie, prompt=build(color, gender, outfit, hair), bg="FFFFFF",
            n=1, name=f"person-{key}", model="nano-banana-pro",
            aspect="3:4", resolution="2K", force=True,
        )
        for p in paths:
            print(f"✓ {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or list(SHOTS)))
