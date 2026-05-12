# AI Engineering Rigor

Portable engineering rigor skills for Claude Code and Codex. Use them in any repository for code review, test coverage, commit quality, dependency audit, delivery workflow rigor, and security best-practice guidance.

Agent skills are zero-dependency: clone, copy, and use. The optional Python library under `skills/` has its own runtime dependencies for CI/programmatic use.

## Use In Any Project

This repo ships skills in both supported layouts:

| Platform | Copy From | Copy To | Invocation |
|----------|-----------|---------|------------|
| Codex | `.agents/skills/ai-rigor-*` | `/your/repo/.agents/skills/` | `$ai-rigor-review` |
| Claude Code | `.claude/skills/ai-rigor-*` | `/your/repo/.claude/skills/` | `/ai-rigor-review` |

Optional team-specific behavior lives in `.ai-rigor/`:

| File | Purpose |
|------|---------|
| `.ai-rigor/standards.md` | Team coding, security, testing, Git, and release standards |
| `.ai-rigor/config.yml` | Source control settings, ignore patterns, commit rules, dependency allowlist |

The skills are generic and portable. Add `.ai-rigor/` when you want them to follow your team's standards, repo conventions, ignore patterns, source-control settings, and approved dependency rules.

You can copy all skills or only the ones your project needs. No API keys are required for agent skills because the agent you are already using does the reasoning.

## Skills

### Review and Analysis

| Skill | Claude Code | Codex | What it does |
|-------|-------------|-------|-------------|
| **Code Review** | `/ai-rigor-review` | `$ai-rigor-review` | Security, performance, quality review. Accepts PR links, commits, or files. |
| **Test Coverage** | `/ai-rigor-coverage` | `$ai-rigor-coverage` | Find changed functions missing tests, suggest specific test cases |
| **Commit Quality** | `/ai-rigor-commit` | `$ai-rigor-commit` | Conventional commit format, scope/file alignment, rewrite suggestions |
| **Dependency Audit** | `/ai-rigor-deps` | `$ai-rigor-deps` | Unpinned versions, CVEs, unused additions, broken removals |

### Delivery Rigor

| Skill | Claude Code | Codex | What it does |
|-------|-------------|-------|-------------|
| **Development Rigor** | `/ai-rigor-dev` | `$ai-rigor-dev` | Production-ready task execution, tests, and QA/Infra handoffs |
| **QA Rigor** | `/ai-rigor-qa` | `$ai-rigor-qa` | Acceptance-criteria validation, defect evidence, and QA sign-off |
| **Infra Rigor** | `/ai-rigor-infra` | `$ai-rigor-infra` | IaC/script validation, security baseline checks, and infra sign-off |
| **Release Rigor** | `/ai-rigor-release` | `$ai-rigor-release` | Release planning, stage validation, production approval, rollback reporting |
| **Security Rigor** | `/ai-rigor-security` | `$ai-rigor-security` | Secure-by-default guidance and security best-practice reviews |

## Quickstart

### Add To A Repo

From this repo:

```bash
# Codex
mkdir -p /your/repo/.agents/skills
cp -r .agents/skills/ai-rigor-* /your/repo/.agents/skills/

# Claude Code
mkdir -p /your/repo/.claude/skills
cp -r .claude/skills/ai-rigor-* /your/repo/.claude/skills/

# Optional team config
cp -r .ai-rigor /your/repo/.ai-rigor
```

Then open `/your/repo` in Codex or Claude Code. Skills are auto-detected from the copied folders.

### Claude Code

Clone and open in Claude Code, or copy `.claude/skills/ai-rigor-*` into another repo.

```
# Review a PR (paste any GitHub PR link)
/ai-rigor-review https://github.com/org/repo/pull/42

# Review by PR number (uses config for org/project)
/ai-rigor-review 42

# Review last commit
/ai-rigor-review HEAD~1

# Review a specific file
/ai-rigor-review app/auth.py

# Other skills
/ai-rigor-coverage HEAD~1
/ai-rigor-commit HEAD
/ai-rigor-deps HEAD~1
/ai-rigor-security app/auth.py
/ai-rigor-dev "Implement password reset"
```

Install globally: copy `.claude/skills/ai-rigor-*/` to `~/.claude/skills/`.

### Codex

Clone and open in Codex, or copy `.agents/skills/ai-rigor-*` into another repo.

```
$ai-rigor-review
$ai-rigor-coverage
$ai-rigor-commit
$ai-rigor-deps
$ai-rigor-security
$ai-rigor-dev
$ai-rigor-qa
$ai-rigor-infra
$ai-rigor-release
```

### ChatGPT

The `.agents/skills` folder is for Codex auto-discovery. ChatGPT skills do not automatically sync from a local repo folder; package/upload the same skill folders through ChatGPT's Skills UI if you want to use them there.

## Configuration

Drop a `.ai-rigor/` folder in any repo to add a team-specific behavior layer. Both files are optional -- skills use sensible defaults without them.

### Team Standards (`.ai-rigor/standards.md`)

Write your coding standards in plain markdown. The review skill uses this **instead of** built-in defaults.

```markdown
# .ai-rigor/standards.md

## Python / FastAPI
- All routes must use Pydantic request/response models
- Auth via FastAPI Depends() injection -- no manual token parsing
- All database calls must be async
- No raw SQL -- use ORM or parameterized queries

## Security
- No hardcoded secrets
- All user inputs validated via Pydantic
- No f-strings in SQL queries
- JWT must validate expiry and signature

## Code Quality
- Functions max 30 lines
- No TODO comments in merged code -- create tickets
- Test coverage required for all new public functions
```

### Repo Config (`.ai-rigor/config.yml`)

Configure source control credentials, ignore patterns, and skill-specific settings.

```yaml
# .ai-rigor/config.yml

# Source control (for PR review by number)
source_control:
  provider: github
  github:
    owner: your-org
    repo: your-repo

# Review settings
review:
  standards_file: .ai-rigor/standards.md           # path to standards
  ignore:                                           # files to skip
    - "*.generated.*"
    - "*.min.js"
    - "migrations/"
    - "vendor/"

# Commit quality
commit:
  conventional: true                                # enforce conventional commits
  max_subject_length: 72
  # types: [feat, fix, docs, refactor, test, chore] # allowed types

# Dependency audit
deps:
  allowed:                                          # pre-approved packages (won't be flagged)
    - openai
    - pydantic
    - fastapi
    - pytest
```

### What Each Skill Reads

| Skill | `config.yml` sections | `standards.md` |
|-------|----------------------|----------------|
| **Code Review** | `source_control`, `review.ignore` | Yes -- replaces built-in standards |
| **Test Coverage** | `review.ignore` | Test conventions section |
| **Commit Quality** | `commit.*` | Git/PR conventions section |
| **Dependency Audit** | `deps.allowed`, `deps.files` | No |
| **Development Rigor** | General repo preferences | Yes -- implementation standards |
| **QA Rigor** | General repo preferences | Yes -- test/release standards |
| **Infra Rigor** | General repo preferences | Yes -- infra/security standards |
| **Release Rigor** | General repo preferences | Yes -- release standards |
| **Security Rigor** | General repo preferences | Yes -- security standards plus bundled references |

## Security References

`ai-rigor-security` includes bundled reference guidance for:

- Python: FastAPI, Django, Flask
- JavaScript/TypeScript: general frontend, React, Vue, Next.js, Express, jQuery
- Go: general backend

Those reference files are adapted from Apache-licensed security-best-practices material. Keep `LICENSE.txt` with the `ai-rigor-security` skill when copying or redistributing it.

## How It Works

The review and analysis skills follow the same pattern:

1. **Load config** -- read `.ai-rigor/config.yml` and `.ai-rigor/standards.md` if they exist
2. **Extract** -- pull minimal context from the diff (changed lines, signatures, imports, decorators)
3. **Reason** -- analyze against team standards (or built-in defaults)
4. **Report** -- structured output with severity, line numbers, and actionable fixes

No API keys needed. The agent you're already running IS the LLM.

## Does It Actually Save Tokens?

We benchmarked raw diff vs extracted context on real and production-like diffs:

```
Scenario                              Naive   Extracted   Reduction
--------------------------------------------------------------------
Large file, 3-line change              1522       934       38.6%
Huge file (300 unchanged lines)        3455       726       79.0%
Full project (all commits)             7503      7060        5.9%
Multi-file PR (3 files, new code)      1147      1128        1.7%
```

**Production diffs** (small changes in large files) see **39-79% token reduction**. Greenfield code sees modest savings.

```bash
uv run --extra dev python benchmarks/token_benchmark.py
```

## Publishing to Another Repo

Copy the skills and optionally the config template. You can copy all skills or a subset:

```bash
# Skills (pick your platform)
cp -r .claude/skills/ai-rigor-* /your/repo/.claude/skills/    # Claude Code
cp -r .agents/skills/ai-rigor-* /your/repo/.agents/skills/    # Codex

# Config template (optional -- customize for your team)
cp -r .ai-rigor /your/repo/.ai-rigor
```

Then edit `.ai-rigor/standards.md` with your team's conventions and `.ai-rigor/config.yml` with your GitHub credentials.

## Repo Structure

```
.ai-rigor/                             # Team config (copy to any repo)
  config.yml                           # Source control, ignore patterns, settings
  standards.md                         # Team coding standards

.claude/skills/ai-rigor-*/skill.md     # Claude Code skills
.agents/skills/ai-rigor-*/SKILL.md     # Codex skills
.claude/skills/ai-rigor-*/references/  # Optional bundled templates/guidance
.agents/skills/ai-rigor-*/references/  # Optional bundled templates/guidance

skills/                                # Python library (CI/programmatic use)
tests/                                 # 66 tests
benchmarks/                            # Token reduction benchmark
```

## Is This Useful?

**What it does well:**
- Gives the LLM a structured review framework instead of "review this code"
- Reviews against **your team's standards**, not generic rules
- Hits specific dimensions (security, auth, types, performance) that generic reviews miss
- Context extraction keeps token cost down on large PRs
- PR link support -- review any GitHub PR from the conversation
- Works on any repo -- just copy the skill files

**What it doesn't do:**
- Replace human reviewers -- it's a second opinion, not a gate
- Guarantee finding all bugs -- LLMs miss things
- Work offline -- requires Claude Code or Codex running
