"""정렬 검수기(tools/check_align.py) — 4대 오류 클래스를 실제로 잡는지."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_align", Path(__file__).resolve().parent.parent / "tools" / "check_align.py")
check_align = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_align)
check_page = check_align.check_page


def _codes(warns):
    return {w.split("]")[0].lstrip("[") for w in warns}


def test_clean_page_has_no_warnings():
    items = [
        {"type": "card", "x": 0.05, "y": 0.3, "w": 0.4, "h": 0.495},
        {"type": "card", "x": 0.55, "y": 0.3, "w": 0.4, "h": 0.495},
        {"type": "band", "x": 0.05, "y": 0.845, "w": 0.9, "h": 0.06, "text": "요약"},
    ]
    assert check_page(items) == []


def test_A_card_row_bottom_mismatch():
    items = [
        {"type": "card", "x": 0.05, "y": 0.3, "w": 0.4, "h": 0.45},
        {"type": "card", "x": 0.55, "y": 0.3, "w": 0.4, "h": 0.40},  # h 다름
    ]
    assert "A" in _codes(check_page(items))


def test_B_num_xl_hairline_overlap():
    items = [
        {"type": "text", "style": "num_xl", "text": "23분", "x": 0.08, "y": 0.40, "w": 0.2},
        {"type": "hairline", "x": 0.08, "y": 0.42, "w": 0.22},  # 숫자 밑 0.02 → 겹침
    ]
    assert "B" in _codes(check_page(items))


def test_C_row_y_micro_mismatch():
    items = [
        {"type": "text", "style": "caption", "text": "왼", "x": 0.08, "y": 0.34, "w": 0.2},
        {"type": "text", "style": "caption", "text": "오", "x": 0.65, "y": 0.346, "w": 0.2},  # 0.006 어긋
    ]
    assert "C" in _codes(check_page(items))


def test_C_ignores_optical_offset_under_threshold():
    items = [
        {"type": "text", "style": "caption", "text": "왼", "x": 0.08, "y": 0.34, "w": 0.2},
        {"type": "text", "style": "caption", "text": "오", "x": 0.65, "y": 0.343, "w": 0.2},  # 0.003 광학
    ]
    assert "C" not in _codes(check_page(items))


def test_D_dead_bottom_gap():
    items = [
        {"type": "card", "x": 0.05, "y": 0.3, "w": 0.9, "h": 0.35},  # 바닥 0.65
        {"type": "band", "x": 0.05, "y": 0.845, "w": 0.9, "h": 0.06, "text": "요약"},
    ]
    assert "D" in _codes(check_page(items))
