from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class KieConfig(BaseModel):
    base_url: str = "https://api.kie.ai/api/v1"
    image_model: str = "nano-banana-pro"
    image_model_fast: str = "google/nano-banana"
    aspect_ratio: str = "16:9"
    resolution: str = "1K"


class QualityProfile(BaseModel):
    model: str
    resolution: str


class Defaults(BaseModel):
    candidates_per_page: int = 3
    profile: str = "standard"


class AppConfig(BaseModel):
    kie: KieConfig = KieConfig()
    quality_profiles: dict[str, QualityProfile] = {}
    defaults: Defaults = Defaults()

    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def profile(self, name: str | None = None) -> QualityProfile:
        key = name or self.defaults.profile
        return self.quality_profiles[key]
