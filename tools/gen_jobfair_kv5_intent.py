"""잡페어 '의도형' 키비주얼 5차 — kie 고급 재렌더 6컷 (nano-banana-pro, 3:4, 2K).

브리프: 키비주얼-캠페인/브리프-의도형-kie고급재렌더.md
컨셉·구도는 Codex(pumasi) 원본에서 확정됐고, 문제는 **싸구려·AI·스톡 티**뿐이다.
원본은 매끈한 CG 렌더 느낌(플라스틱 가죽 / 무결점 바닥 / 데칼처럼 얹힌 페인트)이라
이번엔 그걸 정면으로 눌러 **실제 광고 사진**으로 끌어올린다:
  ① 미디엄포맷 실사 문법 ② 진짜 재질(풀그레인 가죽·미장 콘크리트) ③ 바닥에 '칠해진' 페인트
  ④ 자연 그림자·미세 결함 ⑤ NOT 3D/CGI 명시.
공통: 사람 0 / 글자 0 / 로고 0, 상단 여백 넓게(카피 자리), 원색 1색.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pptm.cli import _simple_dotenv, _ROOT  # noqa: E402
from pptm.kie import KieClient  # noqa: E402

OUT = Path("/home/lmh/event-ax/events/2026-지역협업기술센터-잡페어"
           "/키비주얼-캠페인/의도-kie고급")
MODEL = os.environ.get("KV_MODEL", "nano-banana-pro")

# ── 극사실 코어: '3D 렌더 티'를 이름으로 지목해 막는 게 핵심 ──────────────
REAL = ("this is a real advertising photograph captured on a Phase One medium format "
        "camera with an 80mm lens at f/8, true-to-life materials and physically accurate "
        "light, the black leather is genuine full-grain hide with visible natural pores, "
        "fine grain, soft creases and a low satin sheen rather than a glossy plastic "
        "surface, the floor is real power-trowelled pale grey concrete with authentic "
        "faint swirl marks, fine aggregate speckle, subtle patina, hairline scuffs and "
        "slightly uneven tone, the painted marking is real matte floor paint physically "
        "applied onto that concrete so the concrete texture reads faintly through it and "
        "its edges are crisp but very slightly imperfect, natural soft directional "
        "daylight with realistic soft-edged contact shadows under every wheel and foot, "
        "subtle real-world imperfections, fine natural photographic grain")

NEG = ("absolutely not a 3D render, not CGI, not a computer graphic, no ray-traced "
       "look, no video-game look, no plastic or rubbery surfaces, no waxy sheen, no "
       "mirror-perfect flawless floor, no floating objects, no fake decal sticker look, "
       "no cheap stock-photo cliche, no oversharpening, no HDR halo, no heavy vignette, "
       "no lens flare, "
       "no people, no person, no human, no hands, no silhouette, no mannequin, "
       "no text, no letters, no words, no numbers, no typography, no signage, no logo, "
       "no branding, no watermark, no UI overlay")

# 카피 자리 — 상단 1/3은 반드시 비운다
COMPOSE = ("vertical 3:4 portrait framing, the entire upper third of the frame is a "
           "clean empty pale wall with nothing in it, deliberately reserved as quiet "
           "negative space for a headline, the chair sits low in the lower-middle of the "
           "frame, extreme minimalism, calm symmetrical editorial composition, at least "
           "half the frame is clean empty space, restrained and expensive")

CHAIR = ("one single empty premium black full-grain leather executive chair with a "
         "polished aluminium five-star base and castors, no one sitting in it")

CUTS = [
    (
        "1-화살표정면",
        f"{CHAIR}, standing in the mid-ground of a large bright empty white studio room "
        "and facing the viewer straight on. A single bold vivid orange directional arrow "
        "is painted flat onto the smooth pale concrete floor, running from the very "
        "bottom edge of the frame away into the room in one-point perspective and ending "
        "in a clean arrowhead that points exactly at the chair. The orange is one strong "
        "saturated accent and the only colour in the whole scene",
    ),
    (
        "2-원형타겟",
        f"{CHAIR}, standing exactly at the centre of a bold vivid orange target ring "
        "painted flat onto the smooth pale concrete floor of a large bright empty white "
        "studio room, the ring a clean wide band of matte orange paint seen in "
        "perspective as a soft ellipse around the chair, the chair facing the viewer "
        "straight on. The orange is one strong saturated accent and the only colour in "
        "the whole scene",
    ),
    (
        "3-스포트라이트",
        f"{CHAIR}, turned very slightly to one side and standing on a completely plain "
        "smooth pale concrete floor with no markings or paint of any kind, in a calm "
        "bright white room whose back wall is one single continuous flat white surface "
        "with no horizontal band, no dado line, no skirting and no colour change "
        "anywhere on it, lit by one single dramatic overhead theatre spotlight that "
        "carves a clean bright circular pool of light on the bare floor around only the "
        "chair, a faint volumetric cone of light hanging in the air above it, the "
        "surrounding room staying bright and airy in soft warm white rather than going "
        "grey or dark. Palette of bright white and black only, no colour accent",
    ),
    (
        "4-레드카펫로프",
        f"{CHAIR}, facing the viewer straight on and standing in the middle of a wide "
        "deep crimson red carpet runner that starts at the very bottom edge of the frame "
        "and runs away from the camera in one-point perspective all the way past the "
        "chair, the runner wide enough that both of the two polished chrome stanchion "
        "posts in the foreground stand with their heavy round bases fully on the red "
        "carpet, one thick crimson velvet rope swagging gently between the two posts in "
        "front of the chair and hanging clearly below the seat so it never overlaps the "
        "chair legs, the rest of the bright empty white room a smooth pale concrete "
        "floor. Real dense woven carpet pile and real crushed velvet nap with visible "
        "fibres, a rich saturated true red, the only colour in the scene, a reserved seat",
    ),
    (
        "5-컬러게이트",
        "A bold vivid magenta rectangular portal frame stands in a large bright empty "
        "white room with a smooth pale concrete floor, a clean thick freestanding "
        f"doorway of solid matte magenta-painted panel, and just beyond the opening "
        f"{CHAIR} stands facing the viewer, perfectly framed and centred inside the "
        "portal, the floor continuing through the opening. The magenta is one strong "
        "saturated accent and the only colour in the whole scene",
    ),
    (
        "6-발자국트레일",
        "A trail of bold vivid green painted footprints, left and right shoe soles "
        "alternating, marches across the smooth pale concrete floor of a large bright "
        "empty white room from the bottom edge of the frame into the mid-ground and stops "
        f"right in front of {CHAIR}, which faces the viewer straight on. The footprints "
        "are a thin flat layer of matte green floor paint lying almost level with the "
        "concrete, absolutely not thick impasto oil paint and not glossy raised blobs of "
        "pigment, each print crisply shaped with very slightly ragged real paint edges. "
        "The green is one strong saturated accent and "
        "the only colour in the whole scene",
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
        prompt = f"{subject}. {REAL}. {COMPOSE}. {NEG}"
        tid = kie._create_task(MODEL, prompt, "3:4", "2K")
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
