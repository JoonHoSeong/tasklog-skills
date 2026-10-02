# Notion 작업 기록 스킬 / Notion Work Log Skills

## 한국어

### 설정

`notion-init-work`는 프로젝트 설정, `notion-log-work`는 작업 기록, `notion-resume-work`는 진행 중 작업 복원, `notion-monthly-report`는 선택한 기록을 프로젝트별 월간 보고서로 정리할 때 사용한다. Codex, Kiro CLI, agy의 설치 위치와 스킬 전문은 [설치 안내](INSTALL_KIRO_CODEX_AGY.md)에 있다. 각 도구에 Notion MCP 연결이 필요하다.

프로젝트 루트의 `.tasklog.json` 템플릿:

```json
{
  "project": "billing-api",
  "notion_database_id": "null"
}
```

`"null"`은 문자열 입력 자리다. 기록 전에 **기록할 Notion 데이터베이스의 URL 전체 또는 데이터베이스 ID**로 교체한다. Notion에서 대상 데이터베이스를 열고 [`공유` → `링크 복사`](https://www.notion.com/en-gb/help/share-your-work)로 URL을 얻는다. URL을 그대로 넣어도 되고, URL 경로의 데이터베이스 페이지 ID만 넣어도 된다. `?v=` 뒤의 값은 뷰 ID이므로 사용하지 않는다. 데이터베이스 안의 템플릿이나 일반 페이지 링크도 사용하지 않는다. 스킬이 MCP로 실제 데이터베이스인지 검증한다. ID 탐색 순서는 명시적 입력 → `.tasklog.json` → `NOTION_WORK_LOG_DATABASE_ID`다. 문자열 `"null"`, JSON `null`, 빈 값은 미설정으로 취급한다.

### 속성과 언어별 매핑

스킬은 연결된 데이터베이스의 실제 속성명·타입·Status 옵션·데이터 소스 ID를 확인한다. 영어 열은 예시이며 실제 영어 템플릿의 이름이 다르면 그 스키마를 따른다.

| 용도 / Purpose | 필수 타입 / Type | 현재 LLM Logs | 영어 예시 / English example |
| --- | --- | --- | --- |
| 제목 / Title | Title | `이름` | `Name` |
| 프로젝트 / Project | Select | `Project` | `Project` |
| 날짜 / Date | Date | `Date` | `Date` |
| 분류 / Category | Select | `Category` | `Category` |
| 작업 방식 / Work type | Select | `Type` | `Type` |
| 사용 모델 / LLM model | Select | `LLM` | `LLM` 또는 `Model` |
| 상태 / Status | Status | `Status` | `Status` |
| 보고서 포함 / Include in report | Checkbox | `Include in Report` | `Include in Report` |

현재 `LLM Logs`의 완료/진행 중 옵션은 `완료`/`진행 중`이다. 영어 템플릿의 예시는 `Done`/`In Progress`다. 스킬은 가능하면 Status 그룹 `complete`/`in_progress`로 식별하고, 그룹 정보가 없으면 의미가 분명한 이름을 사용한다. 여러 옵션이 대응되거나 의미가 불분명하면 확인을 요청한다. `시작 전`/`Not Started`는 완료나 진행 중에 해당하지 않는다.

Codex, Kiro CLI, agy는 모두 동일한 Category 기준을 적용한다. 주된 산출물 한 가지를 선택하고, 여러 범주에 걸치면 판단 이유를 본문에 남긴다.

| Category | 주된 산출물 |
| --- | --- |
| Backend | API, 비즈니스 로직, 데이터 접근 코드 |
| Infra | 클라우드·네트워크·배포 인프라, IaC |
| Workflow | CI/CD 절차, 개발 도구 사용 흐름, 반복 작업 자동화 |
| Troubleshooting | 기존 오류의 원인 분석과 복구 |
| Architecture | 구성요소 경계, 데이터 구조, 인터페이스, 시스템 설계 결정 |

`Type`은 LLM-Assisted 또는 Manual이다. LLM이 작업이나 기록 분석에 관여했다면 `Type=Manual`이어도 **활성 모델의 정확한 ID**를 모델 Select 속성에 기록한다. 사용자 `--model` 지정, 현재 세션 메타데이터·실행 옵션, 실제 적용된 CLI 설정 순서로 확인한다. 전역 기본 설정, 제품명, 모델 계열만으로 정확한 ID를 추측하지 않는다. 확인할 수 없으면 요약을 준비한 뒤 기록 전에 모델 ID를 요청한다. 여러 모델을 썼다면 주된 모델을 Select에, 다른 모델과 역할을 본문에 적는다. 모델용 Select 속성이 없는 템플릿에서는 `LLM` Select를 추가한다. `생성일` Created time은 Notion이 채운다.

기존 Select 옵션 중 같은 의미의 값이 있으면 사용한다. `Project`, `Category`, `Type`, 모델용 Select에 필요한 옵션이 없으면 **기록 스킬이 Notion MCP로 자동 추가한 뒤 기록**한다. [Notion의 Select 옵션 갱신 규칙](https://developers.notion.com/reference/update-data-source-properties)에 따라 기존 옵션과 설명을 보존할 수 있는 경우에만 수정하고, 갱신 결과를 다시 확인한다. MCP의 스키마 수정 권한이 없거나 옵션 추가가 실패하면 기록을 중단하고 원인을 보고한다. `Include in Report` 기본값은 false다.

`.tasklog.json`에는 **데이터베이스** ID/URL을 넣고 MCP 생성·조회에는 해당 데이터베이스에서 조회한 **데이터 소스** ID를 사용한다. 데이터 소스 ID를 사용자가 설정 파일에 입력할 필요는 없다. 스킬의 JSON 예시는 한국어 데이터베이스 기준이다. 다른 데이터베이스에서는 속성 키, 상태 옵션, 날짜 필드명, 데이터 소스 ID를 실제 값으로 치환한다. Notion 화면 언어만 바뀌어도 기존 속성명이 번역된다고 가정하지 않는다.

### 사용 순서

1. `notion-init-work`로 설정 파일을 만들고 `"null"`을 실제 데이터베이스 ID/URL로 교체한다.
2. `notion-log-work`로 완료 기록 또는 진행 중 체크포인트를 남긴다.
3. 새 세션에서 `notion-resume-work`로 같은 프로젝트의 최신 진행 중 기록을 읽는다.
4. `notion-monthly-report`로 `Include in Report`가 선택된 기록을 기간별·프로젝트별 보고서로 작성한다.

기록이 실패하면 데이터베이스 접근 권한, 데이터베이스 ID와 데이터 소스 ID 구분, 속성 타입, Status 옵션, Select 옵션 수정 권한을 확인한다. 자동 스키마 변경 범위는 이번 기록에 필요한 Select 옵션 추가로 제한한다.

## English

### Setup

Use `notion-init-work` to configure a project, `notion-log-work` to save work, `notion-resume-work` to restore an in-progress checkpoint, and `notion-monthly-report` to create a project-organized report from selected entries. The [installation guide](INSTALL_KIRO_CODEX_AGY.md) contains Codex, Kiro CLI, and agy paths and complete skill files. Each tool needs its own Notion MCP connection.

Create `.tasklog.json` in the project root:

```json
{
  "project": "billing-api",
  "notion_database_id": "null"
}
```

`"null"` is a string placeholder. Replace it with the **full URL or ID of the Notion database where logs should be stored**. Open that database in Notion and use [`Share` → `Copy link`](https://www.notion.com/en-gb/help/share-your-work). You may paste the full URL or just the database page ID from its path. The value after `?v=` is a view ID; do not use it. Do not use a template or ordinary page URL from inside the database. The skill verifies the target through MCP. ID precedence is explicit input → `.tasklog.json` → `NOTION_WORK_LOG_DATABASE_ID`. String `"null"`, JSON `null`, and empty values mean “not configured.”

### Properties and localization

The skills fetch the database's actual property names, types, Status options, and data source ID. This table maps the current Korean `LLM Logs` schema to a **possible** English template. Use the actual schema if its names differ.

| Purpose | Required property type | Current LLM Logs | English example |
| --- | --- | --- | --- |
| Title | Title | `이름` | `Name` |
| Project | Select | `Project` | `Project` |
| Date | Date | `Date` | `Date` |
| Category | Select | `Category` | `Category` |
| Work type | Select | `Type` | `Type` |
| LLM model | Select | `LLM` | `LLM` or `Model` |
| Status | Status | `Status` | `Status` |
| Include in report | Checkbox | `Include in Report` | `Include in Report` |

The current Korean completion/in-progress options are `완료`/`진행 중`; `Done`/`In Progress` are English examples. Prefer the Status groups `complete`/`in_progress` when available. Otherwise use unambiguous option names. Ask if multiple options could match or their meaning is unclear. `Not Started`/`시작 전` means neither completed nor in progress.

Codex, Kiro CLI, and agy use the same five Category values. Choose one based on the main deliverable and explain borderline choices in the entry.

| Category | Main deliverable |
| --- | --- |
| Backend | APIs, business logic, data access code |
| Infra | Cloud, network, deployment infrastructure, IaC |
| Workflow | CI/CD procedures, development tool flows, repeatable automation |
| Troubleshooting | Root cause analysis and repair of an existing failure |
| Architecture | Component boundaries, data structures, interfaces, system design decisions |

Type is LLM-Assisted or Manual. If an LLM contributed to the work or analyzed it for logging, record the **exact active model ID** even when Type is Manual. Resolve it from explicit `--model` input, current session metadata or launch options, then CLI configuration confirmed active for this session. A product name, model family, or unrelated global default is insufficient. If the ID cannot be confirmed, prepare the summary and request the model ID before writing. For multiple models, put the primary one in Select and list the others with their roles in the body. Add an `LLM` Select property if the template lacks a model Select. `생성일` is a read-only created-time field in the current database.

Prefer an equivalent existing Select option. If a required `Project`, `Category`, `Type`, or model option is missing, **the logging skill adds it through Notion MCP before writing the entry**. It follows [Notion's Select option update rules](https://developers.notion.com/reference/update-data-source-properties) to preserve existing options and descriptions, then refetches the schema. If the MCP lacks permission or cannot safely add an option, it stops and reports the cause. `Include in Report` defaults to false.

Store the **database** ID/URL in `.tasklog.json`; the skill fetches the **data source** ID needed for MCP creation and queries. Users do not need to enter a data source ID in the config file. The skill payloads illustrate a Korean database. For another database, substitute its actual property keys, status values, date field names, and data source ID. Changing the Notion UI language does not imply that existing property names changed.

### Workflow

1. Run `notion-init-work`, then replace `"null"` with the target database ID/URL.
2. Run `notion-log-work` to save completed work or an in-progress checkpoint.
3. In a later session, run `notion-resume-work` to load the project's latest in-progress entry.
4. Run `notion-monthly-report` to write a period-based report grouped by project from entries marked `Include in Report`.

If writing fails, check database access, database versus data source IDs, property types, Status options, and permission to update Select options. Automatic schema changes are limited to Select options required for the current log entry.

## 라이선스 / License

MIT License. See [LICENSE](LICENSE).
