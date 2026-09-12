# Contribuir a inventario-cli-python

## Setup inicial
```bash
git clone https://github.com/javiersandovaltap-beep/inventario-cli-python.git
cd inventario-cli-python
python -m venv .venv
source .venv/Scripts/activate  # Git Bash en Windows
# .venv\Scripts\activate  # PowerShell
pip install -e ".[dev]"
pre-commit install
```

## Antes de commitear
```bash
ruff check . && ruff format --check . && pytest && mypy . && bandit -r . -ll
```

## Conventional commits
- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `refactor:` refactor sin cambio funcional
- `docs:` cambios en documentación
- `test:` cambios en tests
- `chore:` tareas de mantenimiento
