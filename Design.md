# Design: ai-engineering-rigor

## Philosophy: Minimal Context, Maximum Signal

LLMs have finite context windows. Sending entire files for code review wastes tokens and dilutes reasoning. This project's core insight: **extract only what the LLM needs to reason about**.

Instead of sending a 500-line file, each skill extracts:
- Function signatures only (not bodies)
- Changed lines only (not unchanged context)
- Deduplicated imports
- Decorator metadata (reveals auth patterns, routes)

This applies whether the LLM is Claude (via skills), Codex, or an external API call.

---

## Skill Architecture

Each skill follows a 4-phase pattern:

```
┌──────────────────────────────────────┐
│        Agent (Claude / Codex)         │
│     invokes skill via / or $          │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Phase 0: Load Config           │
│   .ai-rigor/config.yml (credentials, │
│   ignore patterns, settings)          │
│   .ai-rigor/standards.md (team rules) │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Phase 1: Extract Context       │
│   PR link / git diff → minimal        │
│   signal payload (hunks, signatures,  │
│   imports, decorators)                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Phase 2: Reason                │
│   Agent analyzes against team         │
│   standards (or built-in defaults)    │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Phase 3: Report                │
│   Structured output with severity,    │
│   line numbers, and actionable fixes  │
└──────────────────────────────────────┘
```

---

## Configuration System

Skills are zero-config by default but fully customizable per repo via `.ai-rigor/`.

### `.ai-rigor/standards.md` -- Team Standards

Plain markdown file with team coding conventions. When present, the review skill uses this **instead of** built-in defaults. Teams write whatever rules matter to them -- security policies, framework patterns, naming conventions, test requirements.

### `.ai-rigor/config.yml` -- Repo Config

YAML file with:
- **Source control credentials** (`source_control.ado.org_url`, `source_control.ado.project`) -- enables PR review by number
- **Ignore patterns** (`review.ignore`) -- skip generated files, migrations, vendor
- **Commit rules** (`commit.conventional`, `commit.max_subject_length`) -- enforce team conventions
- **Pre-approved deps** (`deps.allowed`) -- packages that shouldn't be flagged in audits

Both files are optional. Skills use sensible defaults without them.

### Input Detection

The review skill auto-detects what it's reviewing:
- **PR link** (GitHub or ADO URL) -- fetches metadata + diff via `gh` CLI or ADO MCP tools
- **PR number** -- uses `config.yml` credentials to resolve the PR
- **Commit range** -- `git diff`
- **File path** -- `git diff HEAD -- <path>`
- **Default** -- `git diff HEAD~1`

---

## Skills

### Code Review (`/ai-rigor-review`)

Extracts changed hunks, function signatures, imports, decorators, and class definitions from a git diff. Reviews against 5 dimensions: security, framework patterns, type safety, performance, and code quality. Outputs risk score, security score, issue list, and merge recommendation.

### Test Coverage (`/ai-rigor-coverage`)

Extracts changed function signatures (skipping dunders and test functions). Maps source files to expected test files via naming conventions (`foo.py` → `test_foo.py`). Searches for existing tests. Suggests specific, implementable test cases for uncovered functions.

### Commit Quality (`/ai-rigor-commit`)

Parses commit messages against conventional commit format (`type(scope): description`). Checks subject length, imperative mood, scope/file alignment. Suggests rewrites for non-conforming messages.

### Dependency Audit (`/ai-rigor-deps`)

Parses added/removed lines from dependency file diffs (requirements.txt, pyproject.toml). Flags unpinned versions, known CVEs, typosquats. Cross-references against actual imports in the codebase.

---

## Delivery: Agent Skills (Primary)

The skills are delivered as markdown prompts that run inside Claude Code or Codex. The agent IS the LLM — no external API keys, no Python runtime, no dependencies.

| Platform | Location | Invocation |
|----------|----------|------------|
| Claude Code | `.claude/skills/ai-rigor-*/skill.md` | `/ai-rigor-review HEAD~1` |
| Codex | `.agents/skills/ai-rigor-*/SKILL.md` | `$ai-rigor-review` |

Skills are auto-detected when the repo is opened. They can also be installed globally.

---

## Delivery: Python Library (Secondary)

The same extraction and reasoning logic exists as a Python library under `skills/`. This is for CI pipelines, GitHub Actions, or programmatic use where you want to call an external LLM (Azure/OpenAI).

```
skills/
  base.py                     # Skill(ABC) — interface all skills implement
  registry.py                 # SkillRegistry — discover and dispatch skills
  errors.py                   # Shared error hierarchy
  extractors/base.py          # CodeExtractor(ABC) — interface for all extractors
  shared/                     # Token utils, diff utils, LLM response parsing
  code_review/python/         # PythonCodeReviewSkill
  test_coverage/python/       # PythonTestCoverageSkill
  commit_quality/             # CommitQualitySkill
  dependency_audit/python/    # PythonDependencyAuditSkill
```

Key patterns:
- **Strategy pattern** — Pluggable LLM providers (Azure, OpenAI, extensible via `LLMProvider` ABC)
- **Pydantic validation** — Strict schema enforcement on LLM output
- **Error recovery** — Single retry with error feedback on parse failure
- **Extractor pattern** — Pure Python parsing, no LLM. `extract(diff) → dataclass → to_prompt_payload() → str`

---

## Extension Points

### Adding a New Skill (Agent)

1. Create `skill.md` (Claude) or `SKILL.md` (Codex) with YAML frontmatter
2. Define extraction phase (what to `git diff` / `grep` / `read`)
3. Define reasoning phase (what standards to check against)
4. Define output format (structured markdown)

### Adding a New Skill (Python Library)

1. Create `skills/<skill_name>/` with `skill.py`, extractors, models
2. Subclass `Skill(ABC)` — implement `name`, `description`, `run()`
3. Register in `skills/__init__.py` via `SkillRegistry.register()`
4. Add extractor unit tests + integration test with mocked LLM

### Adding a New LLM Provider (Python Library)

1. Subclass `LLMProvider(ABC)` — implement `complete(system_prompt, user_prompt) → str`
2. Add case in `create_provider()` factory

---

## Directory Conventions

- Repo config: `.ai-rigor/config.yml` and `.ai-rigor/standards.md`
- Agent skills: `.claude/skills/` (Claude Code) and `.agents/skills/` (Codex)
- Python library: `skills/<skill_name>/` or `skills/<skill_name>/<language>/`
- Each Python skill has `SKILL.md`, `skill.py`, `models/`, and optionally `extractors/`, `layers/`
- Shared utilities: `skills/shared/`
- Tests: `tests/test_<module>.py`
- Benchmarks: `benchmarks/`
