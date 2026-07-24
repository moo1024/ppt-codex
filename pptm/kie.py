"""kie.ai 이미지 생성 래퍼 — 비동기 작업 기반 (createTask → poll → download)."""
from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://api.kie.ai/api/v1"
UPLOAD_URL = "https://api.kie.ai/api/file-base64-upload"
_POLL_INTERVAL = 5   # 초
_MAX_WAIT = 300      # 최대 대기 5분

# 편집 모델별 입력 이미지 파라미터 이름
_IMAGE_PARAM = {
    "google/nano-banana-edit": "image_urls",
    # nano-banana-pro / nano-banana-2 계열은 image_input
}


class KieError(RuntimeError):
    pass


class KieClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.total_tasks: int = 0

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = f"{BASE_URL}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url, data=body, method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise KieError(f"HTTP {e.code}: {e.read().decode()[:200]}") from e

    def _request_url(self, url: str, data: dict) -> dict:
        """BASE_URL 밖의 절대 URL로 POST (업로드 API 등)."""
        body = json.dumps(data).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise KieError(f"HTTP {e.code}: {e.read().decode()[:200]}") from e

    def upload_image(self, path: Path) -> str:
        """로컬 이미지를 kie.ai 임시 저장소에 업로드하고 URL 반환 (3일 유효)."""
        path = Path(path)
        b64 = base64.b64encode(path.read_bytes()).decode()
        resp = self._request_url(UPLOAD_URL, {
            "base64Data": f"data:image/png;base64,{b64}",
            "uploadPath": "pptm/inputs",
            "fileName": path.name,
        })
        if not resp.get("success") or resp.get("code") != 200:
            raise KieError(f"업로드 실패: {resp.get('msg')}")
        return resp["data"]["downloadUrl"]

    def edit_image(
        self,
        *,
        prompt: str,
        image_paths: list[Path],
        out_path: Path,
        model: str = "nano-banana-pro",
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
    ) -> Path:
        """입력 이미지 기반 편집 — 업로드 → createTask → poll → download."""
        urls = [self.upload_image(p) for p in image_paths]
        image_param = _IMAGE_PARAM.get(model, "image_input")

        resp = self._request("POST", "/jobs/createTask", {
            "model": model,
            "input": {
                "prompt": prompt,
                image_param: urls,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": "png",
            },
        })
        if resp.get("code") != 200:
            raise KieError(f"편집 태스크 생성 실패: {resp.get('msg')}")
        task_id = resp["data"]["taskId"]
        self.total_tasks += 1

        result_urls = self._poll(task_id)
        return self._download(result_urls[0], Path(out_path))

    def _create_task(self, model: str, prompt: str, aspect_ratio: str, resolution: str) -> str:
        resp = self._request("POST", "/jobs/createTask", {
            "model": model,
            "input": {
                "prompt": prompt,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "output_format": "png",
            },
        })
        if resp.get("code") != 200:
            raise KieError(f"태스크 생성 실패: {resp.get('msg')}")
        return resp["data"]["taskId"]

    def _poll(self, task_id: str) -> list[str]:
        """완료될 때까지 폴링 후 이미지 URL 목록 반환."""
        deadline = time.monotonic() + _MAX_WAIT
        while time.monotonic() < deadline:
            time.sleep(_POLL_INTERVAL)
            resp = self._request("GET", f"/jobs/recordInfo?taskId={task_id}")
            data = resp.get("data", {})
            state = (data.get("state") or "").lower()
            if state in ("success", "done"):
                result = json.loads(data.get("resultJson") or "{}")
                urls = result.get("resultUrls") or result.get("images") or []
                if not urls:
                    raise KieError("완료됐지만 이미지 URL이 없습니다")
                return urls
            if state in ("failed", "error"):
                raise KieError(f"태스크 실패: {data}")
        raise KieError(f"태스크 타임아웃 ({_MAX_WAIT}초): {task_id}")

    @staticmethod
    def _download(url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "pptm/2"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        return dest

    def generate_images(
        self,
        *,
        prompt: str,
        n: int = 3,
        model: str = "nano-banana-pro",
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
        out_dir: Path,
        base_name: str = "c",
    ) -> list[Path]:
        """n장 생성. 각 장마다 개별 태스크를 병렬 생성한 뒤 순서대로 폴링."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 태스크 n개 생성
        task_ids: list[str] = []
        for _ in range(n):
            tid = self._create_task(model, prompt, aspect_ratio, resolution)
            task_ids.append(tid)
            self.total_tasks += 1

        # 순서대로 폴링 + 다운로드
        paths: list[Path] = []
        for i, tid in enumerate(task_ids, start=1):
            urls = self._poll(tid)
            dest = out_dir / f"{base_name}{i}.png"
            self._download(urls[0], dest)
            paths.append(dest)

        return paths
