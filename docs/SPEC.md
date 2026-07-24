# layout_spec.json 스펙 — PPT 제작 시 필독

CLAUDE.md 표준 플로우 3단계(스펙 작성)에 들어가기 전에 이 문서를 연다.
경로: `projects/<slug>/pages/pNN/layout_spec.json`

## 기본 형태

```json
{"page": 1, "theme": "gyoan", "variant": "paper|dark", "items": [...]}
```

- 좌표는 전부 슬라이드 비율 0~1 (16:9). 마진 x=0.05~0.07, sowhat은 y=0.885 고정.
- `variant: "dark"` = 배경이 테마의 dark_bg, headline이 divider_h(30pt)로 커짐. 표지/디바이더용.
- `page_size: "a4p"` = A4 세로 (결보 트랙 전용 — docs/design-refs-gyeolbo.md 참조).
- `page_size: "3:4"` = 세로 포스터·키비주얼 (인스타·에타 마스터). 풀블리드 이미지 +
  상단 scrim + 네이티브 카피 오버레이 조합. 실물 `projects/jobfair-kv`.
  kie 장면도 같은 비율로: `pptm spot <slug> --aspect 3:4 --model nano-banana-pro`.
- 일회성 테마가 필요하면 spec에 `theme_tokens: {...}` 인라인.

## 아이템 타입

### 텍스트 계열
- `label` — 좌상단 아이브로우
- `serif_label` — 세리프 아이브로우
- `headline` — `lines`(줄 배열) 또는 `runs`(리치텍스트)
- `text` — `style: sub|body|cardtitle|caption|meta|num_xl...`
- 공통 키 **`tracking`**(자간, pt) — `label`/`headline`/`text`에 적용. 런별 `{"t":…,"tracking":…}`로
  덮어쓸 수 있다. 매거진 마스트헤드는 **가는 웨이트 + `tracking` 2~3**이 정석
  (예: `2026 경북대학교 JOB FAIR` = Pretendard Light 10.5pt / tracking 2.9).
  음수도 가능(대형 헤드라인 -0.1~-0.3으로 조임).

### 서피스 계열
- `card` — fill / outline / radius / rot / **grad**[top,bottom] / **shadow**
- `pill` — 자동 폭, fill / text_color
- `chip` — 원형
- `hairline` — color / **dash** / **thick**
- `arrow`
- `band` — **채워진 클로저/캡션 바.** 라벨+본문 세로·가로 자동 중앙 정렬:
  fill / radius / label / label_color / text / text_color / align[center 기본] / size
- `scrim` — 풀블리드 이미지용 알파 그라데이션 오버레이:
  edge[bottom/top/left/right] / h 또는 w / color / strength / softness.
  투명→color로 페이드, 그 위에 글씨만 얹는 시네마틱 자막용.
- `sowhat` — 하단 요약 바 (헤어라인식)

### 도식 계열
- `timetable` / `bars` / `steps` / `image`(스팟)
- `shape` — `shape: hexagon|parallelogram|pie|arc_ring|chevron|pentagon_arrow|oval|
  triangle|diamond|rounded` — fill("none" 가능) / outline / adj / rot / 내부 text

### 네이티브 개체 (편집 가능)
- `chart` — 엑셀 백업 내장. `kind[bar/column/line/line_markers/pie/doughnut]` /
  categories / series[{name,values,color}] / colors[포인트별 또는 시리즈별] /
  value_labels / label_format(예 `0.0"×"`) / cat_axis / val_axis / gridlines /
  gap / legend / value_max
- `table` — 셀 편집 가능. rows[[…]] / header / col_w / align[열별] /
  header_fill / header_color / body_fill / alt_fill / border_color / size / row_h

## 리치텍스트

```json
"runs": [[{"t":"텍스트","color":"HEX","font":"serif","size":11,"weight":"bold"}]]
```
바깥 리스트가 줄, 안쪽이 런. `font` 키는 테마 fonts의 키(display_b/body/serif 등).

## 자주 쓰는 레시피

- **3카드 그리드**: x = 0.07 / 0.37 / 0.67, w = 0.26
  (또는 0.07 / 0.3735 / 0.677, w 0.253)
- **featured 밴드**: card x0.07 y≈0.56 w0.86 h0.20 + 흰 텍스트 + 우측 pill(x≈0.79)
- **커버**: label(y0.09) → headline(y0.2~0.33, size 28~35, spacing 1.3) → sub → pill → 하단 meta
- **넘버 서클 체인** (단계 도식 표준): chip d0.046 → 라인 y = chip_y+0.040(원 세로중앙) →
  단계명 y = chip_y+0.097(cardtitle 12.5) → 캡션 +0.04

## 인포그래픽 조립 카탈로그 (골격이 필요하면 여기서 고른다)

| 문서 | 내용 |
|---|---|
| `docs/design-refs-krlocal.md` §2 | **29종** — 레일 스펙 테이블, 빅넘버 그리드, 페어 바, As-Is→To-Be, 조직도, 스텝 필 체인, 컬러캡 카드, 단가표(정가→할인가), 코드칩, 하단 선언 바 |
| `docs/design-refs-kmong.md` §2~§4 | **71종** — 프레임·내비/커버/비교/수치/타임라인/표/콜아웃 + 강조 기법 13계열 + 안티패턴. 파스텔 히트 테이블, 활성 탭 돌출 내비, 형광펜 하이라이트, 낙관 도장 칩 |
| `docs/design-refs-paperlogy.md` §7 | **~60종** — 스포트라이트 콘, 3색 감정 체인, 컨테이너 인버전, 정답 열 틴트 표, 폰 목업 조립, 크롭 줌 페어. **프리미엄·시네마틱 의뢰에선 이 문서가 krlocal·kmong보다 우선** |
| `docs/design-refs-260717.md` | 부서 스윔레인 플로우 · 그룹 스팬 간트(세로 그룹 라벨+주 서브컬럼) · 다크 럭스(포토모자이크+헤어라인 아웃라인 카드) |

## 검증된 실물 예시

- `projects/style-gallery/pages/` — 테마 전종 × 커버+내지 (크몽분 p39~p60, 격상분 p61~p70)
- `projects/hackathon-ai/pages/` — 일반 덱
- `projects/deepwork/pages/` — p02 빅넘버 3카드, p04 네이티브 차트
- `projects/cinema-demo/pages/` — 시네마틱 풀블리드 4장
- `projects/goyo/pages/` — p09 scrim 자막
- `projects/step-lab/pages/` — p01 넘버 서클 체인 A/B/C안

## 스팟 이미지 (kie.ai)

- 모델 nano-banana 1K, `KIE_API_KEY`는 `.env`. 일일 크레딧 리셋 = **KST 09:00**.
- **프롬프트에 슬라이드 배경색을 반드시 명시**:
  `"single ceramic cup, on solid warm paper #F7F5F1 background, soft studio light"`
  — 안 하면 붙였을 때 티 난다. 누끼 불필요.
- 다크 페이지용은 다크 배경으로 생성. 저장은 `assets/spots/`, 배치는 spec의 `image` 아이템.

### 시네마틱 풀블리드 트랙 (2026-07-17 검증, 실물 projects/cinema-demo)

프리미엄 브랜드 덱(PAPERLOGY류)은 스팟이 아니라 **16:9 풀블리드 이미지가 주인공** —
`image` 아이템 x0 y0 w1 h1 + 그 위에 초대형 타이포(다크 영역에 배치).

- **밝은 이미지 위 자막에 검정 card 박스 금지 — 둥둥 뜬다.**
  `scrim`(하단 알파 그라데이션)을 깔고 그 위에 흰 글씨만 (2026-07-19 확정, 실물 goyo p9).
  자연히 어두운 영역이 있으면 스크림 없이 바로 얹어도 됨.
- 프롬프트 문법: `cinematic / volumetric light / film grain / high contrast monochrome`
  \+ **텍스트 앉힐 영역을 어둡게 주문** (`"right third fades to near black"`).
- 절반 이미지 + 다크 데이터 패널 조합은 cinema-demo p3.
- 생성물에 워터마크가 박히면 이미지 w/h를 1.1~1.2로 키워 프레임 밖으로.
- 생성 이미지에 박힌 브랜드명(LUNA BREW류)은 카피와 통일하면 오히려 자산이 된다.
