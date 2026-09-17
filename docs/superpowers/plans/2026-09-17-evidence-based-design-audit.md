# Evidence-Based Design Audit 최소 개선 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 디자인 규칙을 중복하지 않고 빈틈만 보완하여, `gx-redesign`은 화면에서 발견된 문제만 수정하고 `gx-design`의 실행 가능한 UI는 데스크톱·모바일·상호작용·접근성을 검증하게 한다.

**Architecture:** 새 규칙 카탈로그나 실행 엔진을 만들지 않고 기존 Markdown 정본 세 개에 책임을 나눈다. `ANTI-TELL-CHECKLIST.md`는 누락된 UI 안티패턴, `gx-redesign/SKILL.md`는 증거 기반 진단과 변경 범위 잠금, `VISUAL-QUALITY.md`와 `REVIEW-AXES.md`는 실행 검증과 검수 게이트를 소유한다. Python `unittest` 계약 테스트는 자연어 전문 대신 필수 계약 문구 묶음을 검사한다.

**Tech Stack:** Markdown 기반 Codex/Claude 플러그인 스킬, Python 3 표준 라이브러리 `unittest`, Git

**Spec:** `docs/superpowers/specs/2026-09-17-evidence-based-design-audit-design.md`

## Global Constraints

- 새로운 20개 항목 카탈로그 파일을 만들지 않는다.
- 이미 존재하는 규칙은 `ANTI-TELL-CHECKLIST.md`, `VISUAL-CRAFT.md`, `VISUAL-QUALITY.md`를 정본으로 유지한다.
- 기존 문서에 없는 규칙만 가장 가까운 기존 문서에 추가한다.
- UI·웹 화면 작업에서만 관련 참고 문서를 조건부로 읽게 한다.
- 화면에서 관찰되지 않은 문제를 고치기 위한 전면 재설계를 금지한다.
- 정적 이미지로 확인할 수 없는 기능은 통과로 추정하지 않고 검증 한계로 기록한다.
- 브리프와 브랜드 기준이 의도적으로 요구하는 표현은 근거를 기록하면 허용한다.
- 외부 Python 패키지를 추가하지 않는다.
- 플러그인 버전과 매니페스트는 변경하지 않는다.

---

### Task 1: 누락된 UI 안티패턴을 기존 체크리스트에 보완

**Files:**
- Create: `tests/test_evidence_based_design_audit.py`
- Modify: `skills/gx-design/ANTI-TELL-CHECKLIST.md:5-46`

**Interfaces:**
- Consumes: 기존 `ANTI-TELL-CHECKLIST.md`의 적용 원칙과 요소·카피·구조 구분
- Produces: `read_doc(relative_path: str) -> str`, `assert_terms(testcase, text: str, terms: tuple[str, ...]) -> None`, UI·웹 조건부 누락 규칙과 법률 정보 비생성 계약

- [ ] **Step 1: 누락 규칙 계약 테스트를 작성한다**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_terms(
    testcase: unittest.TestCase,
    text: str,
    terms: tuple[str, ...],
) -> None:
    for term in terms:
        with testcase.subTest(term=term):
            testcase.assertIn(term, text)


class AntiTellChecklistContractTests(unittest.TestCase):
    def test_ui_web_gap_rules_are_present(self) -> None:
        text = read_doc("skills/gx-design/ANTI-TELL-CHECKLIST.md")
        assert_terms(
            self,
            text,
            (
                "장식용 이모지",
                "리퀴드 글라스",
                "근거 없는 리뷰",
                "벤토 그리드",
                "장식용 터미널",
                "3단계 요금제",
                "체크 표시 목록",
                "제품 화면·사용 과정·결과",
                "같은 큰 둥근 모서리",
                "이용약관",
                "개인정보처리방침",
            ),
        )

    def test_policy_links_require_real_routes_without_invented_facts(self) -> None:
        text = read_doc("skills/gx-design/ANTI-TELL-CHECKLIST.md")
        assert_terms(
            self,
            text,
            ("실제 경로", "임의로 만들지", "입력 필요"),
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 새 테스트가 현재 문서에서 실패하는지 확인한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.AntiTellChecklistContractTests -v`

Expected: `FAIL`이며 첫 실패 메시지에 `장식용 이모지` 또는 그 뒤의 누락 용어가 표시된다.

- [ ] **Step 3: 체크리스트의 적용 범위를 좁히고 누락 규칙만 추가한다**

`ANTI-TELL-CHECKLIST.md`의 적용 원칙에 다음 문장을 추가한다.

```markdown
- 아래 UI 제품 신뢰·구조 항목은 **UI·웹 화면 산출물에만** 적용한다. BX 문서·영상·순수 그래픽 작업에서는 이 절을 로드하거나 점검하지 않는다.
```

기존 `## 3. 구조 수치 가드 (웹/UI 화면)` 뒤, `## 4. 사용법` 앞에 다음 절을 삽입한다.

```markdown
## 4. UI 제품 신뢰·구조 가드 (UI·웹 화면만)

- [ ] 제품 톤과 맞지 않는 장식용 이모지를 쓰지 않았다.
- [ ] 기능·콘텐츠와 관계없는 리퀴드 글라스 효과를 쓰지 않았다.
- [ ] 출처를 확인할 수 없는 근거 없는 리뷰·별점·고객 수·성과 수치를 만들지 않았다.
- [ ] 내용보다 균일한 상자 모양을 먼저 맞춘 벤토 그리드가 아니다.
- [ ] 개발 도구가 아닌 서비스에 장식용 터미널 창을 넣지 않았다.
- [ ] 차이가 불명확한 Basic·Pro·Enterprise식 3단계 요금제를 만들지 않았다.
- [ ] 모든 설명을 체크 표시 목록으로 바꾸지 않았다.
- [ ] 제품 히어로에 실제 제품 화면·사용 과정·결과 중 하나가 있다.
- [ ] 모든 상자와 버튼에 같은 큰 둥근 모서리를 일괄 적용하지 않았다.
- [ ] 결제·가입 기능이 있으면 실제로 열리는 이용약관 경로가 있다.
- [ ] 사용자 데이터를 다루면 실제로 열리는 개인정보처리방침 경로가 있다.

이용약관과 개인정보처리방침은 링크와 실제 경로의 존재를 확인한다. 사업자 정보·수집 항목·보관 기간·제3자 제공처럼 제공되지 않은 사실은 임의로 만들지 말고 문서에 `[입력 필요]`로 표시한다.
```

기존 `## 4. 사용법`은 `## 5. 사용법`으로 번호를 바꾼다.

- [ ] **Step 4: 안티패턴 계약 테스트를 다시 실행한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.AntiTellChecklistContractTests -v`

Expected: 2 tests `OK`.

- [ ] **Step 5: Task 1 변경만 커밋한다**

```bash
git add tests/test_evidence_based_design_audit.py skills/gx-design/ANTI-TELL-CHECKLIST.md
git commit -m "feat: fill UI anti-pattern audit gaps"
```

---

### Task 2: 리디자인 진단과 변경 범위를 증거에 잠근다

**Files:**
- Modify: `tests/test_evidence_based_design_audit.py`
- Modify: `skills/gx-redesign/SKILL.md:32-94`

**Interfaces:**
- Consumes: Task 1의 `read_doc`, `assert_terms`, `ANTI-TELL-CHECKLIST.md`
- Produces: 발견 항목 전용 진단표 계약, `진단 문제 또는 승인된 개선 브리프 목표` 변경 근거 계약, 제작 후 회귀 검사 계약

- [ ] **Step 1: 리디자인 진단 계약 테스트를 추가한다**

`tests/test_evidence_based_design_audit.py`에서 `if __name__ == "__main__":` 블록 앞에 다음 클래스를 추가한다.

```python
class RedesignAuditContractTests(unittest.TestCase):
    def test_audit_reports_only_observed_findings(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(
            self,
            text,
            (
                "UI·웹 화면일 때만",
                "실제로 발견된 항목만",
                "해당 없음",
                "검증 한계",
                "왜 어색한지",
                "무엇으로 바꿀지",
            ),
        )

    def test_changes_are_locked_to_findings_or_approved_brief(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(
            self,
            text,
            (
                "변경 범위 잠금",
                "진단 문제 또는 승인된 개선 브리프 목표",
                "진단되지 않은 새 안티패턴",
            ),
        )
```

- [ ] **Step 2: 리디자인 테스트가 현재 스킬에서 실패하는지 확인한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.RedesignAuditContractTests -v`

Expected: 2 tests `FAIL`이며 누락 용어로 `UI·웹 화면일 때만`과 `변경 범위 잠금`이 표시된다.

- [ ] **Step 3: 단계 1에 증거 기반 진단 계약을 추가한다**

`gx-redesign/SKILL.md` 단계 1의 기존 진단 설명 뒤에 다음 내용을 삽입한다.

```markdown
UI·웹 화면일 때만 [../gx-design/ANTI-TELL-CHECKLIST.md](../gx-design/ANTI-TELL-CHECKLIST.md)를 추가 입력으로 읽는다. 모든 관련 규칙을 검토하되 진단표에는 **실제로 발견된 항목만** 기록하고 `해당 없음` 목록은 출력하지 않는다. 각 행은 `문제 | 화면·위치 | 관찰 증거 | 왜 어색한지 | 무엇으로 바꿀지 | 심각도` 형식을 따른다. 스크린샷만으로 버튼·링크·키보드 동작을 확인할 수 없으면 통과로 추정하지 않고 `검증 한계`에 기록한다. 카드·흰 배경·아이콘처럼 정상적으로도 쓰이는 패턴은 제품 목적과 콘텐츠 구조를 확인한 뒤 판정한다.
```

단계 1 완료 기준을 다음 문장으로 교체한다.

```markdown
완료 기준: outputs/research/에 발견 항목만 담은 진단표와 검증 한계가 저장되었고, 각 진단 행에 관찰 증거·왜 어색한지·무엇으로 바꿀지가 있으며, 사용자에게 진단 요약을 보고했다.
```

- [ ] **Step 4: 단계 3·4·5에 변경 범위 잠금과 회귀 검사를 연결한다**

단계 3 첫 문단 앞에 다음 문단을 추가한다.

```markdown
**변경 범위 잠금**: 세 개선안은 진단 문제 또는 승인된 개선 브리프 목표에 직접 연결된 변경만 제안한다. 단순히 더 세련돼 보인다는 이유로 진단되지 않은 영역을 전면 재설계하지 않는다.
```

단계 4의 before/after 기록 문장을 다음 내용으로 강화한다.

```markdown
**모든 변경 항목은 before → after → 근거의 3열로 기록하고, 근거에는 반드시 `진단 문제 또는 승인된 개선 브리프 목표`를 적는다.** 둘 중 어느 것에도 연결되지 않는 변경은 제작 범위에서 제외한다.
```

단계 5의 축 C 설명 뒤에 다음 문장을 추가한다.

```markdown
축 C는 발견된 문제의 해소뿐 아니라 제작 과정에서 진단되지 않은 새 안티패턴이 생기지 않았는지도 회귀 검사한다.
```

- [ ] **Step 5: 리디자인 계약 테스트를 다시 실행한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.RedesignAuditContractTests -v`

Expected: 2 tests `OK`.

- [ ] **Step 6: Task 2 변경만 커밋한다**

```bash
git add tests/test_evidence_based_design_audit.py skills/gx-redesign/SKILL.md
git commit -m "feat: ground redesign changes in observed evidence"
```

---

### Task 3: 실행 가능한 UI의 반응형·상호작용·접근성 검증을 강제

**Files:**
- Modify: `tests/test_evidence_based_design_audit.py`
- Modify: `skills/gx-design/VISUAL-QUALITY.md:8-48`
- Modify: `skills/gx-design/REVIEW-AXES.md:5-17`

**Interfaces:**
- Consumes: Task 1의 테스트 헬퍼, 기존 렌더 품질 로그와 검수 축 B
- Produces: `실행 검증 로그`, 비실행 산출물의 `검증 불가: 비실행 산출물`, 실행 가능한 UI의 누락 로그 Critical 판정

- [ ] **Step 1: 실행 검증 계약 테스트를 추가한다**

`tests/test_evidence_based_design_audit.py`에서 `if __name__ == "__main__":` 블록 앞에 다음 클래스를 추가한다.

```python
class RuntimeVerificationContractTests(unittest.TestCase):
    def test_visual_quality_covers_runtime_ui_checks(self) -> None:
        text = read_doc("skills/gx-design/VISUAL-QUALITY.md")
        assert_terms(
            self,
            text,
            (
                "데스크톱 대표 뷰포트",
                "모바일 대표 뷰포트",
                "주요 버튼",
                "내부·외부 링크",
                "키보드 Tab 이동 순서",
                "보이는 포커스",
                "WCAG AA 대비",
                "prefers-reduced-motion",
                "검증 불가: 비실행 산출물",
            ),
        )

    def test_review_axis_requires_runtime_log_for_executable_ui(self) -> None:
        text = read_doc("skills/gx-design/REVIEW-AXES.md")
        assert_terms(
            self,
            text,
            (
                "실행 검증 로그",
                "실행 가능한 UI",
                "Critical",
                "비실행 산출물",
            ),
        )
```

- [ ] **Step 2: 실행 검증 테스트가 현재 문서에서 실패하는지 확인한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.RuntimeVerificationContractTests -v`

Expected: 2 tests `FAIL`이며 `데스크톱 대표 뷰포트`와 `실행 검증 로그`가 누락됐다고 표시된다.

- [ ] **Step 3: VISUAL-QUALITY 품질 루프에 실행 검증 단계를 추가한다**

`VISUAL-QUALITY.md` 절차의 기존 4번 앞에 다음 항목을 삽입하고 뒤 항목 번호를 하나씩 올린다.

```markdown
4. **UI·웹 실행 검증(실행 가능한 코드 산출물)**: 아래 결과를 제작 문서의 `실행 검증 로그`에 기록한다.
   - 데스크톱 대표 뷰포트 1개 이상과 모바일 대표 뷰포트 1개 이상에서 레이아웃·오버플로·콘텐츠 가림을 확인한다.
   - 주요 버튼의 실행 결과와 내부·외부 링크의 실제 대상·실패 여부를 확인한다.
   - 키보드 Tab 이동 순서가 화면의 의미 순서와 맞고 모든 대화형 요소에 보이는 포커스가 있는지 확인한다.
   - 본문과 주요 제어 요소의 WCAG AA 대비를 확인한다.
   - 모션이 있으면 `prefers-reduced-motion`에서 제거 또는 축소된 대체 동작을 확인한다.
   정적 이미지·영상·비실행 문서에는 기능 통과를 선언하지 않고 `검증 불가: 비실행 산출물`과 제외된 항목을 기록한다.
```

`## 검수 연계`의 첫 항목을 다음 문장으로 교체한다.

```markdown
- 검수(REVIEW-AXES) 축 B의 입력에 실물 이미지 경로, 렌더 품질 로그, 실행 가능한 UI이면 실행 검증 로그를 포함한다.
```

- [ ] **Step 4: REVIEW-AXES 축 B에 실행 검증 게이트를 추가한다**

축 B 설명 뒤에 다음 문단을 삽입한다.

```markdown
실행 가능한 UI·웹 코드 산출물은 [VISUAL-QUALITY.md](VISUAL-QUALITY.md)의 `실행 검증 로그`가 필수다. 로그가 없거나 데스크톱·모바일·버튼·링크·키보드 포커스·대비·모션 감소 중 적용 가능한 항목이 빠졌으면 Critical로 처리한다. 정적 이미지·영상·비실행 산출물은 `검증 불가: 비실행 산출물`과 제외 항목이 기록되어 있으면 기능 결함으로 판정하지 않는다.
```

- [ ] **Step 5: 실행 검증 계약 테스트를 다시 실행한다**

Run: `python -m unittest tests.test_evidence_based_design_audit.RuntimeVerificationContractTests -v`

Expected: 2 tests `OK`.

- [ ] **Step 6: 전체 계약 테스트를 실행한다**

Run: `python -m unittest discover -s tests -v`

Expected: 6 tests `OK`.

- [ ] **Step 7: Task 3 변경만 커밋한다**

```bash
git add tests/test_evidence_based_design_audit.py skills/gx-design/VISUAL-QUALITY.md skills/gx-design/REVIEW-AXES.md
git commit -m "feat: require runtime verification for UI output"
```

---

### Task 4: 조건부 로딩과 전체 회귀를 최종 확인

**Files:**
- Modify: `tests/test_evidence_based_design_audit.py`
- Verify: `skills/gx-design/SKILL.md`
- Verify: `skills/gx-redesign/SKILL.md`
- Verify: `skills/gx-design/ANTI-TELL-CHECKLIST.md`
- Verify: `skills/gx-design/VISUAL-QUALITY.md`
- Verify: `skills/gx-design/REVIEW-AXES.md`

**Interfaces:**
- Consumes: Task 1~3의 문서 계약
- Produces: UI·웹 조건부 참조 회귀 테스트와 최종 검증 증거

- [ ] **Step 1: 조건부 로딩과 독립 카탈로그 부재 테스트를 추가한다**

`tests/test_evidence_based_design_audit.py`에서 `if __name__ == "__main__":` 블록 앞에 다음 클래스를 추가한다.

```python
class LoadingAndScopeContractTests(unittest.TestCase):
    def test_orchestrators_scope_anti_tell_checks_to_visual_ui_outputs(self) -> None:
        design = read_doc("skills/gx-design/SKILL.md")
        redesign = read_doc("skills/gx-redesign/SKILL.md")
        self.assertIn("UI·그래픽·UX/UI·Gemini 웹 생성 산출물", design)
        self.assertIn("UI·웹 화면일 때만", redesign)
        self.assertIn("ANTI-TELL-CHECKLIST.md", design)
        self.assertIn("ANTI-TELL-CHECKLIST.md", redesign)

    def test_no_new_diagnostic_catalog_exists(self) -> None:
        self.assertFalse(
            (ROOT / "skills/gx-design/DESIGN-DIAGNOSTIC-CATALOG.md").exists()
        )
```

- [ ] **Step 2: 전체 계약 테스트를 실행한다**

Run: `python -m unittest discover -s tests -v`

Expected: 8 tests `OK`.

- [ ] **Step 3: 독립 카탈로그 참조와 공백 오류가 없는지 검사한다**

Run: `Test-Path skills/gx-design/DESIGN-DIAGNOSTIC-CATALOG.md`

Expected: `False`.

Run: `git diff --check`

Expected: 출력 없음, 종료 코드 0.

- [ ] **Step 4: 변경 범위가 사양과 일치하는지 확인한다**

Run: `git diff --stat HEAD~3..HEAD`

Expected: 변경 파일이 `tests/test_evidence_based_design_audit.py`, `skills/gx-design/ANTI-TELL-CHECKLIST.md`, `skills/gx-redesign/SKILL.md`, `skills/gx-design/VISUAL-QUALITY.md`, `skills/gx-design/REVIEW-AXES.md`로 제한되고 매니페스트·버전 파일은 없다.

- [ ] **Step 5: 최종 테스트 추가분을 커밋한다**

```bash
git add tests/test_evidence_based_design_audit.py
git commit -m "test: lock evidence-based design audit contracts"
```

- [ ] **Step 6: 최종 상태와 커밋을 확인한다**

Run: `git status --short`

Expected: 이번 계획의 파일에는 미커밋 변경이 없다. 작업 시작 전부터 존재한 사용자 미추적 파일은 그대로 남아 있을 수 있다.

Run: `git log -4 --oneline`

Expected: Task 1~4의 커밋 네 개가 최신 이력에 순서대로 보인다.
