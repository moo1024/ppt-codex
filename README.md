# ppt-master-v2

**Codex로 편집 가능한 PPTX를 자동 생성하는 파이프라인 (아키텍처 v7).**

사용자가 내용을 주면 Codex가 직접 **내용 정리 → 컷 분할 → 디자인**해서
`layout_spec.json`을 작성하고, python-pptx **네이티브 개체**로 렌더합니다.
결과물은 파워포인트에서 **텍스트 100% 편집 가능** (클릭·수정·복사·검색).
커버·스팟 이미지는 **Codex 내장 `$imagegen`**(gpt-image-2, API 키 불필요, ChatGPT 로그인 사용량)로 생성합니다.

```
내용/자료 입력
    ↓ (Codex: 컷 분할 · 톤 분석 · 테마 선택)
projects/<slug>/pages/pNN/layout_spec.json   ← 페이지별 레이아웃 스펙
    ↓ (pptm rendernative — python-pptx 네이티브 렌더)
deck.pptx (편집 가능한 한글 텍스트 · 도형 · 네이티브 차트/표)
    ↓ (pptm export — LibreOffice + pdftoppm)
PDF + 슬라이드 썸네일 (검수용)
    ↓ (tools/check_align.py — 정렬 자동 검수 게이트)
완성
```

## 핵심 특징

- **100% 편집 가능**: 통짜 이미지가 아니라 네이티브 텍스트박스·도형·차트로 렌더 — 받는 사람이 직접 수정
- **한글 정확**: 텍스트는 스펙에서 그대로 렌더 (OCR 없음, 글리프 깨짐 없음)
- **테마 시스템**: 40여 종 테마(.json) — 톤에 맞춰 색·서피스 문법 일괄 적용
- **정렬 검수 게이트**: `tools/check_align.py`가 어긋난 정렬을 기계적으로 잡아냄
- **이미지도 키 불필요**: Codex 내장 `$imagegen`(gpt-image-2)로 커버·스팟 생성 — 별도 API 키 없이 ChatGPT 로그인 사용량으로 (본문은 네이티브)

> 참고: v1~v6은 "AI 통짜 이미지 → 자동 분해" 방식이었으나 폐기됨.
> 현재는 v7(네이티브 직접 렌더)만 유효합니다.

## 설치

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 이미지 생성은 Codex 내장 $imagegen 사용 — 별도 API 키 불필요

# 환경 점검 (LibreOffice · poppler · KIE_API_KEY)
pptm doctor
```

> Codex 설치: `npm install -g @openai/codex` (ChatGPT 계정으로 로그인하면 이미지 생성까지 키 없이 됩니다.)

### 협업자 글꼴 설치

PPTX를 다른 사람이 동일한 모양으로 편집하려면, 먼저 저장소의
[`fonts/README.md`](fonts/README.md)에 따라 제공 글꼴을 설치하세요. Paperlogy·Pretendard가
기본이며 Gmarket Sans·The Jamsil·Noto Sans KR도 함께 제공합니다. 모든 글꼴은 재배포 조건과
라이선스 고지를 포함해 관리합니다.

## 사용법 — Codex로 여는 게 핵심

이 저장소는 **Codex로 열어서 쓰는 도구**입니다. `AGENTS.md`에 담긴 작업 지침을
Codex가 읽고 표준 플로우대로 덱을 만들어 줍니다.

1. Codex를 이 폴더에서 실행
2. **"이 내용으로 PPT 만들어줘"** 라고 자료·요청을 전달
3. Codex가 컷 분할 → 톤 분석 → 테마 선택 → `layout_spec.json` 작성 → 이미지($imagegen) → 렌더 → 검수까지 수행
4. 결과물 `projects/<slug>/output/deck.pptx` 확인

수동 CLI 흐름:

```bash
pptm new my-deck                       # 프로젝트 초기화
# → projects/my-deck/pages/pNN/layout_spec.json 작성 (Codex가 함)
pptm rendernative my-deck              # layout_spec → deck.pptx
pptm export my-deck --force            # PDF + 썸네일 (검수용)
python3 tools/check_align.py my-deck   # 정렬 게이트 — 0건이어야 완성
pptm status my-deck                    # 진행 상황

# 이미지는 Codex 내장 $imagegen 으로 생성 → assets/spots/ 에 저장 후 image 아이템으로 참조
```

## 디렉토리 구조

```
ppt-master-v2/
├── AGENTS.md                # ★ Codex 작업 지침 (규칙·플로우·트랙 분기)
├── config.yaml
├── .env                     # KIE_API_KEY (git-ignored, 선택)
├── docs/                    # 설계·레퍼런스 문서
│   ├── SPEC.md              #   layout_spec 아이템 타입·레시피 카탈로그
│   ├── THEMES.md            #   톤 분석표 · 테마 36종 · 신규 테마 제작
│   ├── PITFALLS.md          #   렌더러 함정 · 폰트명 규칙
│   └── design-refs-*.md     #   도식 어휘 · 프리미엄 문법 등
├── .codex/
│   ├── agents/              # 멀티에이전트 분업 (copy · layout · qa)
│   └── skills/gyeolbo/      # 결과보고서(A4 문서형) 스킬
├── pptm/                    # 파이썬 패키지
│   ├── cli.py               # typer CLI (new/rendernative/export/spot/status/doctor)
│   ├── design/
│   │   ├── gyoan.py         # ★ 네이티브 렌더러 (layout_spec → deck.pptx)
│   │   └── themes/*.json    # 테마 40여 종
│   ├── kie.py · spot.py     # kie.ai 이미지 클라이언트
│   └── stages/export.py     # deck.pptx → PDF + 썸네일
├── tools/
│   └── check_align.py       # ★ 정렬 검수 게이트
└── projects/<slug>/         # 산출물 (git-ignored, 로컬 데이터)
    ├── pages/pNN/layout_spec.json
    ├── assets/spots/        # AI 스팟 이미지
    └── output/              # deck.pptx · deck.pdf · thumbnails/
```

## 시스템 요구사항

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (venv 생성용)
- **Codex** — 이 저장소의 지침을 읽고 덱을 설계·렌더 (핵심 사용 인터페이스)
- LibreOffice (`soffice`) — PDF 내보내기용
- poppler (`pdftoppm`) — 슬라이드 썸네일 생성용
- (이미지) Codex 내장 `$imagegen` — 추가 키·설치 없음

```bash
# Ubuntu/Debian
sudo apt install libreoffice-impress poppler-utils
```

## 개발

```bash
pytest -q                              # 전체 테스트
python3 tools/check_align.py <slug>    # 정렬 게이트 (완성 전 필수)
```

렌더러(gyoan.py) 수정 시 TDD 권장. 모든 외부 API 호출은 테스트에서 mock 처리됩니다.

## 라이선스

**소스 코드는 [MIT 라이선스](LICENSE)** — 복사·수정·재배포·상업적 이용 모두 자유입니다.
저작권 고지와 라이선스 전문만 함께 남겨주세요.

단, **`fonts/` 아래 글꼴 파일은 MIT가 아닙니다.** 각 글꼴의 원 라이선스를 따릅니다.

| 글꼴 | 라이선스 | 비고 |
|---|---|---|
| Paperlogy, Pretendard, Gmarket Sans, Noto Sans KR | [OFL 1.1](fonts/LICENSES/OFL-1.1.txt) | 고지 동봉 시 재배포 가능 |
| The Jamsil (더잠실체) | [롯데마트 사용규정](fonts/LICENSES/THE-JAMSIL-TERMS.md) | 수정·포맷 변환 금지, 판매 금지 |

재배포할 때는 `fonts/LICENSES/` 폴더를 그대로 유지해 주세요.
