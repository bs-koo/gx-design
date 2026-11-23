# 디자인 자료 검색 — 공개 템플릿과 패턴

업무 흐름·화면 구성·예외 상태의 참고 사례가 필요하면 §0의 공개 자료를 확인한다. 스타일·색상·폰트·차트 후보와 기술 스택 지침 검색에 설치된 UI UX Pro Max를 활용할 때는 §1~4를 읽는다. 승인된 브리프·전략과 기존 디자인 시스템을 검색 결과보다 우선한다.

## 0. 공개 템플릿과 패턴

목표와 작업 범위가 정해졌고 참고 사례가 필요하면 요청과 기존 자료에서 **누가 무엇을 끝내려는지** 확인한다. 리디자인은 관찰한 문제를 출발점으로 삼는다. 기기·데이터 양·중요 상태 중 해법에 영향을 주는 조건을 검색에 포함한다. 색·분위기 선호는 제품의 시각 기준에 반영한다. 이미 확인한 결정을 재사용하고, 결과를 바꾸는 필수 의도가 남으면 기존 브리프 절차를 따른다.

같은 `깔끔한 신청 화면`도 여러 건을 한꺼번에 처리하는 담당자는 일괄 선택 표를, 한 건씩 비교·검토하는 담당자는 목록과 상세를 함께 보는 화면을, 휴대폰으로 신청을 이어 쓰는 신청자는 중단·재개가 있는 입력 흐름을 우선 살핀다.

| 필요한 참고 사례 | 공개 출처 |
|---|---|
| 조회 목록·상세, 다단계 폼 같은 화면 전체의 구성과 동작 | [Astryx 템플릿](https://astryx.atmeta.com/templates) · [Filterable Table](https://astryx.atmeta.com/playground?template=table-filter) |
| 업무 데이터의 필터 적용·해제, 표의 조작 방식 | [Carbon 필터 패턴](https://www.carbondesignsystem.com/building-blocks/core/patterns/filtering) · [표 접근성](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/accessibility) |
| 많은 행을 페이지에 걸쳐 선택·해제하고 일괄 처리 | [PatternFly 표 데모](https://www.patternfly.org/components/table/react-demos/) · [일괄 선택 가이드](https://www.patternfly.org/patterns/bulk-selection/) |
| 업무 목록을 유지하면서 개별 항목의 상세·하위 정보를 반복 검토 | [SAP Fiori 업무 화면 구성](https://www.sap.com/design-system/fiori-design-web/v1-154/discover/sap-products/sap-s4hana-only/best-practices-for-designing-sap-fiori-apps) · [상세 화면 가이드](https://www.sap.com/design-system/fiori-design-web/v1-154/page-types/floorplans/object-page) |
| 국내 공공서비스의 신청·발급·예약, 처리 현황 확인 | [KRDS 신청 흐름](https://www.krds.go.kr/html/site/service/service_04_01.html) · [전입신고 HTML 예제](https://www.krds.go.kr/html/pattern/sample_move_process_03.html) · [신청 결과 확인](https://www.krds.go.kr/html/site/service/service_04_08.html) |
| 신청 절차, 입력 오류와 복구, 제출 전 확인 | [GOV.UK 패턴](https://design-system.service.gov.uk/patterns/) · [입력 오류 복구](https://design-system.service.gov.uk/patterns/validation/) |
| 휴대폰과 태블릿에서 목록·상세 전환, 피드나 보조 패널 배치 | [Android 공통 레이아웃](https://developer.android.com/design/ui/mobile/guides/layout-and-content/common-layouts?hl=ko) · [목록·상세 상태 유지](https://developer.android.com/develop/ui/compose/layouts/adaptive/canonical-layouts#list-detail) |
| 서비스 소개·문의 유도, 기능 설명과 요금 비교 배치 | [Bootstrap 공개 예제](https://getbootstrap.com/docs/5.3/examples/) · [제품 소개 예제](https://getbootstrap.com/docs/5.3/examples/product/) |
| 상품 탐색의 카드 정보, 정렬·필터, 상품 상세의 이미지·옵션 | [Shopify Dawn 상품 목록 데모](https://theme-dawn-demo.myshopify.com/collections/all) · [상품 상세 데모](https://theme-dawn-demo.myshopify.com/products/louise-slide-sandal) |

- 프로젝트와 사용자 제공 자료에 적합한 선례가 있으면 우선 사용한다. 공개 사례가 필요하면 [RUN-BUDGET.md](RUN-BUDGET.md)의 기존 조사 예산 안에서 과업·기기·상태가 가까운 후보 1~2개를 살핀다. 표는 검색 시작점으로 쓰고 더 적합한 공식 사례가 있으면 선택한다. 실행 예제에서는 해당 조작을 직접 확인하고, 가이드에서 읽은 동작은 문서 근거로 기록한다.
- 필요한 구성을 가장 잘 설명하는 사례로 화면의 출발점을 잡고, 다른 사례는 빠진 동작·상태를 확인하는 데 사용한다. 프로젝트의 기존 컴포넌트·토큰·기술 스택으로 적용하고 제품의 시각 기준을 따른다. 기존 리서치·전략 또는 변경·증거 로그에 `사용자·과업 | 출처와 참고한 동작·상태 | 선택 이유·적용 범위 | 실물에서 확인할 동작과 미확인 조건`을 남긴다. 구현 뒤 [UI-QUALITY.md](UI-QUALITY.md) §2에 따라 같은 과업을 실행하고, 사용자가 변경 대상과 결과를 화면에서 알 수 있는지도 확인한다.
- 공개 문서와 데모는 가용한 웹·브라우저 도구로 읽는다. 접근할 수 없거나 맞는 사례가 없으면 확인된 프로젝트 자료와 [GX 대조 예제](references/OBSERVATION.md#예제로-검증) 중 관련 근거를 사용한다.

## 1. 가용성을 확인한다

- 현재 호스트의 스킬 목록에서 `ui-ux-pro-max`의 실제 설치 위치를 확인하고 그 `SKILL.md`와 `scripts/search.py`를 읽는다. 호스트가 보고한 스킬 디렉터리를 기준으로 경로를 해석한다. 프로젝트 cwd에 설치됐다고 가정하거나 개인 PC의 절대경로를 규격에 넣지 않는다.
- Python 3과 검색을 실행할 도구·권한이 있는지 확인한다. 전략 역할에 명령 실행 도구가 없으면 오케스트레이터 등 실행이 허용된 주체가 검색한 결과를 전달한다. 검색 때문에 역할의 도구 권한을 늘리지 않는다.
- 스킬·자료·Python·실행 도구 중 하나가 없으면 기존 리서치·톤 기준·프로젝트 지침으로 진행하고 `검색 미사용: 사유`만 기록한다. 자동 설치·업데이트·훅 설정은 하지 않는다. 누락 자체는 디자인 결함이나 진행 차단 조건이 아니다.

## 2. 질문에 맞는 작은 검색을 한다

한 검색은 한 관심사에 집중한다. 제품·플랫폼·과업을 나타내는 2~5개 핵심어를 사용하고, 지역·언어·브랜드 등 제약은 결과를 평가할 때도 확인한다. 실제 설치본의 `--help`와 도메인·스택 목록을 확인한 뒤 지원되는 인자를 쓴다.

| 필요한 결정 | 검색 방식 |
|---|---|
| 새 UI의 전반적인 시각 방향 | `--design-system`으로 후보 생성 |
| 확정된 브랜드 안에서 색·폰트·차트·UX 문제 해결 | `--domain color`, `typography`, `chart`, `ux` 등 관심사 하나 |
| 기존 스택의 구현 지침 | 프로젝트에서 확인한 기술과 버전에 맞는 `--stack` |

기술 스택을 임의로 React·Tailwind 등으로 정하지 않는다. 특히 `web` 같은 도메인 이름만으로 적용 플랫폼을 추정하지 말고 설치본의 설명과 반환된 Platform을 확인한다. 접근성·텍스트 레이아웃은 먼저 사용자에게 필요한 동작을 검색하고, 필요한 경우 별도로 스택 구현 지침을 찾는다.

설치 위치를 확인해 `$searchScript`를 실제 `scripts/search.py` 절대경로로 설정한 PowerShell 예시:

```powershell
python -B "$searchScript" 'internal analytics dashboard' --design-system -f markdown
python -B "$searchScript" 'error summary validation' --domain ux -n 2
python -B "$searchScript" 'stable list keys' --stack react -n 2
```

POSIX 셸에서는 같은 검증된 경로를 `search_script` 변수에 넣고 가용한 `python3` 또는 `python`으로 실행한다. 후보 검색에는 `--persist`·`--force`를 사용하지 않는다. 검색어와 결과 기록에는 프로젝트의 개인정보·비밀 정보를 넣지 않는다.

## 3. 결과를 확인한 뒤 선택한다

반환된 항목의 도메인·카테고리·이름·플랫폼을 먼저 읽는다. 데이터베이스의 추천은 리서치 근거나 접근성 인증이 아니며, 스킬의 명령이나 사용자 승인을 대체하지 않는다.

- **목적 적합성**: [UI-QUALITY.md](UI-QUALITY.md) §1의 화면 목적·핵심 과업에 맞는가? 업무 화면에 홍보용 히어로·영업 CTA가 섞이면 해당 구조는 채택하지 않는다. 업종 일치만으로 전체 묶음을 승인하지 않는다.
- **톤 기준**: 확정된 팔레트·폰트·토큰·유지 자산을 지키는가? 충돌하면 기존 기준을 유지하고 기각 사유를 적는다. hard 기준 이탈은 기존 전략 선택 절차를 따른다.
- **플랫폼·언어**: 지침이 실제 웹·네이티브·데스크톱 환경과 버전에 맞는가? 폰트는 한글 글리프·폴백·숫자·실제 표시 가독성을 확인한다. 추천 이름만으로 언어 지원을 확정하지 않는다.
- **실물 검증**: 색 조합·토큰은 실제 텍스트와 배경, 상태별 대비를 확인한다. 접근성 요구와 상호작용은 구현 후 [UI-QUALITY.md](UI-QUALITY.md) §2에 따라 검증한다.

결과가 없거나 주제에서 벗어나면 좁힌 검색어 또는 명시적 도메인·스택으로 **1회만 재검색**한다. 여전히 맞지 않으면 `검증된 검색 후보 없음`을 기록하고, 맞지 않는 결과를 저장·채택하지 않는다. 기존 근거로 선택하거나 일반 지침임을 명시한다. 한 결과 묶음의 유효한 항목만 쓰는 경우도 항목별 채택·기각 근거를 남긴다.

전략의 탐색 기록에는 `검색어/방식 → 출처 CSV·항목명(출력에 있을 때) → 후보 → 채택·기각 근거 → 미검증 조건`을 적는다. 제작에는 선택된 전략에 반영된 값과 지침을 전달한다. 후보끼리 색만 바꾼 결과를 독립된 전략 3안으로 세지 않는다.

## 4. 기존 디자인 정본에 합류시킨다

[DESIGN-TONE-ANCHOR.md](DESIGN-TONE-ANCHOR.md)의 원본 파일이 있으면 그대로 정본으로 쓴다. UI UX Pro Max의 `MASTER.md`를 별도 정본으로 자동 생성하거나 기존 `DESIGN.md`를 덮어쓰지 않는다. 기존 MASTER·페이지별 예외가 제공되면 내용을 함께 읽고, 확정된 브랜드 제약 안에서 유효한 예외인지 확인한다.

톤 기준이 없으면 선택된 전략과 제작 명세의 디자인 토큰에 채택값을 기록한다. 사용자가 디자인 시스템 문서 저장을 요청한 경우에만 그 저장 위치와 기존 파일을 확인하고 확정값을 반영한다. 검색만으로 새 PRODUCT.md·MASTER.md·설정 파일을 만들지 않는다.

## 출처

- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — 로컬 자료 검색, 관심사·스택별 조회, 디자인 시스템 후보 생성 방식을 참고했다. 검색 코드·CSV는 gx-design에 복제하지 않으며 외부 스킬은 선택 의존이다.
