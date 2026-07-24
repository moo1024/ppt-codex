"""pptm CLI — v7: layout_spec → 네이티브 PPTX 렌더 + 검수 파이프라인."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="ppt-master-v2 AI PPT 파이프라인 (v7: Claude 직접 디자인)")

_ROOT = Path(__file__).parent.parent


def _simple_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def _load_kie():
    from pptm.kie import KieClient
    _simple_dotenv(_ROOT / ".env")
    key = os.environ.get("KIE_API_KEY", "")
    if not key:
        typer.echo("KIE_API_KEY 환경변수가 없습니다. .env 파일을 확인하세요.", err=True)
        raise typer.Exit(2)
    return KieClient(api_key=key)


def _proj(slug: str) -> Path:
    p = _ROOT / "projects" / slug
    if not p.exists():
        typer.echo(f"프로젝트 '{slug}' 없음. `pptm new {slug}` 먼저 실행하세요.", err=True)
        raise typer.Exit(1)
    return p


# ── 커맨드 ────────────────────────────────────────────────────────────────

@app.command()
def new(
    slug: str = typer.Argument(..., help="프로젝트 식별자"),
    source: Optional[Path] = typer.Option(None, help="자료 파일 (.md / .txt)"),
    request: Optional[str] = typer.Option(None, help="제작 요청 문자열"),
):
    """새 덱 프로젝트를 초기화합니다."""
    proj = _ROOT / "projects" / slug
    (proj / "input").mkdir(parents=True, exist_ok=True)
    (proj / "pages").mkdir(parents=True, exist_ok=True)
    if source:
        import shutil
        shutil.copy(source, proj / "input" / "source.md")
    if request:
        (proj / "input" / "request.md").write_text(request, encoding="utf-8")
    typer.echo(f"✓ 프로젝트 생성: {proj}")
    typer.echo(f"  다음: {proj}/pages/p01/layout_spec.json 작성 → pptm rendernative {slug}")


@app.command()
def rendernative(slug: str = typer.Argument(...)):
    """layout_spec.json → 네이티브 PPTX 렌더."""
    from pptm.design.gyoan import render_deck
    out = render_deck(_proj(slug))
    typer.echo(f"✓ 네이티브 렌더: {out}")


@app.command()
def export(
    slug: str = typer.Argument(...),
    dpi: int = typer.Option(150, help="썸네일 해상도 (DPI)"),
    force: bool = typer.Option(False, "--force", help="캐시 무시 재생성"),
):
    """deck.pptx → PDF + 썸네일 (LibreOffice + pdftoppm)."""
    from pptm.stages.export import run_export
    run_export(project_dir=_proj(slug), dpi=dpi, force=force)
    typer.echo(f"✓ export 완료: {_proj(slug) / 'output'}")


@app.command()
def spot(
    slug: str = typer.Argument(...),
    prompt: str = typer.Option(..., "--prompt", "-p", help="이미지 주제 (영문)"),
    bg: str = typer.Option("F7F5F1", help="슬라이드 배경색 HEX — 반드시 맞출 것"),
    dark: bool = typer.Option(False, "--dark", help="다크 페이지용"),
    fullbleed: bool = typer.Option(False, "--fullbleed", help="16:9 풀블리드 시네마틱"),
    dark_side: str = typer.Option("right", "--dark-side",
                                  help="풀블리드에서 글자 앉힐 어두운 면: left|right|top|bottom|none"),
    n: int = typer.Option(1, "-n", help="생성 장수"),
    name: str = typer.Option("spot", help="파일 이름 접두어"),
    model: str = typer.Option("google/nano-banana", help="kie 모델 (포토리얼은 nano-banana-pro)"),
    aspect: str = typer.Option("16:9", help="종횡비: 16:9 | 3:4 | 4:3 | 1:1 …"),
    resolution: str = typer.Option("1K", help="1K | 2K"),
    force: bool = typer.Option(False, "--force", help="기존 파일 덮어쓰기"),
):
    """kie.ai 스팟/풀블리드 이미지 → assets/spots/."""
    from pptm.spot import run_spot
    kie = _load_kie()
    try:
        paths = run_spot(
            _proj(slug), kie=kie, prompt=prompt, bg=bg, dark=dark,
            fullbleed=fullbleed, dark_side=dark_side, n=n, name=name,
            model=model, aspect=aspect, resolution=resolution, force=force,
        )
    except (FileExistsError, ValueError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1)
    for p in paths:
        typer.echo(f"✓ {p}")


@app.command()
def status(slug: str = typer.Argument(...)):
    """프로젝트 진행 상황을 출력합니다."""
    proj = _proj(slug)
    typer.echo(f"\n프로젝트: {slug}")
    typer.echo("─" * 48)

    pages_root = proj / "pages"
    specs = sorted(pages_root.glob("p*/layout_spec.json")) if pages_root.exists() else []
    typer.echo(f"  스펙  : {'✓ ' + str(len(specs)) + '장' if specs else '─ 없음'}")

    spots = list((proj / "assets" / "spots").glob("*.png")) if (proj / "assets" / "spots").exists() else []
    if spots:
        typer.echo(f"  스팟  : ✓ {len(spots)}장")

    out_dir = proj / "output"
    pptx, pdf = out_dir / "deck.pptx", out_dir / "deck.pdf"
    thumbs = list((out_dir / "thumbnails").glob("slide-*.jpg")) if (out_dir / "thumbnails").exists() else []

    typer.echo(f"  PPTX : {'✓ ' + str(round(pptx.stat().st_size / 1024)) + ' KB' if pptx.exists() else '─ 미생성'}")
    typer.echo(f"  PDF  : {'✓ ' + str(round(pdf.stat().st_size / 1024)) + ' KB' if pdf.exists() else '─ 미생성'}")
    typer.echo(f"  썸네일: {'✓ ' + str(len(thumbs)) + '장' if thumbs else '─ 미생성'}")
    typer.echo("")


@app.command()
def doctor():
    """환경 점검 (LibreOffice, poppler, KIE_API_KEY)."""
    import shutil
    _simple_dotenv(_ROOT / ".env")
    ok = True

    for cmd, why in [("soffice", "PDF·썸네일 내보내기"), ("pdftoppm", "썸네일 변환")]:
        if shutil.which(cmd):
            typer.echo(f"✓ {cmd}")
        else:
            typer.echo(f"✗ {cmd} 없음 — {why} 불가", err=True)
            ok = False

    if os.environ.get("KIE_API_KEY"):
        typer.echo("✓ KIE_API_KEY 설정됨")
    else:
        typer.echo("! KIE_API_KEY 없음 — pptm spot 불가 (렌더·export는 정상)")

    raise typer.Exit(0 if ok else 1)


if __name__ == "__main__":
    app()
