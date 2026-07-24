"""pptm spot — v7 스팟 이미지 생성 (deck_plan 없이 프롬프트만으로)."""
from __future__ import annotations

from pathlib import Path

import pytest

from pptm.spot import build_prompt, run_spot


class FakeKie:
    """generate_images 호출 인자를 기록하는 스텁."""

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.total_tasks = 0

    def generate_images(self, **kw):
        self.calls.append(kw)
        out_dir = Path(kw["out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for i in range(1, kw.get("n", 1) + 1):
            p = out_dir / f"{kw.get('base_name', 'c')}{i}.png"
            p.write_bytes(b"\x89PNG fake")
            paths.append(p)
        self.total_tasks += kw.get("n", 1)
        return paths


# ── 프롬프트 조립 ──────────────────────────────────────────────────────────

def test_배경색을_프롬프트에_주입한다():
    """CLAUDE.md 규칙: 슬라이드 배경색을 명시하지 않으면 붙였을 때 티가 난다."""
    p = build_prompt("single ceramic cup", bg="F7F5F1")
    assert "#F7F5F1" in p
    assert "single ceramic cup" in p


def test_배경색_해시가_있어도_중복되지_않는다():
    p = build_prompt("cup", bg="#F7F5F1")
    assert p.count("#F7F5F1") == 1
    assert "##" not in p


def test_다크는_다크_배경_문구를_쓴다():
    p = build_prompt("cup", bg="0A0A0A", dark=True)
    assert "#0A0A0A" in p
    assert "dark" in p.lower()


def test_풀블리드는_시네마틱_문법을_붙인다():
    """시네마틱 트랙: 텍스트 앉힐 영역을 어둡게 주문해야 한다."""
    p = build_prompt("a brewery at dawn", fullbleed=True)
    low = p.lower()
    assert "cinematic" in low
    assert "near black" in low


def test_풀블리드는_배경색_문구를_넣지_않는다():
    """풀블리드는 화면을 꽉 채우므로 배경 매칭이 필요 없다."""
    p = build_prompt("a brewery", bg="F7F5F1", fullbleed=True)
    assert "F7F5F1" not in p


# ── 실행 ───────────────────────────────────────────────────────────────────

def test_스팟은_assets_spots에_저장된다(tmp_path):
    kie = FakeKie()
    out = run_spot(tmp_path, kie=kie, prompt="cup", bg="F7F5F1", name="cup")
    assert out[0].parent == tmp_path / "assets" / "spots"
    assert out[0].name == "cup1.png"
    assert out[0].exists()


def test_풀블리드는_16대9로_요청한다(tmp_path):
    kie = FakeKie()
    run_spot(tmp_path, kie=kie, prompt="brewery", fullbleed=True)
    assert kie.calls[0]["aspect_ratio"] == "16:9"


def test_세로_포스터는_aspect를_전달한다(tmp_path):
    """3:4 세로 키비주얼 등 — 16:9 밖의 비율도 요청할 수 있어야 한다."""
    kie = FakeKie()
    run_spot(tmp_path, kie=kie, prompt="empty office chair at dawn",
             fullbleed=True, aspect="3:4")
    assert kie.calls[0]["aspect_ratio"] == "3:4"


def test_n장_생성을_전달한다(tmp_path):
    kie = FakeKie()
    out = run_spot(tmp_path, kie=kie, prompt="cup", n=3)
    assert len(out) == 3
    assert kie.calls[0]["n"] == 3


def test_이름을_안_주면_spot을_쓴다(tmp_path):
    kie = FakeKie()
    out = run_spot(tmp_path, kie=kie, prompt="cup")
    assert out[0].name.startswith("spot")


def test_기존_파일을_덮어쓰지_않는다(tmp_path):
    """크레딧이 드는 작업이라 실수로 날리면 안 된다."""
    spots = tmp_path / "assets" / "spots"
    spots.mkdir(parents=True)
    (spots / "cup1.png").write_bytes(b"OLD")

    kie = FakeKie()
    with pytest.raises(FileExistsError, match="cup1.png"):
        run_spot(tmp_path, kie=kie, prompt="cup", name="cup")

    assert (spots / "cup1.png").read_bytes() == b"OLD"
    assert kie.calls == []


def test_force면_덮어쓴다(tmp_path):
    spots = tmp_path / "assets" / "spots"
    spots.mkdir(parents=True)
    (spots / "cup1.png").write_bytes(b"OLD")

    kie = FakeKie()
    run_spot(tmp_path, kie=kie, prompt="cup", name="cup", force=True)
    assert (spots / "cup1.png").read_bytes() != b"OLD"


# ── 프롬프트 안전장치 (2026-07-21 실제 생성물에서 발견) ────────────────────

class TestNoTextLeak:
    """배경색 hex가 이미지에 글자로 박히는 사고 — credtest1.png에 '1B1B15'가 렌더됨."""

    def test_모든_프롬프트가_글자_금지를_명시한다(self):
        for kw in ({}, {"dark": True}, {"fullbleed": True}):
            p = build_prompt("a jar", **kw).lower()
            assert "no text" in p
            assert "no letters" in p
            assert "no numbers" in p

    def test_색코드를_그리지_말라고_명시한다(self):
        """hex를 프롬프트에 넣는 이상 이 금지가 반드시 붙어야 한다."""
        p = build_prompt("a jar", bg="1B1B15").lower()
        assert "1b1b15" in p.replace("#", "")
        assert "color code" in p


class TestDarkSide:
    """풀블리드 커버는 글자 앉힐 면을 지정할 수 있어야 한다 (mukgold는 좌 텍스트)."""

    def test_기본은_우측이_어둡다(self):
        assert "right" in build_prompt("x", fullbleed=True).lower()

    def test_좌측을_지정할_수_있다(self):
        p = build_prompt("x", fullbleed=True, dark_side="left").lower()
        assert "left" in p
        assert "right third fades" not in p

    def test_하단을_지정할_수_있다(self):
        p = build_prompt("x", fullbleed=True, dark_side="bottom").lower()
        assert "bottom" in p

    def test_none이면_어두운_면_주문을_넣지_않는다(self):
        p = build_prompt("x", fullbleed=True, dark_side="none").lower()
        assert "fades to near black" not in p
        assert "cinematic" in p

    def test_잘못된_값은_거부한다(self):
        with pytest.raises(ValueError, match="dark_side"):
            build_prompt("x", fullbleed=True, dark_side="diagonal")
