"""잡페어 키비주얼 3차 — '잡페어 활기 + 의도' 6컷 (nano-banana-pro, 3:4, 1K).

2차(의도 6컷)는 의도는 읽혔으나 '개인 취업 열망'만 나고 잡페어(여러 기업이 오는 장)의
활기·축제감이 없다는 피드백 → 이번엔 **여러 부스·컬러·배너로 場을 만들고**, 그 안에
'네 자리(빈 의자/빛/경로)'를 심어 활기와 의도를 한 컷에 합친다.

사람 0 / 글자 0 / 로고 0. 잡페어 홀은 원래 사람이 북적이는 장면이라 인물 유출 위험이
크고, 부스·배너·명패는 모델이 글자를 그리려 든다 → 두 금지를 프롬프트에서 반복해 누른다.
팝 원색(비비드 마젠타/블루/그린/오렌지) + 클린 프리미엄 에디토리얼 유지, 파스텔 금지.
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

# 인물 차단: 전시홀은 군중이 기본값이라 2차보다 더 강하게 (개장 전 무인 상태로 못박음)
NEG = ("completely deserted and empty of people, before opening hours, no people at all, "
       "no person, no human, no crowd, no visitors, no staff, no hands, no silhouette of a "
       "person, no mannequin, "
       "no text, no letters, no words, no numbers, no typography, no signage, no printed "
       "graphics on the banners or booth panels, all banners and panels are blank solid "
       "color fabric, no logo, no branding, no watermark, no UI overlay")
BASE = ("photorealistic, full-frame DSLR, sharp focus, clean composition, "
        "bright and airy, premium corporate trade show production quality, "
        "vertical 3:4 poster crop")

CUTS = [
    (
        "잡페어1-부스로우",
        "A bright spacious modern career fair exhibition hall with a high white ceiling and "
        "a pale seamless polished floor, a long row of sleek minimal exhibition booths "
        "receding down a wide clean aisle in one-point perspective, each booth finished in a "
        "different intensely saturated vivid pop color, vivid magenta then electric blue then "
        "vivid green then vivid orange alternating down the row, every booth panel completely "
        "blank with no printing on it, at the far end of the aisle one last booth with a "
        "single empty modern chair standing at its counter, a warm bright shaft of light "
        "falling from above onto exactly that one chair and pooling on the floor around it "
        "while the rest of the hall stays evenly lit and neutral, upscale premium trade show "
        "production, clean editorial architectural photography, deep depth of field",
    ),
    (
        "잡페어2-웰컴아치",
        "A grand modern career fair entrance archway seen straight on and centered, a broad "
        "sculptural gate structure built from bold blocks of intensely saturated vivid pop "
        "color, vivid magenta and electric blue and vivid green and vivid orange interlocking "
        "across the arch, a row of long plain fabric banners in the same vivid colors hanging "
        "down from a truss above the gate, every banner completely blank unprinted solid "
        "color cloth, through the opening of the arch a bright airy white exhibition hall "
        "continues into the distance with soft glowing daylight drawing the eye inward, a "
        "clean pale floor leading straight through the gate, festive but minimal and upscale, "
        "symmetrical composition, clean editorial architectural photography",
    ),
    (
        "잡페어3-배너통로",
        "Looking down a wide bright career fair aisle in dramatic one-point perspective, two "
        "long rows of sleek exhibition booth counters flanking the aisle finished in "
        "intensely saturated vivid pop colors, vivid magenta and electric blue and vivid "
        "green and vivid orange alternating, dozens of long plain fabric banners hanging from "
        "the ceiling truss in the same vivid colors marching backward in repeating rhythm and "
        "vanishing into the bright depth of the hall, every banner and panel completely blank "
        "unprinted solid color cloth, crisp white ceiling and pale seamless floor, bright "
        "clean airy light with a luminous glow at the vanishing point, a sense that the fair "
        "has just opened, clean editorial architectural photography",
    ),
    (
        "잡페어4-상담부스-빈의자",
        "A single modern one-on-one consultation booth at a career fair seen slightly from the "
        "front, a clean minimal counter with a smooth backdrop wall in one intensely "
        "saturated vivid magenta, the backdrop completely blank with no printing, two empty "
        "modern chairs facing each other across the counter with the near chair turned "
        "slightly toward the viewer as if just offered, a small blank white unprinted "
        "nameplate standing on the counter, a soft bright spotlight falling onto the empty "
        "near chair and the blank nameplate so they glow brighter than everything else, "
        "behind and around it other exhibition booths in vivid electric blue and vivid green "
        "and vivid orange rendered soft and out of focus with shallow depth of field, bright "
        "airy hall, premium editorial photography",
    ),
    (
        "잡페어5-랜야드-화이트하나",
        "A close-up editorial still life on a clean white exhibition counter, a dense cluster "
        "of many neck lanyards with blank card holders hanging in tight rows from a minimal "
        "rack, the lanyards in many different intensely saturated vivid pop colors, vivid "
        "magenta and electric blue and vivid green and vivid orange and vivid yellow all "
        "mixed together in an abundant festive mass, every card holder completely empty and "
        "every lanyard strap blank unprinted solid color webbing, one single pure white "
        "lanyard with a blank white card pulled forward toward the camera in sharp crisp "
        "focus and lit by one clean bright directional light, the colorful mass behind it "
        "falling gently out of focus, studio strobe lighting, extremely saturated pop colors, "
        "minimal graphic product photography",
    ),
    (
        "잡페어6-부감플로어",
        "A high overhead top-down aerial view straight down onto a bright career fair "
        "exhibition floor, the booths arranged as a neat grid of clean rectangular blocks "
        "seen from above, each block a flat intensely saturated vivid pop color, vivid "
        "magenta and electric blue and vivid green and vivid orange distributed across the "
        "grid, pale seamless white aisles running between them, every surface blank with no "
        "printing on it, one bold continuous vivid orange path curving and winding through "
        "the white aisles from the bottom edge of the frame and ending precisely at one "
        "single booth, that destination booth lit noticeably brighter than all the others "
        "with a soft glow around it, looks like a clean graphic map of the fair, bright even "
        "daylight, orthographic top down composition, clean editorial photography",
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
