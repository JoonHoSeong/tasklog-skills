# 자동 연동 및 수동 대체

지원 대상은 Codex, Claude Code, Kiro CLI V3, agy(Antigravity CLI), pi coding agent다. `pi`는 다른 동명 제품이 아니라 기존 badlogic/pi-mono, 현재 earendil-works/pi를 뜻한다. Python 3.10 이상과 macOS/Linux용 공통 런타임을 사용한다. Windows는 현재 수동 스킬 사용 경로를 제공한다.

## 설치와 활성화

스킬과 보조 파일을 함께 설치한다. 설치된 `notion-log-work` 폴더의 **절대 경로**를 `SKILL_DIR`로 지정하고 실제 작업 프로젝트를 `PROJECT_DIR`로 지정한다. 아래 명령은 네트워크 설치 없이 프로젝트의 도구 설정만 추가한다.

```bash
SKILL_DIR=/absolute/path/to/notion-log-work
PROJECT_DIR=/absolute/path/to/project
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" install --agent claude-code
```

`--agent`는 `codex`, `claude-code`, `kiro`, `agy`, `pi` 중 하나다. 사용할 도구마다 실행한다. 스크립트가 있는 경로를 유지해야 하며 저장소나 스킬 경로를 옮기면 훅을 확인·정리하고 재설치한다. 동일 경로 재설치는 중복 훅을 추가하지 않는다. 기존 일반 설정은 병합하며 변경 전 `.pre-tasklog` 백업을 남긴다. 기존 이름의 Kiro 훅이나 pi 확장이 다르면 덮어쓰지 않는다. 설치 명령은 사용자 홈에 설치하거나 도구를 다운로드하지 않는다.

프로젝트 `.tasklog.json`의 기존 필드를 유지하면서 다음 설정을 추가한다.

```json
"auto_record": {"enabled": true}
```

프로젝트 `.gitignore`에는 `/.tasklog/`, `/.tasklog.json`, `*.pre-tasklog`를 추가한다. 개인 기록·설정·백업을 커밋하지 않는다. `.tasklog`는 Git 경로 제외 설정과 무관하게 변경 감지에서 제외된다. 해제하려면 `enabled=false`로 바꾼다. 설정 항목을 삭제해도 비활성이다. 각 도구의 훅 신뢰·프로젝트 신뢰 절차와 Notion 쓰기 권한은 해당 도구에서 설정한다. 설치 스크립트가 권한을 우회하지 않는다.

## 도구별 연결

| 도구 | 설치되는 프로젝트 파일 | 자동 기록 방식 |
| --- | --- | --- |
| Codex | `.codex/hooks.json` | Stop에서 현재 에이전트에 한 차례 기록 요청, SessionEnd는 로컬 보관 |
| Claude Code | `.claude/settings.json` | Stop에서 현재 에이전트에 한 차례 기록 요청, SessionEnd는 로컬 보관 |
| Kiro CLI V3 | `.kiro/hooks/tasklog.json` | Stop command가 stdin의 실제 session_id를 사용해 기록 요청을 반환 |
| agy | `.agents/hooks.json` | Stop의 continue 응답으로 현재 에이전트에 한 차례 기록 요청 |
| pi | `.pi/extensions/tasklog.js` | agent_before_settle에서 한 차례 continuation 요청, session_shutdown은 로컬 보관 |

설정 변경 후 도구를 다시 시작한다. pi는 `/reload`도 가능하다. pi 1.5.2의 `agent_before_settle` API를 사용하며 이 이벤트가 없는 버전은 수동 기록한다. Codex/Claude Code/agy는 `/hooks`에서 로딩과 신뢰 상태를 확인한다. Kiro는 V3 형식 지원을 확인한다. pi 확장에는 추가 npm 패키지가 필요 없다.

공통 런타임은 Git HEAD·브랜치·추적/미추적 파일 변경의 지문을 비교한다. 같은 에이전트·세션·상태에 기록 요청은 한 번만 한다. 원문 diff·대화·훅 입력·토큰은 자동 보관하지 않고 메타데이터만 pending으로 남긴다. 따라서 파일 변경이나 새 커밋이 없는 대화·설계 작업은 수동 기록을 사용한다. 첫 자동 실행에서 이미 존재하는 변경도 후보가 되므로 에이전트가 현재 세션의 작업 범위를 대조해야 한다. Git이 없는 프로젝트도 수동 기록을 사용한다.

훅은 별도 모델이나 Notion API를 호출하지 않는다. 현재 에이전트가 세션 맥락과 해당 도구의 Notion MCP를 사용하므로 추가 에이전트 턴 비용이 발생할 수 있다. Kiro도 command 훅에서 변경 지문을 검사하므로 기록할 변경이 없으면 모델에 추가 기록 요청을 보내지 않는다. MCP 제공자가 바뀌면 실제 도구 스키마를 따른다. pi에서 Notion 도구가 노출되지 않으면 MCP 설정의 exposure와 codemode/tool_search 활성 상태를 확인한다. 최소 설정 시험에서는 Notion 서버를 `exposure: "direct"`로 노출할 수 있다. 연결이 안 되면 로컬 초안까지만 만들고 MCP가 연결된 다른 도구에서 전송한다.

모델의 여러 도구 호출을 포함한 자동 기록은 수분 이상 걸릴 수 있다. 로컬 훅 스크립트 timeout과 모델 작업 전체의 실행 제한을 구분한다. 시험에서 pi의 정상 초안 보관이 409.3초 걸렸으므로 2~4분의 외부 제한으로 종료한 결과만으로 실패를 단정하지 않는다.

세션 종료 훅만으로 새 요약·Notion 전송을 보장하지 않는다. 강제 종료, 권한 거부, 훅 시간 초과, 이벤트 미지원은 수동 경로를 사용한다. 동시에 같은 작업을 기록할 때는 Task ID와 기존 페이지를 반드시 대조한다. 런타임은 로컬 파일 잠금으로 같은 세션의 중복 요청을 방지하지만 Notion 생성 자체의 원자성까지 보장하지 않는다.

## 수동 기록 및 장애 복구

먼저 로컬 진단을 실행한다. 실행 파일 존재만 확인하며 최신 버전 호환성이나 Notion 접근 권한을 검증한 것으로 해석하지 않는다.

```bash
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" doctor
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" pending
```

자동화 없이 로컬 체크포인트를 만들 수 있다. 서로 다른 작업에는 다른 `--session` 값을 사용한다. 초안 파일은 사용자가 민감정보를 제거한 Markdown만 지정한다. 이 명령 자체가 비밀값을 자동 마스킹하지는 않는다.

```bash
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" checkpoint --session billing-retry --draft-file /path/to/sanitized-draft.md
```

그다음 에이전트에 자연어로 요청한다. 슬래시 명령 지원 여부와 관계없이 스킬 파일을 읽을 수 있으면 같은 절차를 수행할 수 있다.

> notion-log-work를 사용해 .tasklog/<id>.json의 초안을 현재 작업 기록과 대조해서 Notion에 저장해줘. 같은 Task ID나 page_url의 기존 기록이 있으면 갱신하고, 저장 후 다시 조회해 확인해줘. 실패하면 초안은 보존해줘.

복원은 `notion-resume-work로 해당 체크포인트의 draft를 읽고 다음 작업을 복원해줘`라고 요청한다. 스킬 탐색이 안 되면 설치된 SKILL.md의 경로를 명시한다. 파일 도구도 없으면 스킬 내용과 민감정보를 제거한 기록을 직접 제공한다. Notion MCP가 없을 때에는 Markdown을 Notion에 수동으로 붙여넣을 수 있다. 실제 저장 여부를 확인한 뒤에만 다음 명령을 실행한다.

```bash
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" ack <id> --page-url https://www.notion.so/VERIFIED_PAGE_ID
```

pending이 없더라도 자동 전송 성공을 의미하지 않는다. `page_url`, `status=synced`, 실제 Notion 페이지의 본문을 확인한다. 자동 기록 실패 뒤 동일 Git 상태에서는 자동 재시도하지 않으므로 pending의 초안을 수동으로 처리한다.

## 제거

먼저 `auto_record.enabled=false`로 바꾼다. Codex/Claude Code는 설정의 tasklog.py 명령을 가진 훅 항목만, agy는 최상위 `tasklog` 항목만 제거한다. Kiro/pi는 위 표의 전용 파일을 제거한다. 다른 훅이 추가된 뒤에는 백업 전체를 복원해 덮어쓰지 않는다. `.tasklog` 초안은 필요하면 보관한다.

## 근거와 검증 범위

2026-11-23 공식 인터페이스 기준 구현이다. 지원 최소 버전 숫자를 추정하지 않는다. 실제 환경에서 훅 로딩과 기록 왕복 검증이 끝난 버전만 검증된 버전으로 표시한다. 로컬 프로토콜 테스트는 실제 다섯 CLI와 Notion 간 왕복 검증을 대체하지 않는다.

로컬 검증: Python 통합 테스트 11건, pi 확장 동작 테스트 1건 통과. 설치된 pi 1.5.2의 실제 확장 로더에서 모듈 로딩과 이벤트 등록을 확인했다. Codex 0.171.0, Kiro CLI 3.5.0, agy 1.5.14에서 실제 MCP 쓰기·재조회와 자동 훅의 로컬 초안 보관을 확인했다. pi 1.5.2에서 실제 자동 훅의 로컬 초안 저장·정상 종료(auto: 409.3초)와 Notion 자동 생성·재조회·ack·synced·정상 종료(local: 241.6초)를 확인했다. 외부 실행 제한은 900초였다. Flash 경로는 후속 모델 출력 없이 900초 제한을 넘겼으므로 그 모델 경로의 정상 완료는 확인되지 않았다. Claude Code는 미설치로 실제 실행을 확인하지 못했다. Codex·Kiro·agy의 자동 훅 시험은 DB 미설정 시 복구 경로이며 실제 DB 자동 기록 전체 경로의 성공을 뜻하지 않는다. pi는 위의 local 모델 조건에서 실제 DB 왕복까지 확인했다.

2026-11-24 사용자가 수정·배포한 게이트웨이에서 Flash → local 폴백(12.640초)과 실제 pi의 스트리밍·read 도구 왕복(2.655초)을 재검증했다. 공급자 혼잡은 남아 있었지만 서버의 옵션 변환과 혼잡 우회로 정상 응답했다. 수정 후 Flash 경로의 Notion 자동 저장 전체 과정은 다시 실행하지 않았다. 상세한 조건과 남은 범위는 저장소의 [검증 결과](https://github.com/JoonHoSeong/tasklog-skills/blob/main/VALIDATION.md)를 확인한다. 이 개인 게이트웨이는 스킬의 필수 의존성이 아니며, 사용 중인 모델과 Notion MCP가 정상 동작하면 다른 공급자도 사용할 수 있다.

- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Kiro standalone hooks](https://kiro.dev/docs/hooks/), [V3 migration](https://kiro.dev/docs/cli/v3/hooks-migration/)
- [Antigravity hooks](https://antigravity.google/docs/hooks)
- [pi extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
