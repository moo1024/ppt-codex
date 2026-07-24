"""스팟 이미지 생성 — v7 트랙 (kie.ai).

v6의 candidates.py는 deck_plan.json 기반이라 v7에서 쓸 수 없었다.
이 모듈은 프롬프트 하나만으로 `assets/spots/`에 이미지를 떨어뜨린다.

프롬프트 규칙은 docs/SPEC.md "스팟 이미지" 절 참조 — 핵심은
**슬라이드 배경색을 반드시 명시**해야 붙였을 때 티가 안 난다는 것.
"""
from __future__ import annotations

from pathlib import Path

# 프롬프트에 hex를 넣으면 모델이 그 코드를 이미지에 글자로 그려버린다
# (2026-07-21 실사고: '#1B1B15'가 하단에 렌더됨). 색 지정은 유지하되 강하게 막는다.
_NO_TEXT = "no text, no letters, no numbers, no color codes, no labels, no watermark"

# 스팟: 슬라이드에 얹을 낱개 오브젝트 — 배경이 슬라이드와 같아야 한다
_SPOT_TAIL = "on solid {bg} background, soft studio light, " + _NO_TEXT
_SPOT_TAIL_DARK = "on solid {bg} dark background, dramatic rim light, " + _NO_TEXT

# 풀블리드: 화면을 꽉 채우는 주인공 이미지
_FULLBLEED_BASE = ("cinematic, volumetric light, film grain, high contrast, "
                   "shallow depth of field")

# 글자를 앉힐 면을 어둡게 주문한다 (docs/SPEC.md 시네마틱 풀블리드 트랙)
_DARK_SIDES = {
    "right": "the right third fades to near black for text overlay",
    "left": "the left third fades to near black for text overlay",
    "top": "the top third fades to near black for text overlay",
    "bottom": "the bottom third fades to near black for text overlay",
    "none": "",
}


def build_prompt(
    subject: str,
    *,
    bg: str = "F7F5F1",
    dark: bool = False,
    fullbleed: bool = False,
    dark_side: str = "right",
) -> str:
    """주제 + 배경색 → kie 프롬프트.

    fullbleed면 배경 매칭이 필요 없으므로 배경색을 넣지 않고
    시네마틱 문법을 붙인다 (docs/SPEC.md 시네마틱 풀블리드 트랙).
    dark_side는 글자를 앉힐 면 — 좌측 정렬 커버면 "left".
    """
    subject = subject.strip().rstrip(",")
    if fullbleed:
        if dark_side not in _DARK_SIDES:
            raise ValueError(
                f"dark_side는 {list(_DARK_SIDES)} 중 하나여야 합니다: {dark_side!r}")
        parts = [subject, _FULLBLEED_BASE, _DARK_SIDES[dark_side], _NO_TEXT]
        return ", ".join(p for p in parts if p)

    hex_bg = "#" + bg.lstrip("#").upper()
    tail = (_SPOT_TAIL_DARK if dark else _SPOT_TAIL).format(bg=hex_bg)
    return f"{subject}, {tail}"


def run_spot(
    project_dir: Path,
    *,
    kie,
    prompt: str,
    bg: str = "F7F5F1",
    dark: bool = False,
    fullbleed: bool = False,
    dark_side: str = "right",
    n: int = 1,
    name: str = "spot",
    model: str = "google/nano-banana",
    aspect: str = "16:9",
    resolution: str = "1K",
    force: bool = False,
) -> list[Path]:
    """스팟 이미지를 생성해 `<project>/assets/spots/` 에 저장한다.

    크레딧이 드는 작업이라 기존 파일이 있으면 기본적으로 거부한다 (force로 해제).
    """
    out_dir = Path(project_dir) / "assets" / "spots"

    if not force:
        for i in range(1, n + 1):
            existing = out_dir / f"{name}{i}.png"
            if existing.exists():
                raise FileExistsError(
                    f"{existing.name} 이미 있음 — 다른 --name 을 쓰거나 --force 로 덮어쓰세요: {existing}"
                )

    return kie.generate_images(
        prompt=build_prompt(prompt, bg=bg, dark=dark, fullbleed=fullbleed,
                            dark_side=dark_side),
        n=n,
        model=model,
        aspect_ratio=aspect,
        resolution=resolution,
        out_dir=out_dir,
        base_name=name,
    )
