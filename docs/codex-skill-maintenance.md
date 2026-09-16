# gx-design 스킬 수정 시 Claude Code·Codex 호환 점검

이 저장소의 여섯 스킬은 두 호스트에서 같은 디자인 절차와 산출물 계약을 사용합니다. Claude Code의 `agents/*.md`는 Claude 전용 설정입니다. Codex가 해당 frontmatter의 모델, 도구, 스킬 자동 로드를 해석한다고 가정하지 않습니다.

## 수정 순서

1. 수정할 `skills/<name>/SKILL.md`의 `name`, `description`, 참조 파일을 확인합니다. 새 스킬은 `skills/<name>/SKILL.md`에 두고 두 호스트의 스킬 목록에서 발견되는지 점검합니다.
2. 질문·승인·선택 문장을 바꾸면 [`HOST-COMPAT.md`](../skills/gx-design/HOST-COMPAT.md)를 따릅니다. Claude 전용 `AskUserQuestion` 호출 형식, 문항 수, `multiSelect`, `preview`를 필수 전제로 두지 않습니다. 현재 입력 도구가 제한되면 모든 선택지를 대화로 제시하고 필요한 답변을 기다립니다. 이미 받은 결정은 다시 묻지 않습니다.
3. 위임 문장을 바꾸면 역할, 입력 11항목, 산출 경로, 완료 기준, 주 에이전트 폴백을 확인합니다. `agents/*.md`의 이름이나 모델을 Codex의 필수 작업자로 요구하지 않습니다. 실제 위임 도구와 사용자·프로젝트 지시가 허용할 때만 역할을 맡깁니다.
4. 디자인 방법론을 바꾸면 해당 스킬과 참조 파일, 브리프·전략·제작·검수의 연결을 함께 확인합니다. 신규 제작의 2축 검수, 개선의 3축 검수, 실물 제작 경로 선택을 유지합니다.
5. 배포 기본 버전을 바꾸면 `.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json`의 `name`과 기본 `version`을 맞춥니다. Codex의 `+codex.<cachebuster>` 접미사는 같은 기본 버전에서 로컬 캐시를 갱신할 때만 사용합니다.

## 자동 검증

저장소 루트에서 다음을 실행합니다. 검증기는 설치된 plugin-creator 스킬의 경로를 사용합니다.

```powershell
$repo = (Get-Location).Path
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex' }
$pluginCreator = Join-Path $codexHome 'skills/.system/plugin-creator/scripts'
python -m unittest discover -s tests -v
python (Join-Path $pluginCreator 'validate_plugin.py') $repo
rg -n 'AskUserQuestion|multiSelect|preview|WebSearch|WebFetch|Read로|model: haiku|model: sonnet' skills
git diff --check
```

위 명령은 현재 위치가 gx-design 저장소 루트라고 가정합니다. `CODEX_HOME`이 설정되어 있으면 그 위치를, 없으면 사용자 프로필 아래의 `.codex`를 사용합니다.

`rg` 결과는 문맥을 읽어 두 호스트의 필수 호출인지 판별합니다. 활성 스킬과 참조 파일의 로컬 Markdown 링크는 `tests/test_codex_compat.py`가 실제 파일 존재 여부를 검사합니다. 정적 검사는 사용자의 실제 선택이나 디자인 품질까지 증명하지 않습니다.

## 로컬 설치와 캐시 갱신

기존 사용자 설치와 분리하려면 운영체제의 임시 디렉터리 아래에 별도 `CODEX_HOME`을 만듭니다. 다음 명령은 gx-design 저장소 루트에서 실행하며 네트워크를 필요로 하지 않습니다.

```powershell
$repo = (Get-Location).Path
$originalCodexHome = $env:CODEX_HOME
$smokeHome = Join-Path ([System.IO.Path]::GetTempPath()) 'gx-design-codex-smoke'
New-Item -ItemType Directory -Path $smokeHome -Force | Out-Null
$env:CODEX_HOME = $smokeHome
codex plugin marketplace add $repo --json
codex plugin add gx-design@gx-design --json
codex plugin list
$env:CODEX_HOME = $originalCodexHome
```

실사용 환경에서 같은 기본 버전의 변경을 다시 설치할 때는 마켓플레이스 이름을 확인하고 Codex 매니페스트의 cachebuster를 갱신한 다음 기본 버전 동기화를 테스트합니다.

```powershell
$repo = (Get-Location).Path
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex' }
$pluginCreator = Join-Path $codexHome 'skills/.system/plugin-creator/scripts'
python (Join-Path $pluginCreator 'read_marketplace_name.py') --marketplace-path (Join-Path $repo '.claude-plugin/marketplace.json')
python (Join-Path $pluginCreator 'update_plugin_cachebuster.py') $repo
python -m unittest discover -s tests -v
codex plugin add gx-design@gx-design
```

캐시 갱신 블록은 평소 사용하는 Codex 환경에서 실행합니다. 격리 설치 블록은 마지막에 기존 `CODEX_HOME` 값을 복원합니다.

Claude Code에서는 기존 `/plugin marketplace add bs-koo/gx-design`와 `/plugin install gx-design@gx-design` 경로를 확인합니다. 변경 반영은 Claude 매니페스트 버전과 `claude plugin marketplace update gx-design`, `claude plugin update gx-design@gx-design` 절차를 따릅니다.

## 대표 요청 점검

- 새 Codex 대화에서 `/skills`로 여섯 스킬을 확인하고 `$gx-design 단일 화면 UX/UI 디자인, 핵심 모드`를 요청합니다. 브리프 질문·승인, 전략 선택, 제작, 두 축 검수, 실물 제작 경로 선택이 이어지는지 봅니다.
- `$gx-redesign 기존 화면 개선, 핵심 모드`를 요청합니다. 자산 인벤토리·개선 브리프, before/after/근거 3열, 세 축 검수를 봅니다.
- 위임 도구가 없는 세션에서 같은 요청을 실행해 주 에이전트가 역할별 스킬과 참조 파일을 읽고 산출물 계약을 지키는지 봅니다.
- Claude Code에서는 `/gx-design:gx-design`과 `/gx-design:gx-redesign`의 기존 진입을 확인합니다.

실제 세션을 실행하지 않았다면 설치·정적 검증 결과와 수동 시나리오 확인을 구분해 기록합니다.

## 근거

- [OpenAI Claude 플러그인 전환 안내](https://developers.openai.com/plugins/guides/submit-claude-plugin)
- [OpenAI Codex 플러그인 안내](https://learn.chatgpt.com/docs/build-plugins)
- [OpenAI Codex 스킬 안내](https://learn.chatgpt.com/docs/build-skills)
- [OpenAI 마켓플레이스 지원 형식](https://learn.chatgpt.com/docs/enterprise/plugin-management)
