# Notion 작업 기록 스킬 / Notion Work Log Skills

[한국어](#한국어) | [English](#english)

AI와 함께 수행한 작업의 이유, 변경 사항, 검증 결과와 다음 할 일을 Notion에 기록하고 다음 세션에서 복원하는 네 가지 스킬입니다.

Four skills to save the reasoning, changes, verification, and next steps from AI-assisted work in Notion, then resume in a later session.

> **Notion에 기록·조회하려면 사용하는 AI 도구에 Notion MCP를 반드시 설치 또는 연결하고 인증해야 합니다. 스킬 설치만으로 Notion MCP가 설정되지 않습니다.**
>
> **Notion MCP must be installed or connected and authenticated in your AI agent to read or write Notion. Installing these skills does not configure Notion MCP.**

## 한국어

### 제공 기능

| 스킬 | 역할 |
| --- | --- |
| `notion-init-work` | 프로젝트명과 작업 기록용 Notion 데이터베이스 설정 |
| `notion-log-work` | Why / What / Impact / Next Actions / References 형식으로 작업·체크포인트 기록 |
| `notion-resume-work` | 같은 프로젝트의 최신 진행 중 기록에서 맥락과 다음 작업 복원 |
| `notion-monthly-report` | 지정 기간의 전체 작업 기록을 프로젝트별 보고서로 정리 |

Codex, Claude Code, Kiro CLI, agy(Antigravity CLI), pi coding agent용 연결을 제공합니다. 도구별 실제 검증 범위는 [검증 결과](VALIDATION.md)를 확인하세요. Claude Code의 실제 실행은 아직 검증하지 않았습니다.

### 1. 준비 사항

- 사용할 AI 도구와 모델 접근 권한
- **해당 도구에 연결·인증된 Notion MCP**와 대상 데이터베이스의 읽기·쓰기 권한
- Git과 `npx skills` 실행 환경: Node.js 22.20 이상 ([설치 도구 공식 안내](https://github.com/vercel-labs/skills))
- 자동 기록을 사용할 경우 macOS/Linux, Python 3.10 이상, Git 저장소. Windows에서는 수동 스킬 사용 경로를 제공합니다.

Notion MCP가 없으면 Notion 저장·조회·최신 기록 복원·보고서 조회가 작동하지 않습니다. 로컬 프로젝트 설정, Markdown 초안 보관과 제공된 기록에서의 복원만 사용할 수 있습니다.

### 2. 스킬 설치

여러 프로젝트에서 사용하려면 전역으로 설치합니다.

```bash
npx skills add JoonHoSeong/tasklog-skills -g
```

대화형 설치에서는 네 스킬과 사용할 AI 도구를 선택합니다. 실행 환경에 따라 감지한 도구가 자동 선택될 수 있으므로 설치 요약의 대상을 확인한 뒤 해당 도구를 다시 시작합니다. 프로젝트 한 곳에만 설치하려면 `-g`를 생략합니다. 설치 도구가 대상 도구를 지원하지 않거나 탐색에 실패하면 [수동 배치 안내](INSTALL_KIRO_CODEX_AGY.md)를 참고해 네 스킬 **폴더 전체**를 배치합니다. `scripts/`와 `references/`도 함께 유지해야 합니다.

`-g`는 사용자 전역 설치 범위이며 **모든 CLI 도구에 자동 설치한다는 뜻은 아닙니다**. 설치 대상은 지원되는 도구 중 선택한 도구입니다. 다섯 도구를 명시하려면 다음과 같이 실행합니다.

```bash
npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent codex claude-code kiro-cli antigravity-cli pi
```

설치 도구의 `kiro-cli`·`antigravity-cli` 이름과 자동 기록 스크립트의 `kiro`·`agy` 이름은 다릅니다. `--all`을 추가하면 설치 도구가 지원하는 모든 대상에 모든 스킬을 설치하지만, 모든 LLM CLI의 실행 호환성을 보장하지 않습니다. 각 도구의 Notion MCP 연결과 자동 기록 훅·확장 설치는 여전히 별도입니다. [공식 지원 목록](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)을 확인하세요.

설치 상태와 업데이트를 확인합니다.

```bash
npx skills list -g
npx skills check
npx skills update
```

명령 옵션은 [skills 설치 문서](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)를 참고하세요.

#### 특정 도구에 설치되지 않았을 때

누락된 도구에 해당하는 명령만 실행합니다. 각 명령은 네 스킬을 모두 해당 도구의 전역 범위에 설치합니다. 기존 스킬을 직접 수정했다면 다시 설치하기 전에 변경 내용을 별도로 보관하세요.

| 도구 | 개별 설치 명령 |
| --- | --- |
| Codex | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent codex` |
| agy (Antigravity CLI) | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent antigravity-cli` |
| Kiro CLI | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent kiro-cli` |
| pi | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent pi` |
| Claude Code | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent claude-code` |

설치 목록은 대상 도구별로 확인할 수 있습니다.

```bash
npx skills list -g --agent codex
npx skills list -g --agent antigravity-cli
npx skills list -g --agent kiro-cli
npx skills list -g --agent pi
npx skills list -g --agent claude-code
```

목록에 보여도 현재 CLI 세션에 로딩됐다는 의미는 아닙니다. 해당 도구를 다시 시작한 뒤 `notion-init-work 스킬을 찾아서 읽어줘. 아직 파일이나 Notion은 변경하지 마.`라고 요청해 실제 탐색을 확인합니다. Kiro의 사용자 정의 에이전트는 별도로 스킬 리소스 설정이 필요할 수 있습니다. [Kiro 안내](https://kiro.dev/docs/cli/custom-agents/configuration-reference/#skill-resources)를 확인하세요.

개별 설치도 실패하면 저장소의 네 폴더(`notion-init-work`, `notion-log-work`, `notion-resume-work`, `notion-monthly-report`)를 다음 전역 경로 아래에 폴더째 복사합니다. `SKILL.md`만 복사하면 자동 기록용 `scripts/`와 `references/`가 누락됩니다. 같은 이름의 폴더가 있으면 내용을 비교하고 기존 사용자 변경을 보관한 뒤 갱신합니다.

| 도구 | 수동 배치할 상위 폴더 |
| --- | --- |
| Codex | `~/.agents/skills/` |
| agy (Antigravity CLI) | `~/.gemini/config/skills/` |
| Kiro CLI | `~/.kiro/skills/` |
| pi | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |

예를 들어 pi의 기록 스킬은 `~/.agents/skills/notion-log-work/SKILL.md`와 같은 위치에 둡니다. 수동 복사한 스킬은 설치 도구의 업데이트 관리 대상에 등록되지 않을 수 있으므로 직접 갱신합니다. 배치 후 도구를 다시 시작하고 탐색을 확인한 다음 Notion MCP 연결과 필요한 자동 기록 설정을 진행합니다.

### 3. Notion MCP 연결 — 필수

사용할 AI 도구마다 Notion 커넥터·플러그인 또는 MCP 서버를 연결하고 Notion 워크스페이스 인증을 완료합니다. 공식 원격 MCP 주소는 `https://mcp.notion.com/mcp`입니다. 도구별 설정은 [Notion 공식 MCP 연결 안내](https://developers.notion.com/guides/mcp/get-started-with-mcp)를 따르세요.

대상 데이터베이스를 읽고 페이지를 생성·수정할 수 있어야 합니다. 필요한 Select 옵션이 없으면 스키마 수정 권한도 필요합니다. 이미 연결된 Notion MCP가 있으면 중복 설치 대신 해당 도구에서 접근 권한을 확인하세요. 다른 AI 도구에 연결된 MCP 인증이 자동 공유된다고 가정하지 않습니다.

AI 도구에 다음과 같이 요청해 연결을 확인합니다.

> Notion MCP로 이 데이터베이스 URL의 속성과 데이터 소스를 읽어줘. 아직 페이지를 만들거나 수정하지는 마.

데이터베이스를 실제로 읽을 수 있음을 확인한 뒤 프로젝트를 설정합니다. MCP 서버 설치·로그인·권한 설정은 이 저장소의 스크립트가 대신하지 않습니다.

### 4. 프로젝트 설정

프로젝트 루트의 `.tasklog.json` 템플릿:

```json
{
  "project": "billing-api",
  "notion_database_id": "null"
}
```

`"null"`은 문자열 입력 자리다. 기록 전에 **기록할 Notion 데이터베이스의 URL 전체 또는 데이터베이스 ID**로 교체한다. Notion에서 대상 데이터베이스를 열고 [`공유` → `링크 복사`](https://www.notion.com/en-gb/help/share-your-work)로 URL을 얻는다. URL을 그대로 넣어도 되고, URL 경로의 데이터베이스 페이지 ID만 넣어도 된다. `?v=` 뒤의 값은 뷰 ID이므로 사용하지 않는다. 데이터베이스 안의 템플릿이나 일반 페이지 링크도 사용하지 않는다. 스킬이 MCP로 실제 데이터베이스인지 검증한다. ID 탐색 순서는 명시적 입력 → `.tasklog.json` → `NOTION_WORK_LOG_DATABASE_ID`다. 문자열 `"null"`, JSON `null`, 빈 값은 미설정으로 취급한다.

### 데이터베이스 속성과 언어별 매핑

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
| Git 브랜치 / Git branch (선택) | Select 또는 Text | `Git Branch` | `Git Branch` 또는 `Branch` |

현재 `LLM Logs`의 완료/진행 중 옵션은 `완료`/`진행 중`이다. 영어 템플릿의 예시는 `Done`/`In Progress`다. 스킬은 가능하면 Status 그룹 `complete`/`in_progress`로 식별하고, 그룹 정보가 없으면 의미가 분명한 이름을 사용한다. 여러 옵션이 대응되거나 의미가 불분명하면 확인을 요청한다. `시작 전`/`Not Started`는 완료나 진행 중에 해당하지 않는다.

Codex, Kiro CLI, agy, Claude Code, pi는 모두 동일한 Category 기준을 적용한다. 주된 산출물 한 가지를 선택하고, 여러 범주에 걸치면 판단 이유를 본문에 남긴다.

| Category | 주된 산출물 |
| --- | --- |
| Backend | API, 비즈니스 로직, 데이터 접근 코드 |
| Infra | 클라우드·네트워크·배포 인프라, IaC |
| Workflow | CI/CD 절차, 개발 도구 사용 흐름, 반복 작업 자동화 |
| Troubleshooting | 기존 오류의 원인 분석과 복구 |
| Architecture | 구성요소 경계, 데이터 구조, 인터페이스, 시스템 설계 결정 |

`Type`은 LLM-Assisted 또는 Manual이다. LLM이 작업이나 기록 분석에 관여했다면 `Type=Manual`이어도 **활성 모델의 정확한 ID**를 모델 Select 속성에 기록한다. 사용자 `--model` 지정, 현재 세션 메타데이터·실행 옵션, 실제 적용된 CLI 설정 순서로 확인한다. 전역 기본 설정, 제품명, 모델 계열만으로 정확한 ID를 추측하지 않는다. 확인할 수 없으면 요약을 준비한 뒤 기록 전에 모델 ID를 요청한다. 여러 모델을 썼다면 주된 모델을 Select에, 다른 모델과 역할을 본문에 적는다. 모델용 Select 속성이 없는 템플릿에서는 `LLM` Select를 추가한다. `생성일` Created time은 Notion이 채운다.

기존 Select 옵션 중 같은 의미의 값이 있으면 사용한다. `Project`, `Category`, `Type`, 모델용 Select에 필요한 옵션이 없으면 **기록 스킬이 Notion MCP로 자동 추가한 뒤 기록**한다. [Notion의 Select 옵션 갱신 규칙](https://developers.notion.com/reference/update-data-source-properties)에 따라 기존 옵션과 설명을 보존할 수 있는 경우에만 수정하고, 갱신 결과를 다시 확인한다. MCP의 스키마 수정 권한이 없거나 옵션 추가가 실패하면 기록을 중단하고 원인을 보고한다. 보고서 포함 체크박스는 사용하지 않으며, 기존 속성이 있어도 변경하지 않는다.

`.tasklog.json`에는 **데이터베이스** ID/URL을 넣고 MCP 생성·조회에는 해당 데이터베이스에서 조회한 **데이터 소스** ID를 사용한다. 데이터 소스 ID를 사용자가 설정 파일에 입력할 필요는 없다. 스킬의 JSON 예시는 한국어 데이터베이스 기준이다. 다른 데이터베이스에서는 속성 키, 상태 옵션, 날짜 필드명, 데이터 소스 ID를 실제 값으로 치환한다. Notion 화면 언어만 바뀌어도 기존 속성명이 번역된다고 가정하지 않는다.

### 5. 사용 순서

1. `notion-init-work`로 설정 파일을 만들고 `"null"`을 실제 데이터베이스 ID/URL로 교체한다.
2. `notion-log-work`로 완료 기록 또는 진행 중 체크포인트를 남긴다.
3. 새 세션에서 `notion-resume-work`로 같은 프로젝트의 최신 진행 중 기록을 읽는다.
4. `notion-monthly-report`에 기간을 지정해 해당 기간의 전체 기록을 프로젝트별 보고서로 작성한다.

기록이 실패하면 데이터베이스 접근 권한, 데이터베이스 ID와 데이터 소스 ID 구분, 속성 타입, Status 옵션, Select 옵션 수정 권한을 확인한다. 자동 스키마 변경 범위는 이번 기록에 필요한 Select 옵션 추가로 제한한다.

기간별 보고서는 AI 도구에 다음과 같이 요청합니다. 아래는 셸 명령이 아니라 스킬에 전달할 요청 예시입니다.

> notion-monthly-report로 2026-11-01부터 2026-11-24까지의 보고서를 작성해줘.
>
> notion-monthly-report --from 2026-11-01 --to 2026-11-24 --project billing-api --language ko

시작일·종료일은 모두 포함합니다. `--month 2026-11`처럼 한 달을 지정할 수도 있습니다. 프로젝트를 생략하면 모든 프로젝트를 구분해 정리합니다. 기간을 생략하면 날짜를 확인하며, 완료·진행 중·기타 상태를 구분하고 같은 작업의 중복 체크포인트는 통합합니다. 보고서 포함 체크나 해당 속성은 필요하지 않습니다. 기본 결과는 대화의 Markdown이며, Notion 저장은 별도로 요청합니다.

### 6. 자동 기록 활성화 — 선택

스킬 설치와 자동 기록 활성화는 별도입니다. 기본값은 비활성입니다. 설치된 `notion-log-work` 폴더와 작업 프로젝트의 절대 경로를 지정합니다.

```bash
SKILL_DIR=/absolute/path/to/notion-log-work
PROJECT_DIR=/absolute/path/to/project
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" install --agent pi
```

`--agent` 값은 `codex`, `claude-code`, `kiro`, `agy`, `pi`입니다. 사용할 도구마다 실행한 뒤 기존 `.tasklog.json` 필드를 유지하면서 `"auto_record": {"enabled": true}`를 추가합니다. 도구를 다시 시작하고 훅·확장 신뢰 및 Notion 쓰기 권한을 확인합니다.

프로젝트 `.gitignore`에는 다음을 추가합니다.

```gitignore
/.tasklog.json
/.tasklog/
*.pre-tasklog
```

현재 에이전트가 작업 종료 시 한 차례 기록을 시도합니다. 강제 종료나 MCP·모델 오류 시 Notion 전송은 보장되지 않으며, 로컬 pending과 초안에서 수동 복구합니다. Git 변경이 없는 대화·설계 작업은 수동으로 기록합니다. 자동 기록은 추가 모델 턴을 사용하며, 실행 시간은 모델과 도구 호출에 따라 달라집니다. 자세한 도구별 설정·복구·제거 방법은 [자동 연동 안내](notion-log-work/references/automation.md)를 확인하세요.

### 검증 및 문제 해결

- Notion 접근 실패: 현재 도구의 MCP 연결·인증, 데이터베이스 권한과 ID를 확인합니다.
- 자동 기록 실패: 훅 로딩·신뢰 상태와 `auto_record.enabled`를 확인하고 pending 초안을 수동 처리합니다.
- 실제 지원 범위와 남은 제약: [검증 결과](VALIDATION.md). 지원 구현과 모든 모델·도구 조합의 실제 성공은 구분합니다.

개발 검증 명령은 아래와 같습니다. 패키지 다운로드나 Notion 쓰기 없이 실행합니다. Node 테스트에는 `node --test`를 지원하는 환경이 필요합니다.

```bash
python3 -m unittest discover -s tests -v
node --test tests/pi-extension.test.mjs
git diff --check
```

## English

### Included skills

| Skill | Purpose |
| --- | --- |
| `notion-init-work` | Configure the project name and work-log database |
| `notion-log-work` | Save work and checkpoints as Why / What / Impact / Next Actions / References |
| `notion-resume-work` | Restore context and next steps from the project's latest in-progress entry |
| `notion-monthly-report` | Build project reports from all entries in a specified date range |

Adapters are provided for Codex, Claude Code, Kiro CLI, agy (Antigravity CLI), and pi coding agent. See [validation results](VALIDATION.md) for the actual tested scope. Live Claude Code execution has not been verified yet.

### 1. Prerequisites

- An AI agent and access to its model
- **Notion MCP connected and authenticated in that agent**, with read/write access to the target database
- Git and an environment that runs `npx skills`: Node.js 22.20 or later ([installer documentation](https://github.com/vercel-labs/skills))
- For automatic recording: macOS/Linux, Python 3.10 or later, and a Git repository. Windows users can use the manual skill workflow.

Without Notion MCP, Notion writes, queries, restoration of the latest Notion entry, and report queries do not work. Only local project setup, Markdown drafts, and restoration from supplied records remain available.

### 2. Install the skills

Install globally to use the skills across projects:

```bash
npx skills add JoonHoSeong/tasklog-skills -g
```

In interactive mode, select all four skills and your AI agents. Some environments automatically select detected agents; check the installation summary, then restart the agents. Omit `-g` for a project installation. If the installer does not support or discover your agent, see the [manual placement guide](INSTALL_KIRO_CODEX_AGY.md) and place the four **complete skill folders**, including `scripts/` and `references/`.

`-g` selects user-level installation; it **does not automatically install into every CLI tool**. Targets are the supported agents you select. To explicitly target the five adapters:

```bash
npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent codex claude-code kiro-cli antigravity-cli pi
```

The installer's `kiro-cli` and `antigravity-cli` IDs differ from the automation script's `kiro` and `agy` IDs. Adding `--all` installs every skill into all installer-supported agents; this does not guarantee runtime compatibility with every LLM CLI. Each agent still needs its own Notion MCP connection and hook/extension setup. See the [official agent list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

Inspect installations and manage updates:

```bash
npx skills list -g
npx skills check
npx skills update
```

See the [skills installation reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for command options.

#### If a specific agent is missing the skills

Run only the command for the missing agent. Each command installs all four skills globally for that agent. Preserve any local edits to installed skills before reinstalling.

| Agent | Individual installation command |
| --- | --- |
| Codex | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent codex` |
| agy (Antigravity CLI) | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent antigravity-cli` |
| Kiro CLI | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent kiro-cli` |
| pi | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent pi` |
| Claude Code | `npx skills add JoonHoSeong/tasklog-skills -g --skill '*' --agent claude-code` |

Inspect installations for each target:

```bash
npx skills list -g --agent codex
npx skills list -g --agent antigravity-cli
npx skills list -g --agent kiro-cli
npx skills list -g --agent pi
npx skills list -g --agent claude-code
```

An installer listing does not prove the current CLI session has loaded the skills. Restart the agent and ask: `Find and read the notion-init-work skill. Do not change files or Notion yet.` Custom Kiro agents may also need skill resources configured; see the [Kiro reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/#skill-resources).

If individual installation also fails, copy the four complete folders (`notion-init-work`, `notion-log-work`, `notion-resume-work`, `notion-monthly-report`) from this repository into the appropriate global directory below. Copying only `SKILL.md` leaves out the automation scripts and references. Compare existing folders and preserve local changes before updating them.

| Agent | Parent directory for manual placement |
| --- | --- |
| Codex | `~/.agents/skills/` |
| agy (Antigravity CLI) | `~/.gemini/config/skills/` |
| Kiro CLI | `~/.kiro/skills/` |
| pi | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |

For example, pi's logging skill belongs at `~/.agents/skills/notion-log-work/SKILL.md`. Manually copied skills may not be registered with the installer's update management; update those copies manually. Restart the agent, verify discovery, then configure Notion MCP and any automatic recording you need.

### 3. Connect Notion MCP — required

Connect a Notion connector, plugin, or MCP server in each AI agent you use and complete workspace authentication. The official remote MCP endpoint is `https://mcp.notion.com/mcp`. Follow [Notion's MCP connection guide](https://developers.notion.com/guides/mcp/get-started-with-mcp) for your client.

The connection must be able to read the database and create/update its pages. Adding missing Select options also needs schema-update permission. If Notion MCP is already connected, verify its access instead of installing a duplicate. Do not assume authentication is shared across AI agents.

Verify the connection by asking your agent:

> Use Notion MCP to read the properties and data sources of this database URL. Do not create or modify any pages yet.

Configure the project after the agent successfully reads the database. This repository's scripts do not install MCP servers, log in, or grant permissions for you.

### 4. Configure the project

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
| Git branch (Optional) | Select or Text | `Git Branch` | `Git Branch` or `Branch` |

The current Korean completion/in-progress options are `완료`/`진행 중`; `Done`/`In Progress` are English examples. Prefer the Status groups `complete`/`in_progress` when available. Otherwise use unambiguous option names. Ask if multiple options could match or their meaning is unclear. `Not Started`/`시작 전` means neither completed nor in progress.

Codex, Kiro CLI, agy, Claude Code, and pi use the same five Category values. Choose one based on the main deliverable and explain borderline choices in the entry.

| Category | Main deliverable |
| --- | --- |
| Backend | APIs, business logic, data access code |
| Infra | Cloud, network, deployment infrastructure, IaC |
| Workflow | CI/CD procedures, development tool flows, repeatable automation |
| Troubleshooting | Root cause analysis and repair of an existing failure |
| Architecture | Component boundaries, data structures, interfaces, system design decisions |

Type is LLM-Assisted or Manual. If an LLM contributed to the work or analyzed it for logging, record the **exact active model ID** even when Type is Manual. Resolve it from explicit `--model` input, current session metadata or launch options, then CLI configuration confirmed active for this session. A product name, model family, or unrelated global default is insufficient. If the ID cannot be confirmed, prepare the summary and request the model ID before writing. For multiple models, put the primary one in Select and list the others with their roles in the body. Add an `LLM` Select property if the template lacks a model Select. `생성일` is a read-only created-time field in the current database.

Prefer an equivalent existing Select option. If a required `Project`, `Category`, `Type`, or model option is missing, **the logging skill adds it through Notion MCP before writing the entry**. It follows [Notion's Select option update rules](https://developers.notion.com/reference/update-data-source-properties) to preserve existing options and descriptions, then refetches the schema. If the MCP lacks permission or cannot safely add an option, it stops and reports the cause. Report inclusion checkboxes are not used; existing properties are left unchanged.

Store the **database** ID/URL in `.tasklog.json`; the skill fetches the **data source** ID needed for MCP creation and queries. Users do not need to enter a data source ID in the config file. The skill payloads illustrate a Korean database. For another database, substitute its actual property keys, status values, date field names, and data source ID. Changing the Notion UI language does not imply that existing property names changed.

### 5. Usage

1. Run `notion-init-work`, then replace `"null"` with the target database ID/URL.
2. Run `notion-log-work` to save completed work or an in-progress checkpoint.
3. In a later session, run `notion-resume-work` to load the project's latest in-progress entry.
4. Give `notion-monthly-report` a date range to report on all entries in that period, grouped by project.

If writing fails, check database access, database versus data source IDs, property types, Status options, and permission to update Select options. Automatic schema changes are limited to Select options required for the current log entry.

Ask your AI agent for a date-range report. These are skill requests, not shell commands:

> Use notion-monthly-report to report on November 1–24, 2026.
>
> notion-monthly-report --from 2026-11-01 --to 2026-11-24 --project billing-api --language en

Both dates are inclusive. Use `--month 2026-11` for a calendar month. Omit the project to include all projects in separate sections. If no period is provided, the agent asks for one. Completed, in-progress, and other states are distinguished, and duplicate checkpoints for the same task are consolidated. No report inclusion checkbox or property is required. The default output is Markdown in the conversation; request Notion storage separately.

### 6. Enable automatic recording — optional

Installing the skills does not enable automatic recording. It is disabled by default. Set the absolute paths of the installed `notion-log-work` folder and your project:

```bash
SKILL_DIR=/absolute/path/to/notion-log-work
PROJECT_DIR=/absolute/path/to/project
python3 "$SKILL_DIR/scripts/tasklog.py" --root "$PROJECT_DIR" install --agent pi
```

Accepted `--agent` values: `codex`, `claude-code`, `kiro`, `agy`, and `pi`. Run it for each agent, then add `"auto_record": {"enabled": true}` to `.tasklog.json`, preserving existing fields. Restart the agent and verify hook/extension trust and Notion write permissions.

Add these entries to your project's `.gitignore`:

```gitignore
/.tasklog.json
/.tasklog/
*.pre-tasklog
```

The current agent attempts recording once at the end of work. Forced shutdowns and MCP/model failures can prevent delivery; recover manually from local pending checkpoints and drafts. Record conversations or design work without Git changes manually. Automatic recording uses additional model turns, and duration depends on the model and tool calls. See the [automation guide](notion-log-work/references/automation.md) for agent settings, recovery, and removal.

### Validation and troubleshooting

- Notion access failure: check MCP connection/authentication in the current agent, database permissions, and the database ID.
- Automatic recording failure: check hook loading/trust and `auto_record.enabled`, then process pending drafts manually.
- Tested support and remaining limitations: [validation results](VALIDATION.md). Adapter implementation does not establish success for every model and agent combination.

Run development checks without package downloads or Notion writes. The Node test requires a runtime that supports `node --test`.

```bash
python3 -m unittest discover -s tests -v
node --test tests/pi-extension.test.mjs
git diff --check
```

## 라이선스 / License

MIT License. See [LICENSE](LICENSE).
