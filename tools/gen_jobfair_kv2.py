"""잡페어 키비주얼 2차 — '의도 장치' 6컷 (nano-banana-pro, 3:4, 1K).

1차 6컷은 예뻤지만 메시지가 안 읽힌다는 피드백 → 이번엔 의도를 물체·빛·구도로 넣는다.
사람 0 / 글자 0 / 로고 0. 팝 원색 + 화이트 클린 에디토리얼 + 빈 의자·빈 사원증.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pptm.cli import _simple_dotenv, _ROOT  # noqa: E402
from pptm.kie import KieClient  # noqa: E402

OUT = Path("/home/lmh/event-ax/events/2026-지역협업기술센터-잡페어/키비주얼-후보-팝원색")
MODEL = os.environ.get("KV_MODEL", "nano-banana-pro")  # kie 등록명 (google/ 접두어 없음)

# 인물·글자·로고 완전 차단 (kie가 hex나 라벨을 그려버린 실사고 있음 → 강하게 반복)
NEG = ("absolutely no people, no person, no human, no hands, no silhouette of a person, "
       "no text, no letters, no words, no numbers, no typography, no signage, "
       "no logo, no branding, no watermark, no UI overlay")
BASE = ("photorealistic, full-frame DSLR, sharp focus, clean composition, "
        "vertical 3:4 poster crop")

CUTS = [
    (
        "의도1-스포트라이트-마젠타",
        "A dark premium corporate office interior at night, deep charcoal and near-black "
        "shadows filling most of the frame, one single empty modern ergonomic office chair "
        "standing alone beside a minimal desk, a dramatic vivid magenta spotlight beam "
        "pouring straight down from above and illuminating only that chair, a visible "
        "volumetric shaft of magenta light in the air, a sharp circular pool of magenta "
        "light on the polished floor around the chair, everything else swallowed by shadow, "
        "a blank white employee ID card on a lanyard lying on the desk also catching the "
        "magenta light, theatrical high-contrast stage lighting, intensely saturated vivid "
        "magenta as the only color in the scene, cinematic",
    ),
    (
        "의도2-보드룸-일렉트릭블루",
        "A long modern corporate boardroom seen in symmetrical one-point perspective down a "
        "long polished dark conference table, a row of identical empty premium executive "
        "chairs neatly tucked in along both sides, one single chair near the middle pulled "
        "slightly out from the table and turned a few degrees toward the viewer, that one "
        "chair lit by intense vivid electric blue light with an electric blue glow pooling "
        "on the floor and reflecting on the table beside it, every other chair left neutral "
        "desaturated cool grey with no color at all, clean minimal architecture, floor to "
        "ceiling windows with soft overcast daylight, editorial architectural photography",
    ),
    (
        "의도3-열린유리문-그린",
        "A sleek frameless frosted glass office door standing slightly ajar in a clean "
        "bright white minimal corridor, intense vivid green light spilling out through the "
        "narrow gap and casting a sharp hard-edged green wedge of light across the pale "
        "seamless floor, through the opening a partial glimpse of one empty premium modern "
        "office chair waiting inside the green-lit room, the corridor itself bright white "
        "and completely neutral with generous negative space, a feeling of invitation to "
        "step through, clean editorial architectural photography, saturated pop green",
    ),
    (
        "의도4-시티뷰-핫핑크노을",
        "A high-floor executive corner office with floor-to-ceiling glass windows, one empty "
        "premium leather executive chair alone in the room turned away from the viewer to "
        "face the window, far below through the glass a vast city skyline of skyscrapers "
        "seen from very high up, the sunset sky filling the window in a bold saturated pop "
        "gradient from hot pink through magenta into electric orange, the empty chair "
        "backlit and rim-lit by that vivid pink light, minimal bare polished floor, immense "
        "sense of altitude and aspiration, cinematic wide vertical framing",
    ),
    (
        "의도5-사원증매크로-원색색면",
        "Extreme close-up macro still life of a completely blank pure white plastic employee "
        "ID card attached to a woven neck lanyard, the card face totally empty and unprinted, "
        "lying flat on a bold graphic color-block surface split diagonally between vivid "
        "electric blue and vivid magenta, one clean hard streak of white light sweeping "
        "across the glossy blank card, crisp directional shadow, extremely saturated pop "
        "primary colors, minimal graphic editorial product photography, studio strobe light",
    ),
    (
        "의도6-바닥라인-오렌지",
        "A vast minimal white gallery-like empty room with a seamless pale floor and bare "
        "white walls, one bold thick vivid orange painted line running across the floor from "
        "the bottom foreground straight into the depth of the room, the line tapering into a "
        "clean arrowhead shape that points at and stops exactly at one single empty modern "
        "premium office chair, the chair standing alone in the huge white negative space, "
        "soft even daylight, no other objects in the room, clean editorial architectural "
        "photography, saturated pop orange as the only color",
    ),
]


def main() -> int:
    _simple_dotenv(_ROOT / ".env")
    key = os.environ.get("KIE_API_KEY", "")
    if not key:
        print("KIE_API_KEY 없음 (.env 확인)", file=sys.stderr)
        return 2
    kie = KieClient(api_key=key)
    OUT.mkdir(parents=True, exist_ok=True)

    only = sys.argv[1:]
    cuts = [c for c in CUTS if not only or c[0] in only]

    tasks = []
    for name, subject in cuts:
        prompt = f"{subject}, {BASE}, {NEG}"
        tid = kie._create_task(MODEL, prompt, "3:4", "1K")
        print(f"→ 태스크 생성 {name}: {tid}", flush=True)
        tasks.append((name, tid))

    fails = 0
    for name, tid in tasks:
        try:
            urls = kie._poll(tid)
            dest = OUT / f"{name}.png"
            kie._download(urls[0], dest)
            print(f"✓ {dest.name}  ({dest.stat().st_size // 1024} KB)", flush=True)
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"✗ {name}: {exc}", file=sys.stderr, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
