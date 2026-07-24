"""Stage 7: deck.pptx → PDF + 썸네일 (soffice + pdftoppm)."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

from pptm.cache import ArtifactCache

GRID_COLS = 3
GRID_MAX = 12


def _patch_odp_cjk(odp_src: Path, odp_dst: Path) -> None:
    with zipfile.ZipFile(odp_src, "r") as zin:
        with zipfile.ZipFile(odp_dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in ("styles.xml", "content.xml"):
                    data = data.replace(
                        b'style:text-autospace="ideograph-alpha"',
                        b'style:text-autospace="none"',
                    )
                zout.writestr(item, data)


def _soffice_cmd(profile_dir: Path, *args: str) -> list[str]:
    """전용 프로필로 soffice 실행 — 상주 인스턴스의 프로필 락과 충돌하지 않게.

    락 충돌 시 ODP 변환이 실패해 CJK 패치 없는 직행 폴백으로 떨어지는 사고 방지.
    """
    return ["soffice", f"-env:UserInstallation=file://{profile_dir}", "--headless", *args]


def export_pdf(pptx_path: Path, outdir: Path) -> Path:
    if shutil.which("soffice") is None:
        raise RuntimeError("soffice(LibreOffice) 미설치 — sudo apt install libreoffice-impress")
    pdf_out = outdir / (pptx_path.stem + ".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile = tmpdir / "lo_profile"
        r1 = subprocess.run(
            _soffice_cmd(profile, "--convert-to", "odp", "--outdir", str(tmpdir), str(pptx_path)),
            capture_output=True, text=True, timeout=180,
        )
        odp_raw = tmpdir / (pptx_path.stem + ".odp")
        if r1.returncode != 0 or not odp_raw.exists():
            # 폴백(직행)은 CJK 자동간격 패치가 빠진다 — 반드시 경고를 남긴다
            print(f"! ODP 변환 실패({r1.returncode}) — CJK 패치 없이 직행 폴백: "
                  f"{(r1.stderr or r1.stdout).strip()[:200]}")
            r_fb = subprocess.run(
                _soffice_cmd(profile, "--convert-to", "pdf", "--outdir", str(outdir), str(pptx_path)),
                capture_output=True, text=True, timeout=180,
            )
            if r_fb.returncode != 0 or not pdf_out.exists():
                raise RuntimeError(f"PDF 변환 실패: {r_fb.stderr.strip() or r_fb.stdout.strip()}")
            return pdf_out
        odp_patched = tmpdir / (pptx_path.stem + "_nocjk.odp")
        _patch_odp_cjk(odp_raw, odp_patched)
        r2 = subprocess.run(
            _soffice_cmd(profile, "--convert-to", "pdf", "--outdir", str(tmpdir), str(odp_patched)),
            capture_output=True, text=True, timeout=180,
        )
        pdf_tmp = tmpdir / (pptx_path.stem + "_nocjk.pdf")
        if r2.returncode != 0 or not pdf_tmp.exists():
            raise RuntimeError(f"PDF 변환 실패(ODP→PDF): {r2.stderr.strip() or r2.stdout.strip()}")
        shutil.copy2(pdf_tmp, pdf_out)
    return pdf_out


def export_thumbnails(pdf_path: Path, outdir: Path, dpi: int = 150) -> list[Path]:
    thumb_dir = outdir / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(dpi), str(pdf_path), str(thumb_dir / "slide")],
        capture_output=True, text=True, timeout=180,
    )
    if res.returncode != 0:
        raise RuntimeError(f"썸네일 생성 실패: {res.stderr.strip()}")
    thumbs = []
    for p in sorted(thumb_dir.glob("slide-*.jpg")):
        num = p.stem.split("-")[-1]
        canonical = thumb_dir / f"slide-{int(num):02d}.jpg"
        if p != canonical:
            p.rename(canonical)
        thumbs.append(canonical)
    thumbs = sorted(set(thumbs))
    thumbs += _make_grids(thumbs, thumb_dir)
    return thumbs


def _make_grids(thumbs: list[Path], thumb_dir: Path) -> list[Path]:
    grids = []
    for g, start in enumerate(range(0, len(thumbs), GRID_MAX), start=1):
        chunk = thumbs[start : start + GRID_MAX]
        images = [Image.open(p) for p in chunk]
        w, h = images[0].size
        cell_w, cell_h = w // 2, h // 2
        rows = (len(images) + GRID_COLS - 1) // GRID_COLS
        canvas = Image.new("RGB", (cell_w * GRID_COLS, cell_h * rows), "white")
        for i, img in enumerate(images):
            r, c = divmod(i, GRID_COLS)
            canvas.paste(img.resize((cell_w, cell_h)), (c * cell_w, r * cell_h))
        out = thumb_dir / f"grid-{g}.jpg"
        canvas.save(out, quality=85)
        grids.append(out)
    return grids


def run_export(
    *,
    project_dir: Path,
    dpi: int = 150,
    force: bool = False,
) -> None:
    project_dir = Path(project_dir)
    out_dir = project_dir / "output"
    pptx_path = out_dir / "deck.pptx"

    if not pptx_path.exists():
        return

    cache = ArtifactCache(out_dir)
    inputs = {"pptx_mtime": pptx_path.stat().st_mtime, "dpi": dpi}

    if cache.is_fresh("deck.pdf", inputs=inputs, force=force):
        return

    pdf_path = export_pdf(pptx_path, out_dir)
    export_thumbnails(pdf_path, out_dir, dpi=dpi)
    cache.save_meta("deck.pdf", inputs=inputs, usage={})
