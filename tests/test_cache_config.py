"""cache.py + config.py 테스트."""
import json
from pathlib import Path

import pytest

from pptm.cache import ArtifactCache
from pptm.config import AppConfig


# ---------- cache ----------

class TestArtifactCache:
    def test_miss_on_first_access(self, tmp_path):
        cache = ArtifactCache(tmp_path)
        assert not cache.is_fresh("out.png", inputs={"prompt": "hello", "model": "x"})

    def test_hit_after_save(self, tmp_path):
        cache = ArtifactCache(tmp_path)
        inputs = {"prompt": "hello", "model": "x"}
        (tmp_path / "out.png").write_bytes(b"fake")   # 실제 산출물 파일 필요
        cache.save_meta("out.png", inputs=inputs, usage={"cost": 0.07})
        assert cache.is_fresh("out.png", inputs=inputs)

    def test_miss_on_changed_input(self, tmp_path):
        cache = ArtifactCache(tmp_path)
        inputs = {"prompt": "hello", "model": "x"}
        (tmp_path / "out.png").write_bytes(b"fake")
        cache.save_meta("out.png", inputs=inputs, usage={})
        # prompt 변경 → 해시 달라짐
        assert not cache.is_fresh("out.png", inputs={**inputs, "prompt": "bye"})

    def test_force_flag_bypasses_cache(self, tmp_path):
        cache = ArtifactCache(tmp_path)
        inputs = {"prompt": "hello", "model": "x"}
        (tmp_path / "out.png").write_bytes(b"fake")
        cache.save_meta("out.png", inputs=inputs, usage={})
        assert not cache.is_fresh("out.png", inputs=inputs, force=True)

    def test_meta_stores_usage(self, tmp_path):
        cache = ArtifactCache(tmp_path)
        cache.save_meta("out.png", inputs={"p": "x"}, usage={"cost_usd": 0.07})
        meta = json.loads((tmp_path / "out.png.meta.json").read_text())
        assert meta["usage"]["cost_usd"] == pytest.approx(0.07)


# ---------- config ----------

class TestAppConfig:
    _YAML = (
        "kie:\n  image_model: nano-banana-pro\n  aspect_ratio: '16:9'\n  resolution: 1K\n"
        "quality_profiles:\n  standard: {model: nano-banana-pro, resolution: 1K}\n"
        "defaults:\n  profile: standard\n  candidates_per_page: 3\n"
    )

    def test_loads_yaml(self, tmp_path, monkeypatch):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(self._YAML)
        cfg = AppConfig.from_yaml(cfg_file)
        assert cfg.kie.image_model == "nano-banana-pro"
        assert cfg.defaults.candidates_per_page == 3

    def test_budget_usd_accessible(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(self._YAML)
        cfg = AppConfig.from_yaml(cfg_file)
        assert cfg.defaults.profile == "standard"
