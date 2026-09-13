# CLAUDE.md -- inventario-cli-python

> Project-specific system prompt for Claude Code.
> Read at session start. Treat as binding operational law.

## 1. Project identity

- **Project:** inventario-cli-python
- **Domain:** Generic inventory CLI with swappable domain presets
- **Reference preset:** `LibreriaChilena` (30 books, 17 Chilean authors)
- **Stack:** Pure Python 3.11+ (no runtime dependencies)
- **Repo:** github.com/javiersandovaltap-beep/inventario-cli-python
- **Roadmap:** `/home/z/my-project/download/roadmap_01_inventario.md`

## 2. Core principles

1. **Atomic changes.** One task -> one commit. Never bundle unrelated work.
2. **Evidence-first.** Every claim about code state must be backed by a tool output (ruff / mypy / pytest / git diff). No "I think it works".
3. **Scope discipline.** Refactor only what the current prompt requires. Adjacent smells stay untouched.
4. **Read AGENTS.md first.** It contains the architectural contract. Violating it = rejecting the change.
5. **No silent failure.** If a tool fails or a test is red, STOP. Report. Do not paper over.
6. **Local state.** `.claude/local/sessionstate.md` and `.claude/local/memory.md` are yours to read and update. They are gitignored. Use them.

## 3. Stack & tooling

| Layer       | Tool        | Version pin                                              |
|-------------|-------------|----------------------------------------------------------|
| Runtime     | Python      | >=3.11 (dev box: 3.14.6)                                 |
| Lint        | ruff        | >=0.6, target py311, line-length 100                     |
| Format      | ruff format | quote=double, indent=space                               |
| Types       | mypy        | >=1.11, non-strict, warn_return_any=true                 |
| Tests       | pytest      | >=8.0, strict-markers, markers: smoke/unit/edge/integration |
| Coverage    | pytest-cov  | >=5.0, target >=70% by project close                      |
| Security    | bandit      | >=1.7, skip B101, exclude tests/ and data/               |
| Hooks       | pre-commit  | >=3.8, ruff + format + standard checks                   |

## 4. Model routing (NIM)

| Model               | Alias  | Use for                                                | Avoid for                                       |
|---------------------|--------|--------------------------------------------------------|-------------------------------------------------|
| DeepSeek V3.x Flash | haiku  | Mechanical edits, single-file, data migration          | Multi-file coordination, signature changes     |
| Nemotron Super      | sonnet | Multi-file, CI/CD, Docker, refactor with signature change | Deep architectural reasoning                    |
| Kimi K3             | opus   | Architectural refactor, complex design decisions       | Routine tasks (quota rationed: max 2 per phase) |

### Subagent -> model mapping

| Subagent               | Model  | Purpose                                                          |
|------------------------|--------|------------------------------------------------------------------|
| `@quick-explorer`       | haiku  | Read-only code location (where does X live?)                     |
| `@implementer`         | sonnet | Delegated execution of well-specified plans (write code + verify) |
| `@code-reviewer`       | sonnet | Post-implementation compliance audit against AGENTS.md           |
| `@architecture-reviewer`| opus   | Pre-implementation design quality review (max 2 invocations/phase) |

## 5. Workflow per task

1. **Read** AGENTS.md (architecture contract) and the relevant module.
2. **Plan** -- output a plan with files affected, signatures, and verification commands. Wait for approval before editing.
3. **Optional: design review** -- for tasks touching >2 modules or introducing new patterns, invoke `@architecture-reviewer` BEFORE implementation. Quota: max 2 invocations per phase.
4. **Implement** -- for mechanical/well-specified tasks, delegate to `@implementer`. For architectural tasks, do it yourself.
5. **Verify** -- paste tool outputs. No "should work". Show the green. (If `@implementer` was used, this comes back in its report.)
6. **Audit** -- invoke `@code-reviewer` subagent before commit.
7. **Commit** -- conventional commit format. Ask before `git commit` and `git push` (both are `ask` in settings.json).

### When to delegate vs. do it yourself

| Situation                                                | Action                              |
|-----------------------------------------------------------|--------------------------------------|
| Single new module with contract already in AGENTS.md      | Delegate to `@implementer`           |
| Migration of seed data (e.g., 30 books to preset)         | Delegate to `@implementer`           |
| Refactor with signature change touching 2-3 modules       | Do it yourself (model: sonnet/opus)  |
| New pattern introduced (e.g., new Protocol)               | Do it yourself + `@architecture-reviewer` before |
| Multi-file coordination with dependency chain             | Do it yourself                       |

## 6. Evidence-first checklist

Before claiming a task is done, you must show:

- [ ] `ruff check <files>` output (must be clean or only D-rules in tests)
- [ ] `ruff format --check <files>` output
- [ ] `mypy <files>` output (must be clean)
- [ ] `pytest` output if tests exist for the touched module
- [ ] `git diff --stat` summary (files + line counts)
- [ ] If touching security-sensitive code: `bandit -r <dir> -ll`

## 7. Audit output schema

When auditing changes (either yourself or via `@code-reviewer`), use EXACTLY this format:

```
[Files Changed]
  - path/to/file.py (+N -M)

[Logic Altered]
  - <one-line summary of behavioral change>
  - <one-line summary of behavioral change>

[Tests Run]
  - ruff check: PASS
  - mypy: PASS
  - pytest tests/test_x.py: 5 passed

[Verification Method]
  - <how you confirmed the change works as intended>

[Residual Risks]
  - <risk or "None identified">
```

## 8. STOP conditions

Halt immediately and ask the user if:

1. You encounter a `.env` file or hardcoded secrets in the working directory.
2. A change requires modifying `pyproject.toml`, `.github/workflows/ci.yml`, `AGENTS.md`, `CLAUDE.md`, `.claude/agents/**`, or `.claude/hooks/**` (these are protected).
3. A test is red and the failure is not obviously caused by the current change.
4. You need to `pip install` a new package.
5. You need to invoke Kimi K3 (opus) and the current phase already used its quota.
6. The change touches more than 3 files that were not in the original plan.

## 9. Language policy

- **Governance files** (this file, AGENTS.md, `.claude/agents/*.md`, `.claude/hooks/*.ps1`): English.
- **Public files** (README.md, CONTRIBUTING.md, LICENSE): Spanish.
- **Local state** (`.claude/local/sessionstate.md`, `.claude/local/memory.md`): English.
- **Source code** (Python): English identifiers, Spanish string literals only when user-facing.
- **Commits**: English, conventional format (`feat:` / `fix:` / `refactor:` / `docs:` / `test:` / `chore:`).

## 10. References

- Architecture contract: `AGENTS.md`
- Subagents:
  - `.claude/agents/quick-explorer.md` (haiku) -- read-only code locator
  - `.claude/agents/implementer.md` (sonnet) -- delegated execution of well-specified plans
  - `.claude/agents/code-reviewer.md` (sonnet) -- post-impl compliance audit
  - `.claude/agents/architecture-reviewer.md` (opus, max 2/phase) -- pre-impl design review
- Permissions: `.claude/settings.json`
- Hooks: `.claude/hooks/block-rm.ps1` (PreToolUse, active), `.claude/hooks/run-tests.ps1` (PostToolUse, active from Fase 4)
- Roadmap: `/home/z/my-project/download/roadmap_01_inventario.md`
- Local session state: `.claude/local/sessionstate.md`
- Local long-term memory: `.claude/local/memory.md`
