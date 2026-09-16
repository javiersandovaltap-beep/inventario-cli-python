# AGENTS.md -- inventario-cli-python

> Architectural contract for the project.
> Treat as binding law. Violating any rule requires explicit user approval.
> Read this BEFORE proposing any change.

## 1. Identity

- **Project:** inventario-cli-python
- **Version:** 0.3.0
- **Maturity target:** 3.8/5 (current baseline: 2.7/5)
- **LOC budget:** 650-750 Python lines (current: 518)

## 2. Stack

| Component   | Choice                          | Notes                                                        |
|-------------|---------------------------------|--------------------------------------------------------------|
| Runtime     | Python 3.11+                    | No runtime dependencies                                      |
| Persistence | JSON (injectable)               | Strategy pattern, path injected via constructor              |
| Tests       | pytest + pytest-cov             | strict-markers, >=70% coverage target by project close       |
| Lint        | ruff                            | E, W, F, I, N, B, C4, SIM, UP, D                             |
| Types       | mypy                            | non-strict, warn_return_any=true                             |
| Security    | bandit                          | -ll, skip B101, exclude tests/ and data/                    |
| Hooks       | pre-commit                      | ruff + format + check-yaml/toml/large-files/merge-conflict   |
| Container   | Docker multi-stage              | python:3.12-slim, Fase 2                                     |

## 3. Architecture (layered)

```
+-------------------------------------------------------------+
|  presentation   | modulos/menu.py                           |
|                 | modulos/validaciones.py (generic inputs)  |
+-------------------------------------------------------------+
|  business       | modulos/gestion_datos.py (CRUD)           |
|                 | modulos/funciones_utiles.py (helpers)     |
+-------------------------------------------------------------+
|  domain core    | modulos/item.py (dataclass Item)          |
|                 | modulos/inventario.py (class Inventario)  |
+-------------------------------------------------------------+
|  infrastructure | modulos/persistencia.py (PersistenciaJson)|
+-------------------------------------------------------------+
|  domain presets | presets/base.py (Protocol Preset)         |
|                 | presets/libreria_chilena.py (impl)        |
+-------------------------------------------------------------+
```

**Dependency direction:** top -> bottom only. A preset MUST NOT import from `modulos/`. Presentation MUST NOT import from `persistencia.py` directly.

## 4. Module contracts

### 4.1 `modulos/item.py` (Tarea 0.2 -- pending)

- **Responsibility:** Generic dataclass for inventory items.
- **Public API:**
  - `Item` dataclass: `id: int`, `sku: str`, `nombre: str`, `precio: float`, `stock: int`, `atributos: dict[str, Any] = field(default_factory=dict)`
  - `Item.to_dict(self) -> dict[str, Any]`
  - `Item.from_dict(cls, data: dict[str, Any]) -> Item` (classmethod)
- **Dependencies:** stdlib only (`dataclasses`, `typing`).
- **Constraints:** SKU replaces ISBN as universal identifier. `atributos` is the extension point for domain fields (autor, categoria, marca, etc.).

### 4.2 `modulos/inventario.py` (Tarea 0.5 -- pending)

- **Responsibility:** Encapsulate inventory state + delegate persistence.
- **Public API:**
  - `Inventario(persistencia: PersistenciaProtocol, preset: Preset)`
  - `agregar(item: Item) -> None`
  - `eliminar(sku: str) -> bool`
  - `buscar(sku: str) -> Item | None`
  - `actualizar_stock(sku: str, delta: int) -> None`
  - `listar() -> list[Item]`
  - `cargar() -> None`
  - `guardar() -> None`
- **Dependencies:** `modulos/item.py`, `presets/base.py`.
- **Constraints:** No globals. State lives in `self._items: list[Item]`. Persistence is injected, not imported.

### 4.3 `modulos/persistencia.py` (Tarea 0.4 -- refactor pending)

- **Responsibility:** Concrete JSON I/O implementing `PersistenciaProtocol`.
- **Public API:**
  - `PersistenciaJson(ruta: Path | str)`
  - `guardar(items: list[Item]) -> None`
  - `cargar() -> list[Item]`
- **Dependencies:** stdlib (`json`, `pathlib`, `os`).
- **Constraints:** No module-level `RUTA_DATOS`. Path comes from constructor. Raises `PersistenciaError` (new) on corrupt JSON, not raw `json.JSONDecodeError`.

### 4.4 `modulos/validaciones.py` (Tarea 0.6 -- cleanup pending)

- **Responsibility:** Generic input validators only.
- **Public API:**
  - `validar_input_numero(prompt: str, min_val: int = 0) -> int`
  - `validar_input_flotante(prompt: str, min_val: float = 0.0) -> float`
- **Constraints:** No domain logic (no `validar_autor_chileno` -- that moves to preset).

### 4.5 `modulos/funciones_utiles.py` (Fase 1 -- refactor pending)

- **Responsibility:** ID generation (iterative, not recursive -- fixes L-04).
- **Public API:** `generar_id(ids_en_uso: set[int]) -> int`
- **Constraints:** Iterative, not recursive. O(n) worst case. No stack overflow on large inventories.

### 4.6 `modulos/gestion_datos.py` (Tarea 0.5 -- refactor pending)

- **Responsibility:** CRUD operations on `Inventario` instance.
- **Public API:** Functions receiving `Inventario` instance, not raw lists.
- **Constraints:** No direct persistence calls. No `print()` for system errors (raise exceptions).

### 4.7 `modulos/menu.py` (Tarea 0.6 + Fase 1)

- **Responsibility:** CLI presentation only (input/output).
- **Public API:** `mostrar_menu() -> None`, `pedir_opcion() -> int`
- **Constraints:** No business logic. Validates 0-6 range (fixes L-01). No duplicate definitions (fixes L-07).

### 4.8 `presets/base.py` (Tarea 0.3 -- pending)

- **Responsibility:** Protocol defining the domain preset contract.
- **Public API:**
  ```python
  class Preset(Protocol):
      nombre: str
      slug: str
      schema_atributos: dict[str, type]
      validadores: dict[str, Callable[[Any], bool]]
      seed: list[Item]
  ```
- **Constraints:** Pure protocol, no implementation. Each domain ships its own concrete preset.

### 4.9 `presets/libreria_chilena.py` (Tarea 0.3 -- pending)

- **Responsibility:** Concrete preset for Chilean bookstore domain.
- **Public API:** Implements `Preset`. Migrates 30 books from `datos_basicos.py`.
- **Constraints:** Domain fields (autor, categoria literaria) live in `Item.atributos`, not as top-level dataclass fields.

## 5. Design patterns

| Pattern              | Where                                          | Why                                                              |
|----------------------|------------------------------------------------|------------------------------------------------------------------|
| Strategy             | `PersistenciaJson` injected into `Inventario` | Allows swapping JSON -> SQLite -> memory without touching business |
| Protocol             | `Preset` in `presets/base.py`                  | Structural typing, no inheritance coupling                        |
| Dataclass            | `Item`                                         | Immutable-ish, serializable, type-safe                          |
| Dependency Injection | `Inventario(persistencia, preset)`             | Testable with mocks (Fase 4)                                     |
| Layered architecture | presentation -> business -> core -> infra -> presets | Single dependency direction                                     |

## 6. Rules

| #    | Rule                                                                                                          | Severity    |
|------|--------------------------------------------------------------------------------------------------------------|-------------|
| R1   | Never mix presentation (CLI/menu) with business logic or persistence.                                        | [BLK] |
| R2   | No `print()` for system errors. Use `logging` or raise typed exceptions.                                    | [BLK] |
| R3   | All user input must be validated before processing.                                                          | [BLK] |
| R4   | No global mutable state in business layer. State lives in `Inventario`.                                     | [BLK] |
| R5   | Every new feature ships with at least one smoke test and one edge test.                                      | [REQ] |
| R6   | Domain logic lives in `presets/`, never in `modulos/`.                                                       | [BLK] |
| R7   | Type hints on all public APIs. Internal helpers may skip.                                                   | [REQ] |
| R8   | No new runtime dependencies without explicit user approval.                                                 | [BLK] |
| R9   | Conventional commits only (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).                       | [REQ] |
| R10  | Don't touch `pyproject.toml`, `.github/workflows/`, `AGENTS.md`, `CLAUDE.md`, `.claude/agents/**`, `.claude/hooks/**` without explicit approval. | [BLK] |

## 7. Definition of Done (by task type)

### New module
- [ ] Module file created with full type hints
- [ ] Module-level docstring
- [ ] Public API matches AGENTS.md contract
- [ ] `ruff check` clean
- [ ] `mypy` clean
- [ ] At least one smoke test (Fase 4+)

### Refactor (signature change)
- [ ] All callers updated in same commit
- [ ] Backward-compat shim only if explicitly requested
- [ ] `pytest` still green (or new tests added)
- [ ] `@code-reviewer` invoked

### Bug fix
- [ ] Reproduction test added (must fail before fix, pass after)
- [ ] Root cause identified in commit message
- [ ] No unrelated changes

### Docs
- [ ] Spanish for public files, English for governance
- [ ] No broken links
- [ ] Code samples run as-is

## 8. Anti-patterns (do NOT do)

| Anti-pattern                              | Correct alternative                                  |
|-------------------------------------------|------------------------------------------------------|
| `global libros_db`                        | Encapsulate in `Inventario` instance                 |
| Module-level `RUTA_DATOS = ...`           | Inject path via `PersistenciaJson(path)` constructor |
| `print("Error: ...")` in business layer  | `raise InventarioError(...)` or `logging.error(...)` |
| `sys.exit(0)` in middle of loop          | `break` or `return` from `main()`                   |
| Recursive ID generator                   | Iterative `while` loop                               |
| ISBN as identifier                       | SKU (universal) + `atributos['isbn']` for domain     |
| Domain logic in `modulos/`               | Move to `presets/<domain>.py`                        |
| `Dict[str, Any]` (legacy typing)         | `dict[str, Any]` (modern syntax)                     |
| Skipping `@code-reviewer` before commit   | Always audit, even for trivial changes              |
| `datos_basicos.py` for seed data         | Move to `presets/<domain>.py` as `seed` attribute   |

## 9. Permission matrix

| Command / file                                     | Permission | Source                |
|----------------------------------------------------|------------|-----------------------|
| `ruff check`, `ruff format`, `pytest`, `mypy`, `bandit` | Allow   | settings.json         |
| `git status`, `git diff`, `git log`                | Allow   | settings.json         |
| `python main.py`, `python -c`                      | Allow   | settings.json         |
| `git commit`, `git push`                           | Ask     | settings.json         |
| `pip install`                                      | Ask     | settings.json         |
| `rm -rf`, `git push --force/-f`, `DROP TABLE`, `TRUNCATE`, `Remove-Item -Recurse` | Deny | settings.json + block-rm.ps1 |
| Edit `AGENTS.md`, `CLAUDE.md`, `.github/workflows/ci.yml` | Deny    | settings.json         |
| Edit `.claude/agents/**`, `.claude/hooks/**`       | Deny    | settings.json         |
| Read `.env`, `**/secrets/**`, `**/.aws/**`         | Deny    | settings.json         |

## 10. References

- Roadmap: `/home/z/my-project/download/roadmap_01_inventario.md`
- Last session handover: `/home/z/my-project/download/traspasos/traspaso_fase_0_setup.md`
- Local state: `.claude/local/sessionstate.md`, `.claude/local/memory.md`
- Subagents (4 total):
  - `.claude/agents/quick-explorer.md` (haiku) -- read-only code locator
  - `.claude/agents/implementer.md` (sonnet) -- delegated execution of well-specified plans
  - `.claude/agents/code-reviewer.md` (sonnet) -- post-implementation compliance audit
  - `.claude/agents/architecture-reviewer.md` (opus, max 2/phase) -- pre-implementation design review
- Hooks: `.claude/hooks/block-rm.ps1` (active), `.claude/hooks/run-tests.ps1` (active from Fase 4)
## 11. Versioning and Tags

- **Versioning scheme**: semantic versioning `vMAJOR.MINOR.PATCH`.
  - `v0.X.0` per phase boundary (Fase 0 = v0.1.0, Fase 1 = v0.2.0, ..., Fase 5 = v1.0.0).
  - `v1.0.0` marks project complete (post-Fase 5).
  - Patch releases `vX.Y.Z` (Z > 0) reserved for hotfixes between phases.
- **Tag type**: annotated (`git tag -a`), not lightweight. Phase boundaries are release-like markers.
- **Cadence**: per phase boundary, NOT per task. Tasks are internal; phases are deliverables.
- **Push policy**: `git push origin <tag>` per-tag, NOT `git push --tags` (granular control, avoids accidental pushes of stale local tags).
- **Message format**: one-line: `Fase <N>: <one-line summary>`.
- **Retroactive application**: if a phase was closed without a tag, apply retroactively with `git tag -a v0.X.0 <hash> -m "<message>"` at the next opportunity. Do not skip -- phase boundaries without tags are a governance debt.
- **Verification**: after push, verify with `git ls-remote --tags origin | grep v0.X.0`. The returned hash is the tag object hash (not the commit hash) for annotated tags.

Example:

```bash
git tag -a v0.3.0 5695ba6 -m "Fase 2: DevOps pipeline (CI + Docker + docker-cleanup)"
git push origin v0.3.0
git ls-remote --tags origin | grep v0.3.0
```
