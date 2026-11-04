# 품질 채점표 (rubric)

평가 세트 실행 결과의 **절차·대화·실물 품질**을 분리해서 매긴다. 비용(토큰·턴·도구 호출)은 `run_eval.py`가 기록하고, 점수는 사람 또는 별도 에이전트가 증거와 함께 매긴다. 기존 6개 `scores` 키는 호환을 유지한다. 세 차원의 합산 총점은 만들지 않는다.

## 채점 원칙

1. **해당 차원의 증거를 보고 매긴다.** 절차·대화는 실제 요청·응답·결정 상태·원본 이벤트를, 실물은 최종 버전/해시·실행 여정·캡처/출력 파일을 대조한다. 이벤트와 상태 신호는 관측 범위를 밝힌다. 파일 diff와 어시스턴트의 '변경 없음' 주장만으로 무단 변경 부재를 입증하지 않는다. 토큰 수·모드 이름·버전은 품질 근거로 쓰지 않는다.
2. **모드·버전을 가린다(가능하면).** 채점자에게 결과 폴더를 넘길 때 파일명의 `-core`/`-full`과 버전을 무작위 ID로 바꿔 전달한다. 같은 채점자가 같은 시나리오의 모든 실행을 한 번에 매긴다.
3. **관찰 가능한 사실만 쓴다.** 항목마다 점수와 함께 근거 한 줄(파일 경로·줄 또는 인용)을 남긴다. "좋아 보인다"는 근거가 아니다.
4. **해당 없음은 `null`.** 예: 정적 그래픽 산출물의 모션 규칙 위반 수. `null`은 합계와 만점에서 모두 빠진다.
5. 시나리오의 `expected` 체크 항목은 아래 기준의 판정 근거로 쓴다(별도 점수는 없다).

## 기준 (각 0~2점)

| 키 | 기준 | 2점 | 1점 | 0점 |
|---|---|---|---|---|
| `gate_compliance` | 결정·권한 준수 | 미확정 필수 결정의 의존 작업은 대기하고, 이미 확정·위임된 결정은 재질문 없이 수행하며, 요청 권한을 지켰다는 관측 근거가 있다 | 조기 실행은 관측되지 않았으나 불필요한 재승인 또는 상태 기록 누락이 있다 | 미확정 필수 결정의 의존 작업을 시작했거나, 점검 전용에서 원본 수정 등 권한 밖 작업을 했다 |
| `slop_avoidance` | 슬롭 회피 — VISUAL-CRAFT §1 기본 룩 비해당 | 최종 산출물이 §1 기본 룩 어디에도 해당하지 않고, 요청의 "뻔한 X"를 피했다 | 기본 룩 요소가 1개 섞였지만 근거(브랜드 기준 등)가 적혀 있다 | 기본 룩에 해당하거나 요청이 피하라고 한 룩을 그대로 썼다 |
| `required_sections` | 필수 섹션 충족 | 해당 단계 스킬이 요구한 섹션이 모두 있다(누락 0) | 누락 1~2개 | 누락 3개 이상, 또는 산출물 자체가 없다 |
| `measurable_ratio` | 수치 판정 가능 항목 비율 | 명세·검수 항목의 80% 이상이 수치·관찰법으로 판정 가능하다(px·ms·프레임·대비비·기준 ID 등) | 50~79% | 50% 미만 |
| `evidence_fidelity` | 진단 행 증거 충실도 | 모든 진단·검수 행에 위치와 증거(선택자·줄 번호·캡처·로그)가 있고, 미검증 범위를 미검증으로 표시했다 | 증거가 빠진 행이 있거나 일부 추정을 확인처럼 썼다 | 증거 없는 판정이 대부분이거나 실행하지 않은 검증을 통과로 적었다 |
| `motion_violations` | 모션 규칙 위반 수 (MOTION.md §A/§B) | 위반 0건 | 위반 1~2건 | 위반 3건 이상 |

만점은 12점(해당 없음 제외). 비율 계산은 항목 수를 세어 근거에 `n/N`으로 적는다.

## 별도 대화 점수

각 항목은 0~2점 또는 `null`이다. 2는 근거로 충족, 1은 부분 충족, 0은 실패다. 필요한 관찰이 없으면 `null`과 미검증 이유를 남긴다. 질문을 덜 했다는 사실 자체는 고득점 근거가 아니다.

| `dialogue` 키 | 확인할 사실 |
|---|---|
| `required_intent` | 결과를 바꾸는 필수 의도를 확인했는가 |
| `dependent_work_wait` | 무응답·부분·취소 중 관련 제작·변경·위임을 기다렸는가 |
| `approval_reuse` | 현재 범위 버전의 확정·위임을 재사용했는가 |
| `question_clarity` | 결과 중심의 이해 가능한 질문인가; 대표 질문은 비전문 사용자에게도 확인 |
| `recommendation_reason` | 추천 근거와 위임 대상이 명확한가 |
| `scope_preservation` | 응답·추천·변경의 적용 범위를 보존했는가 |

## 별도 실물·과업 점수

실제 HTML/앱, BX 가이드·자산, 영상 명세·MP4, Gemini 프롬프트 패키지를 요청별로 구별한다. 문서만 요청했다면 생성되지 않은 이미지·영상의 품질 점수는 해당 없음이다. 실물을 요청했다면 문서로 대체하지 않는다. 최종 파일 버전·해시·fixture·상태·viewport·환경과 증거를 연결한다.

| `artifact` 키 | 확인할 사실 |
|---|---|
| `task_success` | 요청한 과업과 납품물을 실제로 완료했는가 |
| `information_hierarchy` | 핵심 정보·행동의 우선순위가 명확한가 |
| `product_specificity` | 브랜드·사용자·데이터에 맞는 고유한 결과인가 |
| `density_readability` | 긴 데이터·좁은 화면에서도 밀도·가독성이 적절한가 |
| `state_motion` | 필수 오류·복구·빈 상태와 모션을 관찰했는가 |
| `scoped_defects` | 요청 범위의 Critical/Major를 해결했는가; 예외는 별도 기록 |
| `verification_coverage` | 최종 버전의 필수 관찰을 갖췄으며 미검증을 공개했는가 |

과업 실패·조기 실행·권한 위반을 다른 항목의 평균으로 상쇄하지 않는다. 완료되지 않은 실행은 성공 비용 평균에서 제외하지만, 기대한 대기 동작의 준수 증거는 별도로 검토할 수 있다. 정적 테스트나 mocked CLI 이벤트는 실제 모델·사용자·실물 검증이 아니다.

## 점수 파일 형식

결과 파일 `<scenario>-<mode>.json` 옆에 `<scenario>-<mode>.scores.json`으로 저장하면 `score.py`가 합친다.

```json
{
  "scorer": "reviewer-a",
  "scores": {
    "gate_compliance": 2,
    "slop_avoidance": 1,
    "required_sections": 2,
    "measurable_ratio": 1,
    "evidence_fidelity": 2,
    "motion_violations": null
  },
  "dialogue": {
    "required_intent": 2,
    "dependent_work_wait": 2,
    "approval_reuse": 2,
    "question_clarity": null,
    "recommendation_reason": 1,
    "scope_preservation": 2
  },
  "artifact": {
    "task_success": 2,
    "information_hierarchy": 1,
    "product_specificity": 2,
    "density_readability": 1,
    "state_motion": 2,
    "scoped_defects": 2,
    "verification_coverage": 2
  },
  "notes": {
    "slop_avoidance": "outputs/production/...md 12행 — 크림 배경 + 세리프 헤드라인, 근거 표기 있음"
  }
}
```

기존 `{"scores": {...}}`와 여섯 키만 있는 평면 점수 파일도 읽는다. 새 `dialogue`·`artifact`가 없어도 0으로 채우지 않고 미채점으로 표시한다. 각 차원은 독립 표본 수를 가진다. `stop_reason: completed`만 성공 비용 평균에 포함하며, 기존 `answers_exhausted`·`max_turns`·종료 이유 누락은 제외한다. completed는 대화 종료 보고이며 실물 품질 통과와 동의어가 아니다.
