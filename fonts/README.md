# PPT 글꼴 패키지

이 폴더는 이 저장소에서 만든 PPTX를 다른 사람이 같은 모양으로 열고 편집할 수 있도록
넣어 둔 **재배포 허용 공개 글꼴** 묶음입니다. 43개 파일(TTF·OTF·TTC), 약 112MB입니다.

## 포함 글꼴과 용도

| 글꼴 | 폴더 | 파일 | 권장 역할 |
|---|---|---:|---|
| Paperlogy 1–9 | `paperlogy/` | 9 | 기본 제목·소제목. 헤드라인은 `Paperlogy 8 ExtraBold`, 카드/표 헤더는 `Paperlogy 7 Bold` |
| Pretendard 1–9 | `pretendard/` | 9 | 기본 본문·표·캡션 |
| Gmarket Sans | `gmarket-sans/` | 3 | 친근한 브랜드·캠페인형 제목 |
| The Jamsil 1–6 | `the-jamsil/` | 6 | 모던한 문화·유통·라이프스타일형 제목 |
| Noto Sans KR Variable | `noto-sans-kr/` | 1 | 외부 환경 호환용 본문 대체 글꼴 |
| KoPubWorld 돋움체·바탕체 | `kopub-world/` | 4 | 공공·정책 보고서. 바탕체는 인용·정론형 본문 |
| KoPub 돋움체 | `kopub/` | 3 | 공공·정책 보고서의 제목·강조 |
| 에스코어 드림 5·7 | `s-core-dream/` | 2 | 기업·IR형 제목. `에스코어 드림 7 ExtraBold`가 헤드라인 |
| Freesentation 6·8 | `freesentation/` | 2 | 발표 특화 제목·소제목 |
| 에이투지체 5·7 | `a2z/` | 2 | 모빌리티·테크형 제목 |
| 던파 비트비트체 v2 | `dnf-bitbit/` | 1 | 픽셀 디스플레이. `bitbit` 테마 제목 전용 |
| D2Coding | `d2coding/` | 1 | 코드 블록·모노스페이스 |

기본 규칙은 변하지 않습니다. 일반 보고서의 제목·소제목은 Paperlogy, 본문은 Pretendard를
우선합니다. Gmarket Sans와 The Jamsil은 주제와 테마에 어울릴 때만 제목용으로 사용하며,
수치 중심의 공공·정책 보고서 본문에는 쓰지 않습니다. 던파 비트비트체는 제목에만 쓰고
본문에는 쓰지 않습니다.

## 번들하지 않는 테마 글꼴

`pptm/design/themes/*.json` 중 일부는 아래 글꼴을 지정하지만, 재배포가 금지되어 있어
이 저장소에 **파일을 넣지 않습니다.** 해당 테마를 쓰려면 각 배포처에서 직접 내려받아
설치해야 하며, 설치하지 않으면 PowerPoint가 대체 글꼴로 표시합니다.

| 글꼴 | 사유 |
|---|---|
| 교보 손글씨 2019 | 재배포·수정·양도 금지(교보문고) |
| 비트로 코어 TTF | 재배포·복제 금지(㈜학산) |
| Rix이누아리두리 Regular | 재배포·수정 금지(폰트릭스) |
| 한컴 말랑말랑 Regular·Bold, 한컴산뜻돋움 | 수정·재배포 금지(한글과컴퓨터) |
| 삼성긴고딕 Ultralight·Medium·Bold | 삼성 기업 전용 서체 |
| Georgia | Microsoft 번들 글꼴 |

## 설치

PowerPoint에서 파일을 편집할 사람은 사용 전에 이 폴더의 글꼴 파일을 운영체제에 설치해야
합니다. Windows에서는 파일을 모두 선택해 우클릭한 뒤 **모든 사용자용으로 설치**를 선택합니다.
설치 후 PowerPoint를 다시 열어 주세요. 설치하지 않은 환경에서는 PowerPoint가 대체 글꼴로
표시할 수 있습니다.

## 라이선스

- Paperlogy, Pretendard, Gmarket Sans, Noto Sans KR, D2Coding, Freesentation, 에이투지체는
  SIL Open Font License 1.1(OFL)입니다. 전문은 [LICENSES/OFL-1.1.txt](LICENSES/OFL-1.1.txt),
  글꼴별 저작권 고지는 [LICENSES/NOTICE.md](LICENSES/NOTICE.md)에 있습니다. 폰트 파일을 단독
  판매하지 않는 한 사용·번들·재배포가 가능하며, 저작권·라이선스 고지를 함께 유지해야 합니다.
- The Jamsil은 롯데쇼핑(롯데마트) 소유 글꼴입니다. 사용·소프트웨어 번들·재배포는 가능하지만,
  저작권 고지와 사용규정을 함께 제공해야 하고 수정·포맷 변환·폰트 단독 유료 판매는 금지됩니다.
  전문 요약은 [LICENSES/THE-JAMSIL-TERMS.md](LICENSES/THE-JAMSIL-TERMS.md)에 있습니다.
- KoPub·KoPubWorld는 문화체육관광부·한국출판인회의 소유 글꼴입니다. 본 라이선스를 함께
  배포하는 조건으로 재배포가 허용되며, 서버 임베딩은 별도 승인이 필요합니다. 약관 요지는
  [LICENSES/KOPUB-TERMS.md](LICENSES/KOPUB-TERMS.md)에 있습니다.
- 던파 비트비트체 v2는 ㈜네오플 소유 글꼴입니다. 저작권 고지를 포함하면 번들·재배포가
  가능하지만 수정과 유료 판매는 금지됩니다. 사용규정은
  [LICENSES/DNF-BITBIT-TERMS.md](LICENSES/DNF-BITBIT-TERMS.md)에 있습니다.
- 에스코어 드림은 에스코어㈜ 소유 글꼴입니다. 저작권 고지를 포함하면 번들·재배포가 가능하며
  수정과 유료 판매는 금지됩니다. 사용규정은
  [LICENSES/S-CORE-DREAM-TERMS.md](LICENSES/S-CORE-DREAM-TERMS.md)에 있습니다.

이 폴더에는 개인 구매·회사 전용·Windows 기본 글꼴을 넣지 않습니다. 새 글꼴을 추가할 때에는
반드시 재배포 및 번들 허용 여부를 확인하고 해당 라이선스 전문을 `LICENSES/`에 같이 넣습니다.
