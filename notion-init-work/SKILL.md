---
name: notion-init-work
description: 현재 프로젝트의 작업 기록용 이름을 .tasklog.json에 설정하고 Notion 데이터베이스 ID 입력 자리를 만들거나 갱신할 때 사용한다.
---

# Notion 작업 프로젝트 설정

Codex, Kiro CLI, agy, Claude Code, pi에서 같은 JSON 설정을 사용한다. 자동 기록은 선택 기능이며 기존 `auto_record` 설정을 보존한다. 사용자가 활성화를 요청한 경우에만 `"auto_record": {"enabled": true}`를 추가한다. 훅·확장은 별도로 설치해야 하며 스킬만 설치했다고 자동 기록 완료로 보고하지 않는다. MCP가 없으면 로컬 설정만 준비하고 연결 미검증으로 표시한다. 파일 쓰기 기능도 없으면 사용자가 저장할 JSON을 응답으로 제공한다.

## 입력과 위치

- 설정 파일 위치는 Git 저장소 안이면 `git rev-parse --show-toplevel`의 `.tasklog.json`, Git 저장소 밖이면 현재 작업 디렉터리의 `.tasklog.json`이다.
- 프로젝트명은 사용자 지정값 > 기존 `.tasklog.json`의 `project` > Git `remote.origin.url`의 저장소명 > 현재 작업 디렉터리명 순서로 정한다. remote 이름에서는 끝의 `/`와 `.git`을 제거한다. 식별 결과가 비어 있거나 명백히 상위 공용 폴더명이면 이름을 요청한다.
- Notion 데이터베이스 ID/URL은 선택 입력이다. 입력이 없으면 `"null"` 문자열을 입력 자리로 남긴다. 기존에 유효한 ID/URL이 있으면 유지한다.

## 설정

1. 기존 `.tasklog.json`이 있으면 JSON 형식과 `project` 타입을 검사한다. 손상된 파일은 덮어쓰지 않는다. 유효하면 기존의 다른 필드는 유지한다.
2. 새 파일을 만들거나 기존 파일에 필드가 빠져 있으면 아래 형식으로 저장한다. `"null"`은 사용자가 ID 또는 URL을 넣을 입력 자리이며 실제 Notion ID가 아니다. 기존의 JSON `null`도 입력 대기 상태로 취급한다.

```json
{
  "project": "billing-api",
  "notion_database_id": "null"
}
```

3. 사용자 지정 ID/URL 또는 기존 유효값을 Notion MCP로 fetch해 실제 **데이터베이스**인지 확인한다. 검증에 실패하면 기존 값을 덮어쓰지 않고 이유를 보고한다. 일반 페이지, 템플릿, 데이터 소스의 `collection://` ID는 이 필드에 저장하지 않는다. 한국어 `LLM Logs`와 영어 템플릿 모두 데이터베이스의 실제 속성명·타입·상태 옵션을 읽는다. 한국어 `이름`·`완료`·`진행 중`이나 영어 `Name`·`Done`·`In Progress`라는 이름을 필수 조건으로 강제하지 않는다. 기존 속성명을 바꾸지 않는다.
4. 요청 없이 Notion 데이터베이스를 새로 만들거나 스키마를 변경하지 않는다. MCP 연결이 없어 ID를 검증할 수 없으면 입력 자리 `"null"`을 유지한다. 비밀번호나 액세스 토큰은 파일에 넣지 않는다.
5. 유효한 UTF-8 JSON으로 저장하고 다시 읽어 확인한다. 같은 값으로 재실행해도 파일을 불필요하게 바꾸지 않는다. 완료 후 프로젝트명, 파일 경로, `notion_database_id`가 입력 대기 상태인지 연결 완료 상태인지 보고한다.
