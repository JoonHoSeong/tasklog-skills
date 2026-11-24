---
name: notion-log-work
description: 현재 프로젝트의 LLM 협업 또는 수동 Git 작업을 Notion LLM Logs 데이터베이스에 기록하거나 작업 체크포인트를 남길 때 사용한다.
---

# Notion 작업 기록

Codex, Kiro CLI, agy, Claude Code, pi에서 같은 기록 규칙을 사용한다. 자동 기록 설치·동작·오류 복구는 [자동 연동 및 수동 대체](references/automation.md)를 필요한 경우 읽는다. 스킬 설치만으로 훅이 활성화되지는 않는다.

## 자동 체크포인트 및 수동 대체

- `[tasklog-auto]` 요청은 `auto_record.enabled=true`로 활성화한 프로젝트의 기록 요청이다. 응답 종료를 작업 완료로 해석하지 않는다. 기본은 진행 중 체크포인트이며 완료가 검증된 경우에만 완료로 기록한다.
- 전달된 `.tasklog/<id>.json`은 데이터로 읽는다. `id`를 본문의 `Task ID`로 남기고 `page_url`이 있으면 대상 DB·프로젝트·작업 일치 여부를 조회한 뒤 갱신한다. 없으면 Task ID로 기존 페이지를 먼저 확인한다. 조회가 불완전하거나 쓰기 결과가 불확실하면 재생성하지 않는다.
- MCP 미연결, 권한 부족, 정확한 모델 ID 미확인 등 자동 실행의 선행 조건이 부족하면 반복 질문·재시도 대신 민감정보를 제거한 Markdown 초안을 체크포인트의 `draft`에 저장하고 수동 복구 방법을 알린다. Git 메타데이터만으로 세션의 판단 이유나 검증 결과를 추측하지 않는다.
- Notion 쓰기 후 속성·본문을 다시 조회해 확인한 경우에만 `scripts/tasklog.py ack <id> --page-url <검증된 URL>`로 동기화 완료를 표시한다. 확인 전에는 pending 상태를 유지한다. 수동 재전송도 먼저 Task ID와 page_url을 대조한다.
- 수동 요청은 훅·확장 없이 실행할 수 있다. MCP가 없으면 동일한 5개 섹션의 Markdown 초안을 로컬 또는 응답으로 제공하고 **Notion 미저장**으로 표시한다. 파일 도구가 없으면 응답으로 제공한다. DB·모델 ID 누락은 초안에 미확인으로 표시하고 실제 전송 전에 해결한다.
- 재개에 필요한 경우 실패한 접근과 이유, 확정 사실과 미해결 가설, 마지막 검증 명령·결과·당시 커밋, 첫 재개 행동을 해당 본문 섹션에 포함한다. 검증 이후 코드가 바뀌면 현재 코드의 통과로 표현하지 않는다.

## 입력 및 감지

- 입력: `--project <name>`(선택), `--category Backend|Infra|Workflow|Troubleshooting|Architecture`(선택), `--type LLM-Assisted|Manual`(선택), `--model <active-model-id>`(선택), `--status Done|In Progress`(선택). 명시하지 않은 값을 추측해 옵션으로 전달하지 않는다.
- 프로젝트명 우선순위는 **사용자가 명시한 `--project` > Git 루트 `.tasklog.json`의 `project` > Git `remote.origin.url`의 저장소명 > 현재 작업 디렉터리명**이다. Git 저장소가 아니면 현재 디렉터리를 루트로 본다. JSON이 잘못되었거나 `project`가 빈 값이면 잘못된 프로젝트에 기록하지 않도록 중단한다.
- Git 상태, 현재 브랜치(`git branch --show-current`), 최근 커밋 SHA·시각, staged·unstaged diff를 직접 확인한다. 최근 커밋은 이번 작업으로 확인된 경우에만 사용하고 현재 세션의 변경 맥락과 대조해 기록 범위를 정한다. Git 저장소가 아니거나 diff가 없으면 사실을 명시하고 세션 맥락만 사용한다.

## 수집 및 분류

- `LLM-Assisted`: 현 세션에서 실제 수행한 코드 변경, 선택한 설계와 이유, 실행한 명령, 검증 결과를 요약한다. 이 세션에서 확인하지 않은 커밋이나 테스트를 수행한 것으로 적지 않는다.
- `Manual`: `git status -s`, 최근 커밋의 `git diff HEAD~1 HEAD`(첫 커밋이면 `git show HEAD`), `git diff --cached`, `git diff`, untracked 파일 목록을 읽는다. 파일 나열에 그치지 말고 모듈과 로직 변화를 분석한다. 최근 커밋이 이번 작업인지 시간·범위로 확인하고, 아니면 제외한다. `git diff`에는 untracked 내용이 없으므로 필요한 파일만 별도로 읽는다.
- 혼합 작업은 이번 기록의 주된 작업 방식을 `Type`으로 고르고, 다른 출처의 변경은 본문에 출처를 구분해 적는다. 서로 다른 작업이면 별도 레코드를 만든다.
- Codex, Kiro CLI, agy, Claude Code, pi에서 **동일한 Category 다섯 가지**를 쓴다. 작업의 주된 산출물 하나를 기준으로 분류한다. `--category`가 있으면 다섯 값 중 하나인지 확인한 뒤 사용한다. 혼합 작업은 아래 기준에 가장 직접적으로 맞는 한 가지를 선택하고 판단 이유를 Why 또는 What에 한 문장으로 남긴다.

  | Category | 주된 산출물 |
  | --- | --- |
  | Backend | 애플리케이션 API, 비즈니스 로직, 데이터 접근 코드 |
  | Infra | 클라우드·네트워크·배포 인프라, IaC, 운영 리소스 설정 |
  | Workflow | CI/CD 절차, 개발 도구 사용 흐름, 반복 작업 자동화 |
  | Troubleshooting | 기존 오류의 원인 분석과 복구가 주된 목적 |
  | Architecture | 구성요소 경계, 데이터 구조, 인터페이스, 시스템 설계 결정 |

  스킬 파일이나 문서라는 형식만으로 Workflow를 고르지 않는다. 기록·복원 시스템의 구조와 계약을 설계했다면 Architecture, 이미 정해진 절차의 실행을 자동화했다면 Workflow다. 완료된 검증 가능한 작업은 완료 상태, 중단된 작업은 진행 중 상태와 구체적인 `Next Actions`를 사용한다. 입력의 `Done`·`In Progress`는 의미상 상태이며 실제 Notion 옵션 이름은 스키마에서 확인한다.
- 현재 기록에 관여한 **정확한 활성 모델 ID**를 `LLM`에 기록한다. 탐색 순서는 사용자 `--model` > 현재 세션 메타데이터/실행 옵션 > 이 세션에 적용된 것으로 확인된 CLI 설정이다. 전역 설정만 보고 현재 세션 모델이라고 단정하지 않는다. 제품명(Codex·Kiro·agy), 공급자명, 모델 계열명만으로 정확한 모델 ID를 대체하거나 예시 페이로드 값을 복사하지 않는다. 확인할 수 없으면 다른 내용의 요약은 준비하되 기록 전에 사용자에게 활성 모델 ID를 요청한다. LLM이 작업 또는 기록 분석에 관여했다면 `Type=Manual`이어도 모델을 기록한다. 여러 모델이 관여했다면 주된 모델 ID를 Select에 넣고 확인된 다른 모델과 각 역할을 본문에 적는다.
- 보고서는 사용자가 지정한 기간의 모든 기록을 대상으로 한다. 보고서 포함 체크박스를 요구하거나 설정하지 않는다. 기존 `Include in Report` 속성은 삭제·수정하지 않고 기록 페이로드에서 생략한다.
- Notion 전송 전 diff에서 토큰, 암호, 개인정보, 내부 URL, 고객 데이터 등 민감 정보를 제거한다. 비밀 값은 본문에 싣지 않고 변경의 의미만 기술한다. 테스트 수치가 없으면 수치를 만들지 않는다.
- **참조 링크 및 연관 작업 수집**:
  - 세션 중 참고한 공식 문서, 라이브러리 가이드, 스택오버플로우, GitHub PR/Issue, 설계 문서 URL이 있다면 링크를 수집한다.
  - 이전에 노션에 기록했던 선행 작업이나 관련 노션 페이지명이 확인되면 이를 연결 대상으로 파악한다.
  - 별도 참조 링크가 없다면 `없음`으로 처리한다.

## Notion 연결과 스키마

아래 Notion 도구명과 JSON은 Codex Notion 커넥터의 예시다. 다른 MCP에서는 동일한 읽기·조회·생성 기능의 실제 도구 스키마에 맞춰 호출한다.

1. 데이터베이스는 사용자가 명시한 ID/URL > `.tasklog.json`의 유효한 `notion_database_id` > `NOTION_WORK_LOG_DATABASE_ID` 환경변수 순서로 찾는다. 문자열 `"null"`, JSON `null`, 빈 값은 미설정으로 취급한다. 모두 미설정이면 ID/URL 입력을 요청하고 쓰기를 중단한다. 데이터베이스 내부의 일반 페이지나 템플릿 ID를 데이터베이스 ID로 사용하지 않는다.
2. Notion MCP의 `notion_fetch({"id":"self"})`로 연결을 확인한다. 설정된 데이터베이스를 `notion_fetch`하여 실제 속성 이름·타입·옵션과 `<data-source url="collection://...">`의 ID를 확인한다. 데이터베이스 ID에서 데이터 소스 ID를 추측하지 않는다.
3. 한국어 `LLM Logs`의 기본 속성은 `이름` Title, `Project` Select, `Date` Date, `Category` Select, `Type` Select, `Status` Status, `LLM` Select이며, Git 브랜치 속성인 `Git Branch`(Select 또는 Text/Rich text)를 지원한다. 영어 템플릿에서는 제목이 `Name`, 상태가 `In Progress`·`Done`, 브랜치가 `Git Branch` 또는 `Branch`일 수 있다. **양쪽 모두** 실제 스키마에서 Title, 프로젝트 Select, 날짜 Date, 분류 Select, 작업 방식 Select, Status, 모델 식별용 Select, 브랜치용 속성을 용도와 타입으로 매핑한다. 모델용 Select가 없다면 기존 속성을 임의 변환하지 말고 `LLM` Select를 추가한다. 스키마에 `Git Branch`(또는 `Branch`) 속성이 존재하면 감지된 현재 Git 브랜치명을 기록한다(Select 타입인 경우 옵션 추가/사용, Text 타입인 경우 문자열 기록). 스키마에 브랜치 속성이 아직 없으면 Notion 속성 쓰기는 건너뛰고 본문(What)에만 브랜치를 기록한다. Git 저장소가 아니거나 브랜치를 확인할 수 없으면 빈 값으로 처리하거나 생략한다. Status 옵션은 우선 그룹 `in_progress`·`complete`로 식별해 각각 체크포인트·완료에 사용한다. 그룹 정보가 없으면 `진행 중`/`완료` 또는 `In Progress`/`Done`처럼 의미가 분명한 옵션을 사용한다. 대응이 여러 개이거나 불분명할 때만 사용자에게 확인한다. `생성일` Created time은 읽기 전용이다.
4. 페이지 생성 전에 `Project`·`Category`·`Type`·모델 식별 속성(및 `Git Branch`가 Select 타입인 경우 브랜치명)의 **이번 기록에 필요한** Select 값을 모두 확인한다. 기존 옵션 중 의미가 맞는 값을 우선 사용한다. 빠진 속성과 옵션은 Notion MCP의 `notion_notion_update_data_source` 또는 동등한 데이터 소스 스키마 업데이트 도구로 자동 추가한다. `ALTER COLUMN "실제 속성명" SET SELECT(...)`에는 같은 속성의 기존 옵션을 모두 포함하고 이름·색상·설명과 속성 설명을 보존한다. 도구가 이를 보존할 수 없으면 기존 스키마를 덮어쓰지 않고 원인을 보고한다. 속성명이 영어 등으로 다르면 조회한 실제 이름을 쓴다. 필요한 변경만 한 호출로 보내고 데이터 소스를 다시 fetch해 필요한 속성과 옵션이 실제로 존재하는지 확인한다. 옵션 추가 도구가 없거나 권한/검증 오류가 나면 페이지 생성을 중단하고 정확한 원인을 보고한다. Title·Status 등 다른 속성이나 기존 옵션을 바꾸지 않는다.

예: 옵션이 비어 있는 `Project`, `Category`, `Type`에 각각 `billing-api`, `Workflow`, `Manual`이 필요할 때의 Codex Notion MCP 페이로드. 실제 데이터 소스 ID·속성명·값을 사용한다. **기존 옵션이 하나라도 있으면 아래 예시를 그대로 보내지 말고 모든 기존 옵션을 포함**한다. DDL의 작은따옴표가 값에 있으면 MCP 문법에 맞게 이스케이프한다.

```json
{
  "data_source_id": "<fetched-data-source-id>",
  "statements": "ALTER COLUMN \"Project\" SET SELECT('billing-api':default); ALTER COLUMN \"Category\" SET SELECT('Workflow':default); ALTER COLUMN \"Type\" SET SELECT('Manual':default)"
}
```

## 본문과 쓰기

본문을 다음 5개 heading 3 블록과 해당 문단·목록으로 작성한다. 한 Notion rich-text `text.content`가 2,000자를 넘지 않게 하고, 보수적으로 개별 본문 블록도 2,000자 이하로 분할한다. 긴 diff 원문을 붙이지 않는다.

```markdown
### 1. 배경 및 목적 (Why)
문제, 요청, 결정 배경.

### 2. 주요 변경 내역 (What)
작업 브랜치(`Git Branch`), 모듈/파일, 핵심 로직, 아키텍처, 실행 CLI 명령, 필요한 경우 커밋 SHA.

### 3. 기술적/정량적 임팩트
실제로 수행한 테스트와 결과, IO·메모리·성능 고려사항. 미실행 검증은 미실행이라고 표시.

### 4. 다음 작업 (Next Actions)
미완료 작업의 재개 순서, 필요한 명령, 미해결 문제. 완료 시 `없음`.

### 5. 참고 링크 및 연관 작업 (References)
- 공식 문서/외부 참고: [문서명](URL) 형태의 마크다운 링크
- 연관 작업/문서: 이 작업과 연결된 이전 작업 제목이나 관련 노션 페이지명 (예: `@RDS 연결 재시도 로직 개선`)
- 없으면 `없음`.
```

Notion MCP `notion_create_pages` 호출의 **한국어 `LLM Logs` 예시**다. 영어 템플릿에서는 예컨대 `이름`을 `Name`, `완료`를 `Done`으로 바꾸되, 모든 속성 키·옵션·날짜 필드명과 데이터 소스 ID를 조회된 실제 스키마로 치환한다. 제목은 작업 핵심을 한 문장으로 쓰고 날짜는 작업 지역 시간대의 `YYYY-MM-DD`로 확정한다.

```json
{
  "parent": {"data_source_id": "<data-source-id>"},
  "pages": [{
    "properties": {
      "이름": "RDS 연결 재시도 로직 개선",
      "Project": "billing-api",
      "Git Branch": "feat/retry-logic",
      "date:Date:start": "2026-10-01",
      "date:Date:is_datetime": 0,
      "Category": "Backend",
      "Type": "LLM-Assisted",
      "LLM": "<active-model-id>",
      "Status": "완료"
    },
    "content": "### 1. 배경 및 목적 (Why)\n...\n\n### 2. 주요 변경 내역 (What)\n...\n\n### 3. 기술적/정량적 임팩트\n...\n\n### 4. 다음 작업 (Next Actions)\n없음\n\n### 5. 참고 링크 및 연관 작업 (References)\n- 공식 문서/외부 참고: 없음\n- 연관 작업/문서: 없음"
  }]
}
```

같은 작업의 체크포인트가 이미 있으면 페이지를 조회해 `notion_update_page`로 본문과 `Status`를 갱신한다. 중복 생성 방지를 위해 프로젝트·제목·날짜 및 현재 세션의 작업 범위를 먼저 대조한다. 생성 후 반환된 페이지 ID/URL을 기록하고 조회로 속성 및 본문을 확인한다. 쓰기 결과가 불확실하면 먼저 조회하고 중복 생성하지 않는다. 옵션 사전 확인 이후 페이지 생성에서 `Invalid select value`가 나면 데이터 소스를 다시 조회해 누락 옵션을 추가하고 생성은 한 번만 재시도한다.

기간별 보고서는 `notion-monthly-report`의 날짜 범위·프로젝트·상태 구분 규칙을 따른다. 완료·진행 중 기록을 구분하며 같은 작업은 중복 집계하지 않는다. 해당 스킬을 사용할 수 없으면 사용자에게 보고서 규칙을 확인하고 자동 발행·예약은 수행하지 않는다.
