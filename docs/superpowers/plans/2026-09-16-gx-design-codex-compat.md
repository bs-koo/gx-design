# gx-design Codex Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `gx-design` 0.8.0을 Claude Code와 Codex에서 같은 스킬 흐름으로 설치·실행하고, 이후 스킬 수정 시 두 호스트의 호환을 검증하는 참고문서와 검사를 남긴다.

**Architecture:** 기존 `.claude-plugin/marketplace.json`과 6개 스킬을 재사용하고 `.codex-plugin/plugin.json`만 추가한다. 실행 시 필요한 호스트 차이는 `HOST-COMPAT.md`에 모으고, 오케스트레이터와 질문 참조 파일은 실제 제공된 도구로 동작하도록 고친다. 전문가 절차는 기존 방법론 스킬에 넣어 Claude 에이전트 frontmatter 없이도 실행되게 한다.

**Tech Stack:** Markdown/YAML frontmatter, JSON 매니페스트, Python 표준 라이브러리 `unittest`, Codex CLI/Claude Code CLI.

**Spec:** `docs/superpowers/specs/2026-09-16-gx-design-codex-compat-design.md`

## Global Constraints

- 현재 Claude 플러그인 `name`은 `gx-design`, `version`은 `0.8.0`이다. Codex 매니페스트도 같은 이름·기본 버전을 사용한다. 로컬 재설치용 `+codex.<cachebuster>` 접미사는 허용한다.
- 기존 `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `agents/*.md`, 6개 스킬 이름과 디자인 산출물 형식을 보존한다.
- 이번 범위는 저장소 기반 로컬 설치·실행이다. 공개 디렉터리 제출, 새 MCP·생성 의존성, 저장소 재배치는 포함하지 않는다.
- Python 표준 라이브러리 외의 새 테스트 의존성을 추가하지 않는다.
- 호스트의 실제 질문·서브에이전트 도구 제한을 확인한다. 특정 도구 이름·문항 수·멀티선택·preview 기능을 공통 필수 조건으로 쓰지 않는다.
- 각 변경을 실행하기 전에 기존 미추적 파일을 건드리지 않는다. 커밋에는 이 계획의 파일만 명시적으로 추가한다.
- 실행할 때 저장소가 별도 작업 공간을 요구하면 `superpowers:using-git-worktrees` 절차를 적용한다. 이 계획은 작업 공간을 직접 만들지 않는다.

---

## 파일 구조

| 파일 | 책임 |
|---|---|
| `.codex-plugin/plugin.json` | Codex 플러그인 식별·표시 메타데이터 |
| `tests/test_codex_compat.py` | 매니페스트·스킬·참조·호스트 의존 회귀 검사 |
| `skills/gx-design/HOST-COMPAT.md` | 질문·위임·도구 가용성의 공통 실행 규칙 |
| `skills/gx-design/SKILL.md`, `skills/gx-redesign/SKILL.md` | 두 파이프라인의 역할 기반 실행 |
| `skills/gx-design/BRIEF-INTERVIEW.md`, `DESIGN-IT-TWICE.md`, `DESIGN-TONE-ANCHOR.md`, `REVIEW-AXES.md`, `PRODUCTION-HANDOFF.md`, `VISUAL-QUALITY.md`, `skills/gx-redesign/REDESIGN-INTERVIEW.md` | 입력·선택·검수 게이트의 호스트 중립 절차 |
| `skills/design-research/SKILL.md`, `skills/design-strategy/SKILL.md`, `skills/creative-production/SKILL.md` | Claude 에이전트 없이도 읽을 수 있는 전문가 계약 |
| `docs/codex-skill-maintenance.md`, `README.md` | 추후 수정·설치·검증 안내 |

### Task 1: Codex 매니페스트와 메타데이터 계약

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `tests/test_codex_compat.py`
- Read: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: Claude 매니페스트의 `name: str`, `version: str`, `description: str`, `author.name: str`.
- Produces: Codex 매니페스트 `name: str`, `version: str`, `description: str`, `skills: str`, `interface: object`; 이후 태스크의 검사 모듈 `tests/test_codex_compat.py`.

- [ ] **Step 1: 실패하는 매니페스트 검사를 작성한다**

`tests/test_codex_compat.py`를 다음 내용으로 만든다.

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {
    "gx-design", "gx-redesign", "design-research",
    "design-strategy", "creative-production", "creative-review",
}


class CodexCompatibilityTests(unittest.TestCase):
    def test_codex_manifest_matches_claude_identity(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["version"].split("+", 1)[0], claude["version"])
        self.assertEqual(codex["author"]["name"], claude["author"]["name"])
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue(codex["description"].strip())
        self.assertEqual(set(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")), SKILL_NAMES)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 검사가 예상대로 실패하는지 확인한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: `.codex-plugin/plugin.json`이 없어 `FileNotFoundError`로 FAIL.

- [ ] **Step 3: 최소 Codex 매니페스트를 작성한다**

`.codex-plugin/plugin.json`은 다음 내용을 사용한다. `description`과 `author.name`은 기존 Claude 매니페스트와 뜻을 맞추고 정확한 문자열은 Step 4에서 비교한다.

```json
{
  "name": "gx-design",
  "version": "0.8.0",
  "description": "BX·그래픽·UX/UI·영상 디자인의 브리프, 리서치, 전략, 제작, 검수를 돕는 스킬 패키지",
  "author": { "name": "구본승" },
  "skills": "./skills/",
  "interface": {
    "displayName": "GX Design",
    "shortDescription": "디자인 브리프부터 제작·검수까지",
    "longDescription": "신규 디자인과 리디자인을 위한 조사, 전략, 제작, 검수 워크플로",
    "developerName": "구본승",
    "category": "Productivity",
    "capabilities": ["Read", "Write"]
  }
}
```

- [ ] **Step 4: 검사와 공식 검증기를 실행한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: PASS.

Run: `python C:/Users/SQI/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py D:/SQ/design-plugin`
Expected: 매니페스트 오류 없이 종료. 로컬 환경의 validator 위치가 달라지면 `$plugin-creator`의 `scripts/validate_plugin.py`를 사용한다.

- [ ] **Step 5: 이 태스크 파일만 커밋한다**

```powershell
git -c safe.directory=D:/SQ/design-plugin add -- .codex-plugin/plugin.json tests/test_codex_compat.py
git -c safe.directory=D:/SQ/design-plugin commit -m "feat: add Codex compatibility manifest"
```

### Task 2: 질문·선택 게이트를 호스트 중립으로 만든다

**Files:**
- Create: `skills/gx-design/HOST-COMPAT.md`
- Modify: `skills/gx-design/SKILL.md`, `BRIEF-INTERVIEW.md`, `DESIGN-IT-TWICE.md`, `DESIGN-TONE-ANCHOR.md`, `PRODUCTION-HANDOFF.md`, `VISUAL-QUALITY.md`
- Modify: `skills/gx-redesign/SKILL.md`, `REDESIGN-INTERVIEW.md`
- Modify: `tests/test_codex_compat.py`

**Interfaces:**
- Consumes: Task 1의 `ROOT: pathlib.Path`, `CodexCompatibilityTests`.
- Produces: `HOST-COMPAT.md`의 `질문·선택`, `답변 게이트`, `위임`, `도구 가용성` 4절; 두 오케스트레이터가 Task 3에서 읽을 공통 계약.

- [ ] **Step 1: Claude 전용 입력 호출의 재발 검사를 추가한다**

`tests/test_codex_compat.py`의 `CodexCompatibilityTests`에 다음 메서드를 추가한다.

```python
    def test_active_skills_do_not_require_claude_question_tool(self):
        for path in (ROOT / "skills").rglob("*.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("AskUserQuestion", content)
                self.assertNotIn("multiSelect", content)
                self.assertNotIn("preview를 쓴다", content)
                self.assertNotIn("WebSearch", content)
                self.assertNotIn("WebFetch", content)
                self.assertNotIn("Read로", content)

    def test_host_contract_is_present(self):
        host = (ROOT / "skills/gx-design/HOST-COMPAT.md").read_text(encoding="utf-8")
        for section in ("질문·선택", "답변 게이트", "위임", "도구 가용성"):
            self.assertIn(section, host)
```

- [ ] **Step 2: 새 검사가 예상대로 실패하는지 확인한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: 기존 `AskUserQuestion` 참조와 `HOST-COMPAT.md` 부재 때문에 FAIL.

- [ ] **Step 3: 호스트 공통 계약을 작성한다**

`skills/gx-design/HOST-COMPAT.md`를 다음 내용으로 만든다.

```markdown
# 호스트 호환 실행 규칙

## 질문·선택

실제 제공된 구조화 입력 도구가 있으면 그 도구의 문항 수·옵션 수·선택 방식 제한에 맞춰 질문한다. 한 라운드의 질문이 상한을 넘으면 나눠서 묻는다. 멀티선택이나 시각 미리보기가 없으면 선택지를 대화에 쓰고 답변을 기다린다. 사용자가 이미 결정을 명시했으면 같은 질문을 반복하지 않는다.

## 답변 게이트

브리프의 핵심 결정, 전략안 선택, 실물 제작 경로처럼 사용자 결정이 있어야 결과가 달라지는 단계는 답변을 받은 후 진행한다. 이미 받은 승인·선택은 유지한다. 결정을 묻기 전까지는 파일 조사와 문서 정리 등 독립 작업을 진행한다. 사용자가 명시적으로 "진행해"라고 한 경우 미해소 항목은 [가정]으로 기록한다.

## 위임

사용자·프로젝트 지시가 허용하고 실제 서브에이전트 도구가 있으면 역할, 입력 11항목, 저장 경로, 완료 기준을 명시해 위임한다. 특정 에이전트 이름·모델·스킬 자동 주입을 전제하지 않는다. 위임할 수 없으면 주 에이전트가 해당 방법론 스킬을 읽고 같은 절차·산출물 계약을 수행한다.

## 도구 가용성

파일 탐색, 웹 조사, 이미지 열기, 렌더링은 현재 환경의 실제 도구를 확인해 수행한다. 웹이나 렌더 도구가 없으면 확인하지 못한 사실과 만들지 못한 실물을 명시하고 가능한 문서·프롬프트 경로를 수행한다. 의존성 설치나 외부 서비스 이용은 사용자 지시와 실행 환경의 권한을 따른다.
```

- [ ] **Step 4: 질문 참조 파일의 실행 문장을 바꾼다**

기존 질문 구조와 게이트의 뜻은 유지하며 아래 문장으로 교체한다. 코드 블록은 각 파일에 넣을 실제 문장이다.

```markdown
<!-- skills/gx-design/BRIEF-INTERVIEW.md §4와 §7 -->
### 4. 라운드 실행 — 호스트의 질문 수단
[HOST-COMPAT.md](HOST-COMPAT.md) §질문·선택을 따른다. 한 라운드는 지금 물을 수 있는 frontier 전체다. 제공된 질문 도구의 상한을 넘으면 분할해 묻고, 도구가 없으면 대화로 질문한다. 첫 선택지는 추천안과 근거를 함께 쓴다. 복수 선택이 필요한 질문은 복수 답변이 가능함을 문장으로 밝힌다.
frontier가 비면 브리프 전문을 제시하고 [HOST-COMPAT.md](HOST-COMPAT.md) §답변 게이트에 따라 승인 또는 수정 답변을 받는다.
프로젝트 지시는 `CLAUDE.md`, `AGENTS.md`, `context/` 중 존재하는 파일을 확인한다.
공개 정보는 사용 가능한 웹 조사 수단으로 확인한다. 웹 접근이 없으면 확인하지 못한 사실을 표시한다.

<!-- skills/gx-design/DESIGN-IT-TWICE.md 선택 절 -->
각 안과 추천 근거를 보여 준 뒤 [HOST-COMPAT.md](HOST-COMPAT.md) §질문·선택으로 전략안을 선택받는다. 이미 선택한 안이 있으면 다시 묻지 않는다.

<!-- skills/gx-design/DESIGN-TONE-ANCHOR.md 강도 결정 절 -->
톤 기준의 강도는 [HOST-COMPAT.md](HOST-COMPAT.md) §질문·선택으로 한 번 확정한다. 구속/참고 중 추천안과 근거를 먼저 제시한다.

<!-- skills/gx-design/PRODUCTION-HANDOFF.md 질문 절 -->
실물 제작 여부와 경로는 [HOST-COMPAT.md](HOST-COMPAT.md) §답변 게이트로 선택받는다. 복수 경로가 가능하면 그 사실을 밝힌다. 지원되지 않는 입력 기능을 전제하지 않는다.

<!-- skills/gx-redesign/REDESIGN-INTERVIEW.md 질문 절 -->
브리프 질문·승인은 [../gx-design/HOST-COMPAT.md](../gx-design/HOST-COMPAT.md) §질문·선택과 §답변 게이트를 따른다. 개선 자산 인벤토리와 기존 브리프 절차는 유지한다.
배포 화면은 사용 가능한 브라우저·웹 조사 수단으로 확인하고, 문서·이미지는 현재 환경의 파일 읽기·이미지 보기 수단으로 직접 확인한다.

<!-- skills/gx-design/VISUAL-QUALITY.md 시각 비평 절 -->
렌더 이미지는 현재 환경의 이미지 보기 수단으로 직접 열어 보고 비평한다. 파일 내용만 읽거나 명세 값만 대조하지 않는다.

<!-- skills/gx-design/SKILL.md와 skills/gx-redesign/SKILL.md 질문 절 -->
전략 선택과 실물 제작 경로는 HOST-COMPAT.md의 질문·선택과 답변 게이트를 따른다. 이미 사용자가 선택한 경로는 다시 묻지 않는다.
```

`rg -n 'AskUserQuestion|multiSelect|preview' skills`로 남은 위치를 확인해 위 공통 규칙에 맞춰 모든 활성 스킬 문장을 정리한다. Claude 전용 도구를 설명하는 주석도 런타임 파일에는 남기지 않는다.

- [ ] **Step 5: 새 검사가 통과하는지 확인한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: PASS. 실패가 질문 문장에 남은 Claude 전용 토큰이면 해당 문장만 정리하고 같은 명령을 다시 실행한다.

- [ ] **Step 6: 이 태스크 파일만 커밋한다**

```powershell
git -c safe.directory=D:/SQ/design-plugin add -- skills/gx-design/HOST-COMPAT.md skills/gx-design/SKILL.md skills/gx-design/BRIEF-INTERVIEW.md skills/gx-design/DESIGN-IT-TWICE.md skills/gx-design/DESIGN-TONE-ANCHOR.md skills/gx-design/PRODUCTION-HANDOFF.md skills/gx-design/VISUAL-QUALITY.md skills/gx-redesign/SKILL.md skills/gx-redesign/REDESIGN-INTERVIEW.md tests/test_codex_compat.py
git -c safe.directory=D:/SQ/design-plugin commit -m "feat: make design decision gates host-compatible"
```

### Task 3: 전문가 역할과 두 오케스트레이터의 위임 폴백

**Files:**
- Modify: `skills/design-research/SKILL.md`, `skills/design-strategy/SKILL.md`, `skills/creative-production/SKILL.md`
- Modify: `skills/gx-design/SKILL.md`, `skills/gx-redesign/SKILL.md`, `skills/gx-design/REVIEW-AXES.md`
- Modify: `tests/test_codex_compat.py`
- Read: `agents/design-researcher.md`, `agents/design-strategist.md`, `agents/creative-producer.md`

**Interfaces:**
- Consumes: Task 2의 `HOST-COMPAT.md` §위임, 기존 전문가 방법론 스킬의 산출물 형식.
- Produces: 이름이 고정된 Claude 에이전트를 사용하지 않아도 역할을 수행할 수 있는 3개 스킬 계약과 신규/개선 오케스트레이터의 위임 폴백.

- [ ] **Step 1: 필수 위임 전제의 회귀 검사를 작성한다**

`CodexCompatibilityTests`에 다음 메서드를 추가한다.

```python
    def test_orchestrators_link_host_contract_and_specialist_skills(self):
        for name in ("gx-design", "gx-redesign"):
            text = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("HOST-COMPAT.md", text)
            self.assertIn("design-research", text)
            self.assertIn("design-strategy", text)
            self.assertIn("creative-production", text)
            self.assertIn("위임할 수 없", text)

    def test_specialist_skills_define_role_contract(self):
        for name in ("design-research", "design-strategy", "creative-production"):
            text = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("## 역할과 산출물 계약", text)
```

- [ ] **Step 2: 새 검사가 예상대로 실패하는지 확인한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: 세 스킬의 역할 계약과 오케스트레이터 폴백이 없어서 FAIL.

- [ ] **Step 3: 전문가 스킬에 역할 계약을 넣는다**

각 파일의 기존 절차·품질 체크는 그대로 두고 다음 절을 추가한다. `agents/*.md`의 `model`, `tools`, `skills`, `memory` frontmatter는 복사하지 않는다.

```markdown
<!-- skills/design-research/SKILL.md -->
## 역할과 산출물 계약
디자인 리서치 역할은 시장·사용자·경쟁사·사례 중 브리프와 직접 관련된 축을 조사한다. 입력은 목표·타깃·조사 질문·자료 경로·저장 경로·완료 기준이다. 출력은 출처와 조사 날짜, 사실/해석 구분, 공통 패턴과 차이, 전략 질문이 포함된 `outputs/research/` 리포트다. 웹 접근이 없으면 검증하지 못한 최신 정보와 근거 한계를 표시한다.

<!-- skills/design-strategy/SKILL.md -->
## 역할과 산출물 계약
디자인 전략 역할은 승인된 브리프와 리서치를 문제 정의·가치 제안·콘셉트·매체별 실행 방향으로 바꾼다. 입력은 브리프·리서치 경로·톤 기준·저장 경로·완료 기준이다. 출력은 근거와 실제 디자인 선택을 연결하고 대안의 차이와 리스크를 설명하는 `outputs/strategy/` 문서다. 사용자 선택 전에는 제안을 확정 전략으로 쓰지 않는다.

<!-- skills/creative-production/SKILL.md -->
## 역할과 산출물 계약
디자인 제작 역할은 선택된 전략을 매체별 필수 섹션, 수치, 카피, 화면·씬 구조, 필요 시 프로토타입으로 구체화한다. 입력은 브리프·선택 전략·리서치·톤 기준·참조 파일·저장 경로·완료 기준이다. 출력은 자체 검수와 수용 체크가 포함된 `outputs/production/` 산출물이다. 코드를 제작하면 구조·실행·렌더 결과를 확인한다.
```

- [ ] **Step 4: 오케스트레이터의 고정 이름 스폰 지시를 역할 기반으로 교체한다**

두 `SKILL.md`의 시작 부분에 `HOST-COMPAT.md` 참조를 넣고, 해당 단계의 위임 문장을 다음 계약으로 바꾼다. 기존 단계 순서·완료 기준·모드별 분량은 그대로 유지한다.

```markdown
실행 전 [HOST-COMPAT.md](HOST-COMPAT.md)의 질문·위임·도구 가용성 규칙을 읽는다.
조사는 design-research 스킬의 역할과 산출물 계약을 따른다. 위임이 허용되고 서브에이전트 도구가 있으면 조사 축과 입력 11항목을 전달한다. 위임할 수 없으면 주 에이전트가 design-research를 읽고 조사한다.
전략은 design-strategy 스킬의 역할과 산출물 계약을 따른다. 위임할 수 없으면 주 에이전트가 대안을 작성하고 사용자 선택을 받는다.
제작은 creative-production 스킬의 역할과 산출물 계약을 따른다. 위임할 수 없으면 주 에이전트가 선택된 전략과 참조 파일을 읽고 제작한다.
```

`gx-redesign/SKILL.md`의 링크는 `../gx-design/HOST-COMPAT.md`로 쓴다. `REVIEW-AXES.md`의 병렬 스폰 문장은 다음 문장으로 교체한다.

```markdown
전체 모드에서 위임이 허용되고 서브에이전트 도구가 있으면 전략 일치(축 A)와 완성도(축 B)를 분리해 병렬 검수한다. 위임할 수 없으면 주 에이전트가 creative-review 스킬을 읽고 축 A와 축 B를 순서대로 각각 기록한다. 두 보고를 합쳐 결함을 가리지 않는다.
```

개선 흐름의 축 C도 같은 위임/순차 폴백으로 처리한다. `agents/*.md`는 수정하지 않는다.

- [ ] **Step 5: 검사와 링크 확인을 실행한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: PASS.

Run: `rg -n 'design-researcher 서브에이전트|design-strategist 서브에이전트|creative-producer 서브에이전트|병렬 스폰한다' skills/gx-design skills/gx-redesign`
Expected: 필수 고정 에이전트 호출이 남지 않는다. 발견된 위치는 역할 계약과 폴백 문장으로 바꾼다.

- [ ] **Step 6: 이 태스크 파일만 커밋한다**

```powershell
git -c safe.directory=D:/SQ/design-plugin add -- skills/design-research/SKILL.md skills/design-strategy/SKILL.md skills/creative-production/SKILL.md skills/gx-design/SKILL.md skills/gx-redesign/SKILL.md skills/gx-design/REVIEW-AXES.md tests/test_codex_compat.py
git -c safe.directory=D:/SQ/design-plugin commit -m "feat: make design roles runnable without Claude agents"
```

### Task 4: 참조 링크·수정 참고문서·설치 검증

**Files:**
- Create: `docs/codex-skill-maintenance.md`
- Modify: `README.md`, `tests/test_codex_compat.py`
- Read: `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, all `skills/**/*.md`

**Interfaces:**
- Consumes: Task 1~3의 매니페스트, 질문·위임 계약, 6개 스킬.
- Produces: 유지보수 절차와 전체 검사 `python -m unittest discover -s tests -v`; 로컬 설치 확인 결과.

- [ ] **Step 1: 참조 링크 검사를 먼저 작성한다**

`tests/test_codex_compat.py`에 `import re`를 추가하고 다음 메서드를 `CodexCompatibilityTests`에 넣는다.

```python
    def test_local_skill_links_resolve(self):
        for path in (ROOT / "skills").rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", content):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                with self.subTest(source=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target).exists())
```

- [ ] **Step 2: 검사 결과를 확인한다**

Run: `python -m unittest tests/test_codex_compat.py -v`
Expected: 깨진 상대 링크가 있으면 FAIL; 해당 링크를 실제 파일로 고친다. 깨진 링크가 없으면 PASS이며 Step 3으로 간다.

- [ ] **Step 3: 스킬 수정 참고문서를 작성한다**

`docs/codex-skill-maintenance.md`에 다음 내용을 작성한다. 공통 변경 순서와 파일·명령을 유지한다.

```markdown
# gx-design 스킬 수정 시 Claude Code·Codex 호환 참고

## 수정 순서
1. 변경할 `skills/<name>/SKILL.md`의 `name`·`description`과 참조 파일을 확인한다. 새 스킬은 `skills/<name>/SKILL.md`에 두고 두 호스트에서 자동 발견되는지 검사한다.
2. 질문·승인·선택 문장을 수정하면 `skills/gx-design/HOST-COMPAT.md`를 따른다. `AskUserQuestion`의 호출 제한, `multiSelect`, `preview`를 필수 전제로 쓰지 않는다. 실제 입력 도구가 없으면 대화로 결정받는다.
3. 위임 문장을 수정하면 역할·입력 11항목·산출물 경로·완료 기준과 주 에이전트 폴백을 함께 확인한다. Claude의 `agents/*.md`는 Claude 전용 설정이며 Codex가 자동 로드한다고 가정하지 않는다.
4. 방법론을 바꾸면 해당 전문가 스킬과 두 오케스트레이터의 참조를 함께 확인한다. 디자인 단계·브리프/전략/실물 선택의 의미를 유지한다.
5. 배포 버전을 바꾸면 `.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json`의 `name`·기본 `version`을 맞춘다. Codex 매니페스트의 `+codex.<cachebuster>` 접미사는 로컬 재설치용이며 기본 버전과 별도로 관리한다.

## 검사 명령
`python -m unittest discover -s tests -v`
`python C:/Users/SQI/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py D:/SQ/design-plugin`
`rg -n 'AskUserQuestion|multiSelect|preview|WebSearch|WebFetch|Read로|model: haiku|model: sonnet' skills`
`git diff --check`

## 로컬 설치와 갱신
새 `CODEX_HOME`을 `D:/Temp` 아래에 지정해 기존 설치를 분리한 뒤 `codex plugin marketplace add D:/SQ/design-plugin --json`, `codex plugin add gx-design@gx-design --json`, `codex plugin list`를 실행한다. 실제 사용자 환경에서 업데이트할 때는 `python C:/Users/SQI/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path D:/SQ/design-plugin/.claude-plugin/marketplace.json`으로 이름을 확인하고 `python C:/Users/SQI/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py D:/SQ/design-plugin`으로 Codex 매니페스트의 접미사를 갱신한다. `python -m unittest discover -s tests -v`로 기본 버전 동기화를 확인한 뒤 `codex plugin add gx-design@gx-design`을 실행하고 새 대화에서 스킬 목록과 신규/개선 대표 요청을 확인한다. Claude Code는 기존 `/plugin marketplace add`와 `/plugin install gx-design@gx-design` 경로를 확인한다.

## 대표 시나리오
- 신규: `$gx-design 단일 화면의 새 UX/UI 디자인, 핵심 모드` → 브리프 질문·전략 선택·제작·2축 검수.
- 개선: `$gx-redesign 기존 랜딩 화면 개선, 핵심 모드` → 자산 인벤토리·개선 브리프·before/after·3축 검수.
- 서브에이전트 도구가 없는 세션: 같은 두 요청에서 주 에이전트 폴백이 완료 기준을 유지하는지 확인한다.

## 근거
- [OpenAI Claude 플러그인 전환 안내](https://developers.openai.com/plugins/guides/submit-claude-plugin)
- [OpenAI Codex 플러그인 안내](https://learn.chatgpt.com/docs/build-plugins)
- [OpenAI Codex 스킬 안내](https://learn.chatgpt.com/docs/build-skills)
- [OpenAI 마켓플레이스 지원 형식](https://learn.chatgpt.com/docs/enterprise/plugin-management)
```

- [ ] **Step 4: README에 Codex 설치·수정 안내를 추가한다**

기존 Claude 설치 절은 유지하고 다음 절을 추가한다.

````markdown
## Codex에서 사용

로컬 저장소를 마켓플레이스로 등록하고 플러그인을 설치한다.

```powershell
codex plugin marketplace add D:/SQ/design-plugin
codex plugin add gx-design@gx-design
```

새 대화에서 `$gx-design` 또는 `$gx-redesign`을 호출한다. 스킬 수정·버전 동기화·재설치 검증은 [Codex 호환 수정 참고](docs/codex-skill-maintenance.md)를 따른다.
````

- [ ] **Step 5: 자동 검사와 로컬 Codex 설치를 검증한다**

Run: `python -m unittest discover -s tests -v`
Expected: PASS.

Run: `git -c safe.directory=D:/SQ/design-plugin diff --check`
Expected: 출력 없음.

Run: `python C:/Users/SQI/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py D:/SQ/design-plugin`
Expected: PASS.

분리된 테스트 홈에서 다음 PowerShell 명령을 순서대로 실행한다. 로컬 마켓플레이스 소스이므로 네트워크를 요구하지 않는다.

```powershell
$env:CODEX_HOME = 'D:/Temp/gx-design-codex-smoke'
codex.cmd plugin marketplace add D:/SQ/design-plugin --json
codex.cmd plugin add gx-design@gx-design --json
codex.cmd plugin list
```

Expected: `codex plugin list`에 `gx-design`이 설치됨. 새 Codex 대화에서 `/skills`로 6개 스킬 발견을 확인하고 대표 시나리오의 질문·전략 선택·참조 파일 읽기·위임 폴백을 점검한다. Claude Code에서는 `/gx-design:gx-design`, `/gx-design:gx-redesign` 진입이 유지되는지 확인한다. 세션 도구가 실제 사용자 대화를 열 수 없으면 설치·정적 검사까지의 증거와 수동 시나리오를 구분해 보고한다.

- [ ] **Step 6: 이 태스크 파일만 커밋한다**

```powershell
git -c safe.directory=D:/SQ/design-plugin add -- docs/codex-skill-maintenance.md README.md tests/test_codex_compat.py
git -c safe.directory=D:/SQ/design-plugin commit -m "docs: document dual-host skill maintenance and verification"
```

## 계획 자체 점검

- 성공 기준 1은 Task 1·4, 2와 3은 Task 2·3·4, 4와 5는 Task 1·4에 대응한다.
- 신규 매니페스트와 테스트 모듈의 키·상수·경로는 Task 1에서 정의하고 이후 태스크가 그대로 쓴다.
- 실행 전 `docs/superpowers/specs/2026-09-16-gx-design-codex-compat-design.md`와 이 계획을 함께 읽는다.
