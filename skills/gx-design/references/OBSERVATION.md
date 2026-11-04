# 화면 구조 관측 — 선택 도구

기존 화면의 배치·계산 스타일·반복 관계가 진단에 필요할 때만 읽는다. 원본 캡처, 상태·데이터·뷰포트 기록과 실제 과업 실행을 우선하며 관측 도구는 그 증거를 보조한다. 관측 요약은 토큰 정본·컴포넌트 의미·사용성 판정이 아니다.

## 사용

사용 가능한 브라우저 실행 도구의 페이지 평가 기능으로 [observe-ui.js](../scripts/observe-ui.js)를 읽어 실행한 뒤 `gxObserveUI({root: '#target'})`를 호출한다. 호스트가 함수를 평가 인자로 받으면 파일 본문의 함수를 그대로 전달한다. Node 자체에서 DOM 없이 실행하는 CLI가 아니다. 새 확장·브라우저 패키지를 설치하거나 서버에 업로드할 필요는 없다.

- 승인된 대상 영역을 `root`로 지정한다. 기본은 body이며 진단할 작은 영역을 우선한다.
- 기본 최대 관측 250요소·탐색 2,500요소. 각각 `maxElements`·`maxScan`으로 조절 가능하며 상한은 1,000·10,000이다.
- 기본 수집 대상은 양수 크기의 사각형, `visibility:visible`, `display:none`이 아닌 요소 중 조상까지 곱한 유효 opacity가 0보다 큰 요소다. 완전히 투명한 요소는 관측 한도를 쓰지 않으며 `coverage.transparentSkipped`에 탐색 중 제외한 수를 기록한다. 투명한 배치 구조도 필요하면 `includeTransparent:true`를 지정한다. `styles.opacity`는 해당 요소의 계산값, `visibility.effectiveOpacity`는 관측 영역 밖 조상까지 반영한 값이다. `coverage.inclusion`과 `includeTransparent`로 수집 기준을 확인한다.
- 투명한 하위 구조도 탐색 한도에는 포함되므로 큰 숨은 영역 뒤의 요소는 `maxScan`에서 잘릴 수 있다. 유효 opacity는 픽셀 가시성 판정이 아니다. 화면 밖 배치·다른 요소의 가림·클리핑·필터 효과를 판정하지 않으며 실제 캡처와 함께 해석한다.
- DOM을 수정·스크롤하거나 클릭하지 않는다. 텍스트 본문·입력값은 수집하지 않지만 선택자·클래스·스타일에도 업무 정보가 있을 수 있으므로 필요한 영역만 취급한다.
- 반환값의 coverage·truncated·fontsStatus를 확인하고 캡처 시점·fixture·상태·뷰포트·환경과 연결한다. 브라우저나 파일 접근이 불가하면 사유와 미검증 범위를 기록한다.
- 반복 묶음과 clippedContentCandidate는 확인할 후보다. 실제 화면을 보고 의미 있는 반복·의도된 스크롤과 잘림을 구별한다. 수집 결과만으로 결함을 만들지 않는다.

shadow root 내부·iframe 문서·가상 요소·입력에 따른 상태는 제외된다. 동작은 원본 페이지에서 별도로 확인한다. 계산된 색·간격을 원래 의미 토큰이라고 부르거나, 한 폭의 관측을 반응형 전체의 검증으로 확대하지 않는다.

## 예제로 검증

[목록·필터](../examples/list-filter.html)와 [폼·오류 복구](../examples/form-errors.html)는 다른 과업의 작은 대조 세트다. 각각 정상·최악 데이터·오류 상태를 확인하고, 같은 조건에서 before/after 증거를 남긴다. 예제의 색·외형을 다른 브랜드의 정답으로 쓰지 않는다. 외부 디자인 자산을 포함하지 않는다.

저장소의 빠른 단위 검사에는 브라우저 시작을 포함하지 않는다. 실제 DOM·입력 복구·선택자 역조회 검사는 Node.js 22+와 로컬 Chrome/Chromium이 있을 때 `GX_BROWSER_TESTS=1`을 설정하고 `python -B -X utf8 -m unittest discover -s tests -p test_browser_observation.py -v`로 별도 실행한다. `GX_BROWSER_BIN`으로 실행 파일을 지정할 수도 있다. Node는 테스트 전송에만 사용하며 관측 함수 자체의 의존성은 아니다. 브라우저 검사 생략은 실제 DOM 검증 통과를 뜻하지 않는다.

실제 Chrome 접근성 트리로 폼의 초기·오류·수정 전/후·복구 상태의 설명을 확인한다. 테스트 전송은 브라우저 시작, DevTools HTTP 응답, WebSocket 연결과 개별 명령에 각각 제한 시간을 두며 실패·중단 때 자신이 시작한 브라우저와 임시 프로필을 정리한다. 운영체제가 Node를 강제로 종료하는 경우에는 Python 실행기의 프로세스 정리가 보완한다.

Swarm Rebuild의 시각 청사진 접근에서 아이디어를 참고했으며 그 소스를 복사하지 않았다. [원문](https://github.com/DhvanilPatel/swarm-cursors)에는 코드 재사용 라이선스가 없다고 명시되어 있다. GX 관측 도구는 자체 작성이며 커서 재구성 연출을 포함하지 않는다.
