# Reglas de Arquitectura — inventario-cli-python

## Stack
- Python 3.11+ puro (sin dependencias externas en runtime)
- Persistencia: JSON inyectable (Strategy pattern)
- Tests: pytest
- Linting: ruff
- Type checking: mypy (modo non-strict)
- Container: Docker multi-stage con python:3.12-slim

## Arquitectura (Nivel 2)
- `modulos/item.py`: dataclass `Item` genérico (campos base + `atributos: dict`)
- `modulos/inventario.py`: clase `Inventario` con persistencia inyectable
- `modulos/persistencia.py`: implementación concreta `PersistenciaJson`
- `presets/base.py`: Protocol `Preset` (contrato de dominio)
- `presets/libreria_chilena.py`: implementación concreta de preset
- `modulos/gestion_datos.py`: lógica CRUD que opera sobre `Inventario`
- `modulos/menu.py`: presentación CLI (solo I/O)

## Reglas
1. (Separación) Nunca mezclar presentación (CLI/menu) con lógica de negocio
   (CRUD/reportes) ni con persistencia (JSON I/O).
2. (Manejo de errores) No usar print() para reportar errores del sistema.
   Usar logging o levantar excepciones específicas.
3. (Datos) Toda entrada del usuario debe ser validada antes de procesarse.
4. (Estado) No mutar estado global desde funciones de negocio. Encapsular
   estado en `Inventario`.
5. (Tests) Toda nueva funcionalidad debe incluir al menos un test smoke
   y un test de caso límite.
6. (Dominio) La lógica específica de un dominio (autores chilenos, categorías
   de ferretería, etc.) vive en `presets/`, no en `modulos/`.

## Comandos permitidos sin preguntar
- pytest, ruff check, ruff format, mypy .
- python main.py (para pruebas manuales)
- git status, git diff, git log

## Comandos que requieren aprobación manual
- git commit, git push
- pip install (cualquier paquete nuevo)
- Cualquier comando que afecte .github/workflows/ o pyproject.toml
