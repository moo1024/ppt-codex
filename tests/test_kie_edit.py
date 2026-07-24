"""KieClient 업로드 + 이미지 편집 테스트 — HTTP 완전 모킹."""
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pptm.kie import KieClient, KieError


def _resp(payload: dict) -> MagicMock:
    m = MagicMock()
    m.read.return_value = json.dumps(payload).encode()
    m.__enter__ = lambda s: s
    m.__exit__ = MagicMock(return_value=False)
    return m


class TestUploadImage:
    def test_returns_download_url(self, tmp_path):
        png = tmp_path / "winner.png"
        png.write_bytes(b"\x89PNG fake")

        kie = KieClient(api_key="test-key")
        upload_resp = _resp({
            "success": True, "code": 200,
            "data": {"downloadUrl": "https://tempfile.example/winner.png"},
        })

        with patch("pptm.kie.urllib.request.urlopen", return_value=upload_resp) as mock_open:
            url = kie.upload_image(png)

        assert url == "https://tempfile.example/winner.png"
        # 요청 바디에 base64Data 포함 확인
        req = mock_open.call_args[0][0]
        body = json.loads(req.data.decode())
        assert "base64Data" in body
        assert body["base64Data"].startswith("data:image/png;base64,")

    def test_raises_on_failure(self, tmp_path):
        png = tmp_path / "x.png"
        png.write_bytes(b"\x89PNG")
        kie = KieClient(api_key="k")
        fail = _resp({"success": False, "code": 500, "msg": "quota"})
        with patch("pptm.kie.urllib.request.urlopen", return_value=fail):
            with pytest.raises(KieError):
                kie.upload_image(png)


class TestEditImage:
    def test_edit_flow(self, tmp_path):
        """upload → createTask(image_input 포함) → poll → download."""
        src = tmp_path / "winner.png"
        src.write_bytes(b"\x89PNG fake")
        out = tmp_path / "background.png"

        kie = KieClient(api_key="test-key")

        responses = [
            # 1. upload
            _resp({"success": True, "code": 200,
                   "data": {"downloadUrl": "https://tmp.example/w.png"}}),
            # 2. createTask
            _resp({"code": 200, "data": {"taskId": "t-123"}}),
            # 3. poll → success
            _resp({"code": 200, "data": {
                "state": "success",
                "resultJson": json.dumps({"resultUrls": ["https://tmp.example/result.png"]}),
            }}),
            # 4. download
            _resp({}),  # download는 read()가 bytes를 반환해야 함
        ]
        responses[3].read.return_value = b"\x89PNG edited"

        with patch("pptm.kie.urllib.request.urlopen", side_effect=responses), \
             patch("pptm.kie.time.sleep"):
            result = kie.edit_image(
                prompt="Remove all text",
                image_paths=[src],
                out_path=out,
                model="nano-banana-pro",
            )

        assert result == out
        assert out.read_bytes() == b"\x89PNG edited"

    def test_edit_uses_image_input_for_pro(self, tmp_path):
        """nano-banana-pro 계열은 image_input 파라미터를 써야 함."""
        src = tmp_path / "w.png"
        src.write_bytes(b"\x89PNG")
        out = tmp_path / "o.png"
        kie = KieClient(api_key="k")

        captured_bodies = []

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode()) if req.data else {}
            captured_bodies.append((req.full_url, body))
            if "file-base64-upload" in req.full_url:
                return _resp({"success": True, "code": 200,
                              "data": {"downloadUrl": "https://t/w.png"}})
            if "createTask" in req.full_url:
                return _resp({"code": 200, "data": {"taskId": "t1"}})
            if "recordInfo" in req.full_url:
                return _resp({"code": 200, "data": {
                    "state": "success",
                    "resultJson": json.dumps({"resultUrls": ["https://t/r.png"]})}})
            r = _resp({})
            r.read.return_value = b"\x89PNG"
            return r

        with patch("pptm.kie.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("pptm.kie.time.sleep"):
            kie.edit_image(prompt="p", image_paths=[src], out_path=out,
                           model="nano-banana-pro")

        create_body = next(b for u, b in captured_bodies if "createTask" in u)
        assert create_body["input"]["image_input"] == ["https://t/w.png"]

    def test_edit_uses_image_urls_for_edit_model(self, tmp_path):
        """google/nano-banana-edit는 image_urls 파라미터를 써야 함."""
        src = tmp_path / "w.png"
        src.write_bytes(b"\x89PNG")
        out = tmp_path / "o.png"
        kie = KieClient(api_key="k")

        captured_bodies = []

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode()) if req.data else {}
            captured_bodies.append((req.full_url, body))
            if "file-base64-upload" in req.full_url:
                return _resp({"success": True, "code": 200,
                              "data": {"downloadUrl": "https://t/w.png"}})
            if "createTask" in req.full_url:
                return _resp({"code": 200, "data": {"taskId": "t1"}})
            if "recordInfo" in req.full_url:
                return _resp({"code": 200, "data": {
                    "state": "success",
                    "resultJson": json.dumps({"resultUrls": ["https://t/r.png"]})}})
            r = _resp({})
            r.read.return_value = b"\x89PNG"
            return r

        with patch("pptm.kie.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("pptm.kie.time.sleep"):
            kie.edit_image(prompt="p", image_paths=[src], out_path=out,
                           model="google/nano-banana-edit")

        create_body = next(b for u, b in captured_bodies if "createTask" in u)
        assert create_body["input"]["image_urls"] == ["https://t/w.png"]
