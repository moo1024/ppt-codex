"""잡페어 키비주얼 4차 — '정답 레인' 정제 4컷 (nano-banana-pro, 3:4, 1K).

3차에서 '잡페어4-상담부스-빈의자'만 정답. 나머지는 네온 무지개 5색 나열이라 '유치'해서 탈락.
이번엔 그 정답 톤(실사 리얼리티·클린 에디토리얼·빈 의자 의도)을 유지하되 팔레트를 갈아끼운다:
**딥 주얼 원색 1~2색 + 화이트/차콜/넉넉한 여백.** 형광·네온·파스텔·무지개 나열 금지.
아이덴티티 = 대기업 채용박람회의 격조. 인물 0 / 글자 0 / 로고 0.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pptm.cli import _simple_dotenv, _ROOT  # noqa: E402
from pptm.kie import KieClient  # noqa: E402

OUT = Path("/home/lmh/event-ax/events/2026-지역협업기술센터-잡페어/키비주얼-후보-팝원색")
MODEL = os.environ.get("KV_MODEL", "nano-banana-pro")

# 인물·글자 차단은 3차와 동일 강도 유지 (전시홀은 군중·인쇄물이 기본값이라 반복해 누른다)
NEG = ("completely deserted and empty of people, before opening hours, no people at all, "
       "no person, no human, no crowd, no visitors, no staff, no hands, no silhouette of a "
       "person, no mannequin, "
       "no text, no letters, no words, no numbers, no typography, no signage, no printed "
       "graphics on the banners or booth panels, all banners and panels are blank solid "
       "color fabric, no logo, no branding, no watermark, no UI overlay")

# 팔레트 규율 — '유치함'의 원인(형광·다색 나열)을 정면으로 막는다
PALETTE = ("strictly restrained color palette of white, warm off-white, pale grey and deep "
           "charcoal as the dominant surfaces, with only one or at most two accent colors in "
           "the whole frame, the accents are deep rich jewel-toned primaries with real depth "
           "and slight darkness, absolutely not fluorescent, not neon, not glowing, not "
           "candy-bright, not pastel, no rainbow, no row of many different colors side by "
           "side, at least half the frame is clean empty white space, tasteful and expensive "
           "and grown-up like a flagship corporate recruiting expo for a major conglomerate")
BASE = ("photorealistic, full-frame DSLR, natural realistic photography, sharp focus, "
        "calm balanced composition with generous negative space, soft diffused daylight, "
        "high-end architectural and editorial magazine quality, vertical 3:4 poster crop")

CUTS = [
    (
        "프리미엄1-상담부스로우",
        "A row of one-on-one consultation booths at an upscale corporate career fair, seen "
        "slightly from the front at seated eye level, the booths built from crisp white "
        "panels and deep charcoal frames with clean minimal joinery, in the foreground one "
        "consultation table of pale white stone with a single empty upholstered chair turned "
        "slightly toward the viewer as if just pulled out and offered, a small blank white "
        "unprinted nameplate standing on the table, one soft warm shaft of light falling onto "
        "exactly that empty chair and that blank nameplate so they read brightest in the "
        "frame, the backdrop panel of this front booth is one single deep magenta accent "
        "surface, the further booths behind it recede softly out of focus with only faint "
        "hints of deep cobalt and deep emerald reading as muted blurred color, everything "
        "else white and charcoal and empty air, restrained and premium, shallow depth of "
        "field, clean editorial architectural photography",
    ),
    (
        "프리미엄2-부스통로-끝빛",
        "Looking straight down a very wide bright aisle between two rows of premium career "
        "fair booths in gentle one-point perspective, the booths finished entirely in crisp "
        "white panels with slim deep charcoal frames, tall plain unprinted white fabric "
        "banners hanging quietly from the ceiling truss, the only color in the entire scene "
        "is a single deep cobalt blue accent stripe repeating discreetly on the booth "
        "counters, a pale seamless polished floor with a lot of empty open space in the "
        "foreground, at the far end of the aisle one single empty modern chair standing alone "
        "in a pool of warm light with a soft luminous glow behind it, the rest of the hall "
        "evenly and softly lit, wide calm airy composition, quiet and expensive, deep depth "
        "of field, clean editorial architectural photography",
    ),
    (
        "프리미엄3-웰컴게이트",
        "A refined modern entrance gate to an upscale corporate career fair seen straight on "
        "and centered, a broad clean architectural portal built from crisp white panels with "
        "slim deep charcoal reveals, one single bold deep emerald green accent band running "
        "across the top beam of the gate as the only color in the frame, three or four long "
        "plain unprinted off-white fabric banners hanging still from the truss above, a wide "
        "empty pale floor leading straight through the opening, through the portal a bright "
        "airy white exhibition hall continues into the distance with soft glowing daylight "
        "drawing the eye inward, symmetrical composition with generous white space around the "
        "gate, welcoming and energetic but dignified and minimal, clean editorial "
        "architectural photography",
    ),
    (
        "프리미엄4-랜야드-화이트하나",
        "A close-up editorial still life on a premium career fair counter of pale white stone, "
        "a small curated group of only five or six neck lanyards with blank empty card "
        "holders hanging in a loose row from a slim matte charcoal rail, the straps in a "
        "restrained palette of deep navy and deep cobalt and one deep magenta, every card "
        "holder completely empty and every strap blank unprinted solid webbing, one single "
        "pure white lanyard with a blank white card pulled forward toward the camera in sharp "
        "crisp focus and lit by one clean directional light so it separates from the darker "
        "straps falling gently out of focus behind it, wide clean empty counter space around "
        "the arrangement, soft shadow, calm and expensive, minimal editorial still life "
        "photography, shallow depth of field",
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
        prompt = f"{subject}, {PALETTE}, {BASE}, {NEG}"
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
