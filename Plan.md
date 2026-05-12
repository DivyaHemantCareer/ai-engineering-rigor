# Development Plan: ai-engineering-rigor

## Context

A collection of engineering rigor skills for Claude Code and Codex. The core differentiator is **context window optimization** — extractors distill git diffs into minimal, high-signal payloads before the LLM reasons about them. Skills are delivered as agent prompts (zero-dependency) and as a Python library (for CI/programmatic use).

---

## Completed

### Phase 0 — Documentation
- [x] `Plan.md` — this file
- [x] `Design.md` — architecture, skill pattern, extension points

### Phase 1 — Foundation
- [x] `__init__.py` in all packages
- [x] `pyproject.toml` with deps and pytest config
- [x] Integration tests with mocked LLM (`tests/conftest.py`, `tests/test_skill_integration.py`)

### Phase 2 — Robustness
- [x] Multi-file diff support (`extract_all()`, `MultiFileReviewResult`, `review_multi()`)
- [x] LLM error recovery — single retry with error feedback
- [x] Configurable LLM parameters (`temperature`, `max_tokens`, env vars)
- [x] Structured logging (`logger.py`)

### Phase 3 — Extensibility
- [x] Abstract base classes (`Skill`, `CodeExtractor`, error hierarchy)
- [x] Skill registry (`SkillRegistry` with `register()`, `get()`, `list_all()`)
- [x] Shared utilities (`token_utils`, `diff_utils`, `llm_utils`)

### Phase 4 — New Skills (Python Library)
- [x] Test Coverage Analysis (`skills/test_coverage/python/`)
- [x] Commit Message Quality (`skills/commit_quality/`)
- [x] Dependency Audit (`skills/dependency_audit/python/`)
- [x] All registered in `SkillRegistry`, each with SKILL.md, extractor tests, integration tests

### Phase 5 — Agent Skills
- [x] Claude Code skills (`.claude/skills/ai-rigor-*/skill.md`)
- [x] Codex skills (`.agents/skills/ai-rigor-*/SKILL.md`)
- [x] 4 skills: review, coverage, commit, deps
- [x] PR link support (GitHub)

### Phase 6 — Configuration
- [x] `.ai-rigor/config.yml` — source control credentials, ignore patterns, skill settings
- [x] `.ai-rigor/standards.md` — team coding standards (replaces built-in defaults)
- [x] All 4 skills read config in Phase 0 before processing
- [x] PR number resolves via config credentials

### Phase 7 — Benchmarks
- [x] Token reduction benchmark (`benchmarks/token_benchmark.py`)
- [x] Real diffs + synthetic production-like scenarios
- [x] Results in README

### Phase 8 — Delivery Rigor Agent Skills
- [x] Development rigor skill (`ai-rigor-dev`)
- [x] QA rigor skill (`ai-rigor-qa`)
- [x] Infrastructure rigor skill (`ai-rigor-infra`)
- [x] Release rigor skill (`ai-rigor-release`)
- [x] Security rigor skill (`ai-rigor-security`) adapted from security best-practices guidance
- [x] Codex and Claude Code skill variants with bundled templates/references

---

## Current State

- **66 tests, all passing**
- **9 agent skills** (Claude Code + Codex): 4 review/analysis skills and 5 delivery rigor skills
- **4 Python library skills** with registry
- **Configurable** — team standards, source control credentials, ignore patterns
- **PR review** — accepts GitHub links or PR numbers
- Zero external dependencies for agent skills

---

## Next Up

### Phase 9 — Work Item Context
- Pull linked work items from PRs (acceptance criteria as review context)
- Pull linked GitHub issues
- Manual `--ticket` argument support

### Phase 10 — CI Integration
- GitHub Actions workflow that runs skills on PRs
- CI pipeline integration
- JSON output mode for machine-readable results

### Phase 11 — Language Expansion
- JavaScript/TypeScript extractors (reuse same skill pattern)
- Go extractors
- Language auto-detection from diff file extensions

### Phase 12 — Skill Composition
- Run all 4 skills in sequence on a PR (`/ai-rigor-full`)
- Aggregate results into a single report
- Configurable skill selection per repo

---

## Critical Files

| File | Role |
|------|------|
| `.ai-rigor/config.yml` | Repo configuration — credentials, ignore patterns, settings |
| `.ai-rigor/standards.md` | Team coding standards — replaces built-in defaults |
| `.claude/skills/ai-rigor-*/skill.md` | Claude Code agent skills |
| `.agents/skills/ai-rigor-*/SKILL.md` | Codex agent skills |
| `.agents/skills/ai-rigor-security/references/` | Bundled security best-practice references |
| `skills/code_review/python/extractors/code_context.py` | Core extractor — pattern all future extractors follow |
| `skills/code_review/python/skill.py` | Reference `Skill` implementation |
| `skills/code_review/python/llm_provider.py` | LLM strategy — shared across Python library skills |
| `skills/registry.py` | Skill discovery and dispatch |
