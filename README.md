<div align="center">

# gx-design

**브랜드·그래픽·UX/UI·영상의 기획, 제작, 개선과 품질 검토를 지원하는 디자인 워크플로.**

Claude Code와 Codex에서 프로젝트의 목표와 기준을 정리하고,
필요한 조사, 디자인 방향 수립, 제작, 최종 검토를 연결합니다.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-%EC%86%8C%EA%B0%9C%20%ED%8E%98%EC%9D%B4%EC%A7%80-533afd?style=for-the-badge&logo=github&logoColor=white)](https://bs-koo.github.io/gx-design/)

[빠른 시작](#빠른-시작) · [결과물](#결과물과-완료-기준) · [요청 예시](#요청-작성-예시) · [진행 방식](#진행-방식) · [FAQ](#faq) · [유지보수](#유지보수와-참고-문서)

</div>

## 작업에 맞는 시작점

개발자·기획자·디자이너가 새 디자인을 기획하거나 기존 결과물을 개선할 때 사용할 수 있습니다. 브랜드 경험(BX)·아이덴티티, 캠페인 그래픽, 웹·앱 화면, 영상·모션 그래픽을 다룹니다.

| 요청 | 시작점 | 사용 예 |
|---|---|---|
| 새 결과물 기획·제작 | `gx-design` | 브랜드 아이덴티티, 랜딩 페이지, SNS 그래픽, 소개 영상 |
| 기존 결과물 개선·리뉴얼 | `gx-redesign` | 업무 화면 개편, 특정 컴포넌트 수정, 브랜드 적용 개선 |
| 기존 결과물 점검·감사·테스트 | `gx-redesign` | 모바일 여정, 접근성, 모션 점검. 점검 전용은 보고로 완료 |

전체 프로젝트뿐 아니라 단일 화면이나 특정 문제도 요청할 수 있습니다. 필요한 단계는 요청 범위와 이미 확정한 기준에 맞춰 적용합니다.

## 빠른 시작

### Claude Code

```text
/plugin marketplace add bs-koo/gx-design
/plugin install gx-design@gx-design
```

Claude Code를 재시작한 뒤 요청합니다.

```text
/gx-design:gx-design 대학생 캠퍼스 중고거래 서비스 UX/UI
/gx-design:gx-redesign 커머스 앱 홈·상세 화면 리뉴얼
```

### Codex

```powershell
codex plugin marketplace add bs-koo/gx-design
codex plugin add gx-design@gx-design
```

새 Codex 대화에서 `$`로 스킬을 호출합니다.

```text
$gx-design 대학생 캠퍼스 중고거래 서비스 UX/UI
$gx-redesign 커머스 앱 홈·상세 화면 리뉴얼
```

자연어 요청도 지원합니다. 예를 들어 “브랜드를 만들어줘”는 신규 제작, “화면을 리뉴얼해줘”는 기존 개선으로 구분합니다. Codex에서는 `$gx-design` 또는 `$gx-redesign` 호출이 안정적인 진입 방법입니다. 설치 확인과 업데이트는 아래 [유지보수 안내](#유지보수와-참고-문서)를 참고하세요.

## 결과물과 완료 기준

요청한 결과물과 제작 방식을 기준으로 작업합니다. 실제 파일 제작·내보내기는 현재 사용할 수 있는 도구와 실행 환경에 따라 달라집니다.

| 결과물 | 제공 범위 | 완료 상태의 구분 |
|---|---|---|
| 기획·설계 문서 | 브리프, 조사·전략, 브랜드 가이드, 화면 명세, 카피, 스토리보드 | 문서 자체를 검토하여 완료 |
| 생성용 프롬프트 | Gemini 이미지·영상 생성용 프롬프트 패키지 | 프롬프트 완성과 이미지·영상 생성은 별도 |
| 이미지·그래픽 | 코드 렌더링을 통한 PNG 등, 도구가 지원하는 `.pen` 파일 | 최종 파일을 직접 확인하여 검토 |
| 영상·모션 그래픽 | 코드 렌더링을 통한 MP4 또는 편집 도구 인계 가이드 | 영상 명세·편집 가이드와 MP4 완성은 별도 |
| UX/UI | 실행 가능한 프로토타입·기존 코드 수정, 도구가 지원하는 `.pen` 시안 | 시안과 실행 UI를 구분하고 관련 화면·과업을 검증 |
| 점검 보고 | 문제 위치·관찰 증거·영향·수정 방향, 검증 한계 | 점검 전용 요청은 원본 수정 없이 보고로 완료 |

결과물 형식과 방식이 이미 정해졌으면 같은 선택을 다시 묻지 않습니다. 미정인 경우에만 실행 가능한 경로와 제약을 설명합니다. 이미지·영상의 제작 경로를 비교할 때는 Gemini 프롬프트 옵션도 포함합니다. 문서나 프롬프트만 요청했다면 해당 패키지를 완성합니다.

최종 보고에는 결과물 경로와 검토 상태, 남은 문제, 미검증 범위를 표시합니다. 문서 검토 결과를 실제 PNG·MP4·실행 UI의 통과 근거로 사용하지 않습니다. 필수 기준이 미검증이거나 요청 범위 안에 미해결 Critical·Major 문제가 남으면 통과를 보류합니다.

산출물은 지정한 위치에 저장합니다. 위치를 정하지 않았다면 실행한 프로젝트의 `outputs/brief/`, `outputs/research/`, `outputs/strategy/`, `outputs/production/`, `outputs/final/`을 사용하며 저장할 때 필요한 폴더를 만듭니다. 문서 파일명은 `YYYY-MM-DD_<project>_<document-type>.md` 형식입니다. 간단한 부분 수정은 원본 파일과 간결한 변경·검토 기록으로 정리합니다.

## 요청 작성 예시

한 문장으로 시작할 수 있습니다. 아래 정보를 함께 주면 확인이 필요한 결정을 줄일 수 있습니다.

```text
[대상] + [사용자·목적] + [원하는 결과물] + [기준 자료·보존 조건] + [범위·기기]
```

모든 항목을 채울 필요는 없습니다. 첫 질문이 필요하면 요청에서 확인된 내용과 미정인 내용을 먼저 요약하고, 지금 결정해야 하는 항목만 묻습니다. 브랜드 가이드·`DESIGN.md`·참고 이미지가 있으면 함께 제공하고, 반드시 유지할 기준과 참고할 방향을 구분해 주세요.

아래는 Claude Code 호출 예시입니다. Codex에서는 앞의 명령을 다음과 같이 바꾸고 같은 요청문을 사용합니다.

| 작업 | Claude Code | Codex |
|---|---|---|
| 신규 제작 | `/gx-design:gx-design` | `$gx-design` |
| 기존 개선·점검 | `/gx-design:gx-redesign` | `$gx-redesign` |

**신규 UX/UI — 랜딩 페이지**

```text
/gx-design:gx-design 사내 협업툴 소개 랜딩 페이지. 도입을 검토하는 IT 팀장이 대상이고 목표는 도입 문의. 실제 제품 화면이 중심인 절제된 구성으로, 첨부한 DESIGN.md를 유지해줘. 데스크톱·모바일에서 실행 가능한 프로토타입이 필요해.
```

**부분 수정 — 지정한 화면 영역**

```text
/gx-design:gx-redesign 대시보드의 상태 카드 간격과 제목 위계만 정리해줘. 기존 색상·폰트·데이터·기능은 유지하고, 다른 영역은 현재 구성대로 둬.
```

**점검 전용 — 모바일 여정과 모션**

```text
/gx-design:gx-redesign 점검만. 쇼핑몰 메인 → 상품 상세 → 장바구니 여정을 모바일(375×812)에서 확인해줘. 진행을 막는 문제와 어색한 모션을 위치·관찰 근거·수정 방향으로 정리하고, 원본은 수정하지 마. 대상 https://shop.example.com
```

실제 클릭·화면 관측은 브라우저 도구가 있을 때 수행합니다. 실행 수단이 없으면 확인하지 못한 범위를 미검증으로 표시합니다. 모션 점검 결과는 `요소·위치 | Before(전) | After(후) | Why(이유)` 표로 정리합니다.

**브랜드 아이덴티티 — 가이드와 적용안**

```text
/gx-design:gx-design 동네 베이커리 브랜드 BX. 출근길 30대 직장인 단골 확보가 목적이야. 따뜻하고 경쾌한 톤으로 브랜드 가이드와 로고·패키지·간판 적용안을 만들고 싶어. 기존 상호는 유지해줘.
```

**영상 — 세로형 앱 소개**

```text
/gx-design:gx-design 신규 앱 출시를 알리는 15초 Instagram Reels. 20대 대상이고 목표는 앱 설치. 손글씨 키네틱 타이포 중심으로, 세로 9:16·30fps의 MP4가 필요해.
```

영상은 씬 길이, 텍스트 노출 시간, 전환, 플랫폼 안전영역을 기준으로 명세와 최종 파일을 확인합니다. UI 인터랙션과 영상에는 각각의 [모션 기준](skills/gx-design/MOTION.md)을 적용합니다.

## 진행 방식

1. **목표와 범위 확인** — 제공 자료와 기존 결정을 확인하고, 결과를 바꾸는 미정 조건을 정리합니다.
2. **필요한 조사와 방향 수립** — 기존 자료로 답이 난 조사는 생략합니다. 방향이 열려 있으면 대표안을 비교하고 선택된 방향을 확장합니다.
3. **요청한 결과물 제작** — 기존 브랜드 기준·기술 스택·컴포넌트를 반영하고, 지정한 형식과 범위에 맞게 제작합니다.
4. **최종 검토와 전달** — 목표·전략 일치와 완성도를 확인합니다. 기존 개선은 문제 해소와 변경으로 생긴 결함도 확인합니다.

기존 개선은 제작 전에 대상 자산과 보존 조건을 확인하고 읽기 전용 진단을 수행합니다. 변경은 진단 문제 또는 승인된 개선 목표에 연결하며, `변경 ID → before → after → 근거`로 추적합니다. 수정 후에는 같은 관찰 조건에서 전후 결과와 관련 기능을 비교하고, 재현할 수 없는 조건은 검증 한계로 기록합니다.

### 작업 범위와 사용자 판단

- **확정한 결정 재사용:** 이미 받은 브리프·방향·결과물 제작 승인은 재사용합니다. 범위가 바뀌면 영향을 받는 결정만 다시 확인합니다.
- **필수 답변 대기:** 결과를 바꾸는 필수 의도가 미정이면 답변을 기다립니다. 빈 응답·취소·시간 경과를 승인으로 처리하지 않습니다. 자료 확인 등 독립 작업은 계속할 수 있습니다.
- **점검과 수정 구분:** 점검 전용은 보고로 완료합니다. 이후 수정은 별도 요청이 있을 때 지정한 범위에서 진행합니다.
- **부분 수정 범위 유지:** 특정 영역이나 진단 ID만 요청하면 그 범위만 수정합니다. `D-02만 고쳐`를 다른 문제 전체의 수정으로 확대하지 않습니다.
- **방향 선택 후 확장:** 후보 탐색을 요청하면 대표 후보를 만든 뒤 선택을 기다립니다. 선택 전에 통합하거나 전체 결과물로 확장하지 않습니다.

구현 간격처럼 기존 기준 안에서 판단할 수 있는 세부 사항은 모두 질문으로 돌리지 않습니다. 선택적 취향을 지정하지 않아도 진행할 수 있으며, 필수 의도와 구분해 처리합니다.

## 적용 사례

인증 진행현황 조회 화면의 기존 개선 사례입니다. 어두운 대시보드에서 밝은 바탕의 조회 화면으로 정리하고, 조회 조건과 진행 목록을 구분했습니다. 이 사례는 현재 버전의 일반적인 품질 효과나 모든 업무 화면의 정답을 의미하지 않습니다.

| Before | After |
|---|---|
| ![개편 전 — 초록색 요약 카드와 알림이 있는 어두운 대시보드](site/assets/redesign-before-dark.png) | ![개편 후 — 밝은 바탕에서 조회 조건과 진행 목록을 구분한 화면](site/assets/redesign-after-light.png) |

## 요구사항과 선택 도구

Claude Code 또는 플러그인 명령과 스킬을 지원하는 Codex가 필요합니다. 기본 절차는 저장소의 스킬과 참조 문서를 사용합니다. 실행·렌더링·외부 도구 활용에는 해당 환경의 도구와 권한이 필요합니다.

| 선택 도구 | 용도와 조건 |
|---|---|
| pencil MCP | `.pen` 디자인 파일 열람·시안 제작. 실제 생성·내보내기 지원 여부 확인 필요 |
| 브라우저 도구 또는 기존 Playwright 환경 | 화면 캡처, 프로토타입 실행, 핵심 여정 클릭 검증 |
| frontend-design 스킬 | 사용 가능한 경우 UI 프로토타입 제작에 적용 |
| UI UX Pro Max + Python 3 | 설치되어 있고 실행 도구가 있을 때 색상·폰트·차트·UX·기술 스택 자료 검색 |
| Remotion·FFmpeg 등 렌더 환경 | 선택한 방식에 따른 MP4 제작. 미가용 시 다른 경로 안내 |

선택 도구와 외부 스킬을 자동 설치하거나 훅을 추가하지 않습니다. 브라우저 실행 검증은 실제 관측 수단이 있을 때 수행하며, 도구가 없거나 확인하지 못한 항목은 미검증으로 남깁니다. 디자인 자료 검색은 기존 브랜드 기준을 우선하고 `DESIGN.md`를 자동으로 덮어쓰지 않습니다.

<details>
<summary>Playwright MCP 설정 명령</summary>

Codex CLI:

```text
codex mcp add playwright -- npx @playwright/mcp@latest
```

설정 후 재시작합니다. Windows에서 `npx`가 해석되지 않으면 `npx.cmd`를 사용합니다.

Claude Code:

```text
claude mcp add playwright npx @playwright/mcp@latest
```

</details>

## FAQ

**기존 디자인이 Figma나 모바일 앱에만 있어도 점검할 수 있나요?**

화면 스크린샷, 접근 가능한 서비스 URL, 디자인 파일 경로 중 제공 가능한 자료를 사용합니다. 이미지 분석과 실제 실행 검증을 구분하며, 기억에 의한 설명만으로 진단하지 않습니다.

**기존 브랜드 컬러와 폰트를 유지하려면 어떻게 하나요?**

브랜드 가이드·팔레트·`DESIGN.md`를 제공하고 반드시 지켜야 할 기준인지 참고 방향인지 알려 주세요. 확정된 팔레트·타이포·톤을 제작과 검토에 반영합니다. 기준 자료가 없다면 새로 정할 수 있으며, [designmd.co](https://www.designmd.co/)나 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md)에서 고른 문서를 첨부할 수도 있습니다. 외부 카탈로그를 자동 연동하지는 않습니다.

**질문을 줄이고 나머지 디자인 판단을 맡길 수 있나요?**

“그만, 진행해”라고 명시하면 현재 설명한 범위 안의 디자인 판단을 위임한 것으로 기록하고, 미확정 사항은 근거와 함께 `[가정]`으로 남깁니다. 기존 금지·보존 조건을 유지하며 요청 범위나 실행 권한을 확대하지 않습니다. “그만” 또는 “멈춰”만 말하면 작업을 중단합니다. 질문 수에 일률적인 상한은 없으며, 판단을 위임하지 않은 필수 결정이 남으면 답변을 기다립니다.

**조사 없이 화면 명세나 특정 수정만 요청할 수 있나요?**

결과물·범위·기준이 확정되어 있으면 필요한 제작·검토로 진행합니다. 부분 수정에 전체 시장 조사나 여러 전략안을 강제하지 않습니다.

**Claude Code와 Codex의 작업 방식은 같은가요?**

같은 스킬 절차와 산출물 기준을 사용합니다. Claude Code의 이름 붙은 에이전트·모델·frontmatter 자동 로드는 Claude Code에만 적용됩니다. Codex는 현재 제공된 위임 도구와 프로젝트 지시에 따라 역할을 맡기며, 위임할 수 없으면 주 에이전트가 해당 절차를 수행합니다. 구조화 질문 도구가 없으면 일반 대화로 선택지를 제시하고 필요한 답변을 받습니다.

## 유지보수와 참고 문서

관리자: 구본승. 설치본 캐시, 호스트별 호환성, 검증·재설치 절차는 [두 호스트 유지보수 안내](docs/codex-skill-maintenance.md)에 정리되어 있습니다.

<details>
<summary>설치 확인·로컬 개발·업데이트·릴리스</summary>

### 설치 확인

Claude Code에서는 재시작 후 다음을 요청해 등록 상태를 확인합니다.

```text
현재 등록된 디자인 서브에이전트(design-researcher, design-strategist, creative-producer)와
스킬(gx-design, gx-redesign, design-research, design-strategy, creative-production, creative-review)을
역할·모델·도구·사전 로드 스킬 표로 확인해줘. 로드되지 않은 항목이 있으면 원인을 분석해줘.
```

Codex에서는 `codex plugin list`로 설치를 확인하고 새 대화의 스킬 목록에서 위 여섯 스킬을 확인합니다. `$gx-design` 또는 `$gx-redesign` 요청으로 브리프 질문·선택과 위임이 불가능할 때의 수행 절차를 확인합니다.

### 로컬 개발 설치

Claude Code에서는 `<repo-path>`를 현재 체크아웃의 절대 경로로 바꿉니다.

```text
/plugin marketplace add <repo-path>
/plugin install gx-design@gx-design
```

Codex에서는 저장소 루트에서 실행합니다.

```powershell
$repo = (Get-Location).Path
codex plugin marketplace add $repo
codex plugin add gx-design@gx-design
codex plugin list
```

### 수정 반영

Claude Code:

1. `.claude-plugin/plugin.json`의 `version`을 올립니다.
2. `claude plugin marketplace update gx-design`
3. `claude plugin update gx-design@gx-design`
4. Claude Code를 재시작합니다.

Codex는 `.codex-plugin/plugin.json`의 기본 버전을 Claude 매니페스트와 맞춥니다. 같은 기본 버전에서 로컬 캐시를 갱신할 때는 유지보수 안내의 `+codex.<cachebuster>` 절차를 사용합니다. 테스트와 플러그인 검증기를 실행한 뒤 재설치합니다.

### 릴리스

main 직접 커밋은 훅이 차단하므로 변경은 작업 브랜치에서 커밋 후 main에 병합합니다.

1. `claude plugin tag .` — `gx-design--v{version}` 태그 생성과 매니페스트 정합성 검증
2. `git push origin main --tags`
3. `gh release create gx-design--v{version}`

</details>

<details>
<summary>내부 구성과 실행 설정</summary>

일반적인 진입점은 `gx-design`과 `gx-redesign`입니다. 나머지 스킬은 해당 단계의 방법론과 산출물 기준으로 사용합니다.

| 종류 | 이름 | 역할 |
|---|---|---|
| 스킬 | `gx-design` | 신규 디자인의 목표 확인·기획·제작·검토 |
| 스킬 | `gx-redesign` | 기존 결과물 진단·개선·점검 전용 요청 |
| 스킬 | `design-research` | 시장·사용자·경쟁사·사례 조사 |
| 스킬 | `design-strategy` | 문제 정의·전략·디자인 방향 수립 |
| 스킬 | `creative-production` | 명세·카피·프롬프트·프로토타입 제작 |
| 스킬 | `creative-review` | 전략 일치·완성도·개선 결과 검토 |
| Claude Code 전용 에이전트 | `design-researcher` (haiku) | 조사 역할 |
| Claude Code 전용 에이전트 | `design-strategist` (sonnet) | 전략 역할 |
| Claude Code 전용 에이전트 | `creative-producer` (sonnet) | 제작 역할 |

Codex는 Claude 전용 에이전트 파일의 모델·스킬 자동 주입을 전제하지 않습니다.

- **진행 깊이:** 기본은 핵심 모드이며 명시한 모드를 존중합니다. 필요한 근거·범위·위험이 확인되면 해당 단계만 전체 수준으로 확장합니다. 필수 결정 확인과 품질 기준은 공통입니다.
- **방향 비교:** 방향이 열린 핵심 모드에서는 추천 스케치 1안과 필요할 때 비교 1안을 제시합니다. 전체 모드나 명시적인 3안 요청에서는 서로 다른 3안을 비교합니다. 확정한 방향은 다시 선택하지 않습니다.
- **수정 예산:** 제작 중 다듬기와 검토 후 수정을 합쳐 기본 총 3회입니다. 관찰·판정은 최소 한 번 수행하고 문제가 발견되면 수정합니다. 예산을 소진해도 미달 결과를 통과시키지 않습니다.
- **실행량 기록:** 위임·외부 열람·렌더·호스트가 제공한 토큰을 상세 기록에 남깁니다. 사용자 보고는 주요 결정·변경·남은 문제를 우선합니다. 기준은 [RUN-BUDGET.md](skills/gx-design/RUN-BUDGET.md)를 따릅니다.

세부 참조는 현재 매체와 단계에 필요할 때 읽습니다. 단순 점검·부분 수정에는 관련 자산과 규칙부터 적용하며, 유효한 기존 근거와 결정을 재사용합니다. 실제 소요시간은 작업 규모와 실행 환경에 따라 달라집니다.

</details>

<details>
<summary>설계·제작·검토 기준과 조사 근거</summary>

| 문서 | 내용 |
|---|---|
| [BRIEF-INTERVIEW.md](skills/gx-design/BRIEF-INTERVIEW.md) · [HOST-COMPAT.md](skills/gx-design/HOST-COMPAT.md) | 의도 확인, 답변 대기, 승인 재사용과 호스트 호환성 |
| [REDESIGN-INTERVIEW.md](skills/gx-redesign/REDESIGN-INTERVIEW.md) | 기존 자산 인벤토리와 개선 범위 확인 |
| [DESIGN-IT-TWICE.md](skills/gx-design/DESIGN-IT-TWICE.md) | 방향 비교와 선택 후 확장 |
| [REVIEW-AXES.md](skills/gx-design/REVIEW-AXES.md) | 신규 제작의 2축·기존 개선의 3축 검토, 최종 버전 근거 |
| [PRODUCTION-HANDOFF.md](skills/gx-design/PRODUCTION-HANDOFF.md) | 결과물·제작 경로와 완료 상태 구분 |
| [PROMPT-PLAYBOOK.md](skills/gx-design/PROMPT-PLAYBOOK.md) | 생성형 이미지·영상 프롬프트 규격 |
| [DESIGN-TONE-ANCHOR.md](skills/gx-design/DESIGN-TONE-ANCHOR.md) | `DESIGN.md`·브랜드 기준 적용 |
| [UI-QUALITY.md](skills/gx-design/UI-QUALITY.md) · [DESIGN-JUDGMENT.md](skills/gx-design/DESIGN-JUDGMENT.md) | 화면 목적·핵심 과업·정보 우선순위·문구·예외 상태 |
| [VISUAL-QUALITY.md](skills/gx-design/VISUAL-QUALITY.md) | 렌더 결과 관찰, 실행 검증 로그와 시각 품질 검토 |
| [VISUAL-CRAFT.md](skills/gx-design/VISUAL-CRAFT.md) · [ANTI-TELL-CHECKLIST.md](skills/gx-design/ANTI-TELL-CHECKLIST.md) | 시각적 일관성, 요소·카피·구조 점검 |
| [MOTION.md](skills/gx-design/MOTION.md) | UI 인터랙션, 영상·모션 그래픽, 모션 점검 표 |
| [REFERENCE-DRIVEN.md](skills/gx-design/REFERENCE-DRIVEN.md) | 참고 이미지·영상 활용과 타인 자산 재현 방지 |
| [DESIGN-INTELLIGENCE.md](skills/gx-design/DESIGN-INTELLIGENCE.md) | 선택적 디자인 자료 검색과 적합성 검토 |
| [PRODUCT-SCENES.md](skills/gx-design/PRODUCT-SCENES.md) | 제품 소개 장면과 실제 동작 UI 구분 |
| [OBSERVATION.md](skills/gx-design/references/OBSERVATION.md) | 읽기 전용 화면 구조 관측과 목록·폼 대조 예제 |

제품 소개 장면에서는 Stageshow 예제·촬영, Agentation의 위치 피드백, DialKit의 값 비교를 기존 설치와 권한이 있을 때 선택적으로 활용합니다. 화면 구조 관측 함수는 자체 작성했으며 Swarm Rebuild 소스를 재사용하지 않았습니다. 관측 요약은 디자인 토큰의 정본이나 기능·접근성 통과를 대신하지 않습니다.

디자인 판단 관점의 해설은 [마디아의 디자인 판단 관점과 활용법](docs/design/madia-design-perspective.md), 출처·적용 조건은 [근거 지도](skills/gx-design/references/madia-evidence.md), 조사 범위·미확인 목록은 [조사 기록](docs/research/2026-10-15-madia-design-judgment.md)에 있습니다. 공개 설명·챕터·전사 일부를 바탕으로 구성했으며 전편 시청 분석을 의미하지 않습니다. 두 호스트에서 같은 문서 기준을 사용하고 외부 영상 서비스의 실시간 접근을 전제하지 않습니다.

초기 설계 배경은 [디자인 멀티에이전트 팀 구축 가이드](디자인-멀티에이전트-팀-구축-가이드.md)와 [스킬 설계안](design-team-스킬-설계안.md)을 참고하세요.

</details>

<details>
<summary>외부 규칙 출처와 라이선스</summary>

다음 지침을 gx-design의 단계별 규칙에 재구성해 적용했습니다. 기본 규칙 사용에 외부 스킬 설치는 필요하지 않으며, 실제 실행 도구는 가용할 때 사용합니다.

시각 제작 기준은 Anthropic 공식 frontend-design 원칙과 커뮤니티 taste·animate·impeccable 규칙을 선택적으로 재서술한 내용을 포함합니다. 적용 근거는 [VISUAL-CRAFT.md](skills/gx-design/VISUAL-CRAFT.md)에 정리되어 있습니다.

| 출처 | 적용 범위 | 라이선스 |
|---|---|---|
| [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | `DESIGN.md` 형식과 디자인 톤 기준 매핑 | MIT |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `taste-skill-v2-experimental`·`high-end-visual-design`의 시각 표현·움직임·정보 밀도 기준 | MIT |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 읽기 전용 진단, 시각·UX 검토와 구현 점검 구분, 문구·예외 상태, 선택적 detect CLI 검사 | Apache-2.0 |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | UI 인터랙션의 빈도·이징·지속시간·press·reduced-motion | MIT |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | 가용할 때 화면·핵심 여정 실제 실행 검증 | Apache-2.0 |

영상·모션 그래픽의 프레임 검산, 텍스트 노출 시간, 전환 체계, 안전영역은 [MOTION.md](skills/gx-design/MOTION.md) §B의 자체 규칙입니다.

</details>

<details>
<summary>평가 세트</summary>

모드·버전별 비용(토큰·턴·도구 호출)과 품질을 실행 기록으로 비교하는 평가 세트가 `evals/`에 있습니다. 시나리오, Codex 비대화 실행 러너, 집계 스크립트, 채점표로 구성됩니다. 실제 모델 호출 비용이 발생하므로 실행 방법·격리 설정·해석 주의는 [evals/README.md](evals/README.md)를 먼저 확인하세요. 평가 도구의 존재만으로 실제 디자인 품질이나 두 호스트의 동작을 보증하지 않습니다.

</details>
