# Inventario CLI -- Python puro con presets de dominio

Sistema de gestion de inventario desarrollado en Python puro, sin frameworks
ni librerias externas. Permite administrar catalogos de productos con
presets de dominio (libros, componentes electronicos, lo que sea),
persistencia en JSON e interfaz de consola interactiva.

El proyecto nacio como un gestor de libreria especializada en literatura
chilena y fue refactorizado a una arquitectura Nivel 2: nucleo generico
(`Item`, `Inventario`, `PersistenciaJson`) + presets de dominio que
definen los contratos especificos (validadores, atributos requeridos, seed
data). Hoy se incluye el preset `LibreriaChilena`; crear uno nuevo es
trivial (ver seccion 4).

---

## 1. Demo

```
========================================
    INVENTARIO CLI
========================================
  1. Listar items
  2. Agregar item
  3. Buscar item
  4. Actualizar stock
  5. Eliminar item
  6. Generar reporte
  0. Salir
----------------------------------------

[+] Datos cargados -- 30 items.

=============================================
       REPORTE DE INVENTARIO
=============================================
  Items en catalogo     : 30
  Unidades totales     : 218
  Valor del inventario : $ 4.345.000
  Item destacado       : Pablo Neruda (autor con mas titulos)
  Stock critico        : 4 items con menos de 5 uds.
=============================================
```

---

## 2. Funcionalidades

- **Listar items** -- tabla formateada con SKU, nombre, precio y stock.
- **Agregar item** -- valida SKU unico y atributos requeridos por el
  preset activo (p. ej. autor chileno para `LibreriaChilena`).
- **Buscar item** -- por SKU exacto o coincidencia parcial de nombre.
- **Actualizar stock** -- registra entradas y salidas con validacion de
  stock disponible.
- **Eliminar item** -- con confirmacion previa del usuario.
- **Generar reporte** -- estadisticas en tiempo real: valor total, stock
  critico y agregaciones por atributo (autor destacado, etc.).
- **Persistencia JSON** -- los datos se guardan en
  `data/inventario_libreria_chilena.json` tras cada operacion.

---

## 3. Arquitectura

El sistema sigue una separacion en tres capas:

```
+---------------------------+        +-----------------------+
|  CLI (main.py, modulos/)  | -----> |  Inventario (core)    |
|  menu, captura, CRUD      |        |  estado + operaciones |
+---------------------------+        +----------+------------+
                                               |
                                               | inyecta
                                               v
                          +--------------------+------------+
                          |  Preset + PersistenciaJson        |
                          |  (dominio + almacenamiento)        |
                          +------------------------------------+
```

### Componentes principales

| Componente        | Ubicacion                        | Responsabilidad                                          |
|-------------------|----------------------------------|----------------------------------------------------------|
| `Item`            | `modulos/item.py`               | Dataclass generico: `id`, `sku`, `nombre`, `precio`, `stock`, `atributos: dict[str, Any]`. Punto de extension para campos de dominio. |
| `Inventario`      | `modulos/inventario.py`         | Encapsula el estado (lista de items) y las operaciones CRUD (`agregar`, `eliminar`, `actualizar_stock`, `buscar`, `listar`, `generar_reporte`). Recibe preset y persistencia via inyeccion. |
| `Preset`          | `presets/base.py`               | Protocol (structural typing) que define el contrato de dominio: `validar_item(item)`, `atributos_requeridos`, `seed` (lista de items precargados). Sin herencia forzada. |
| `PersistenciaJson`| `modulos/persistencia.py`       | Strategy de persistencia: recibe ruta de archivo JSON en el constructor, hace `cargar()` y `guardar()`. Inyectable en `Inventario`. |
| `LibreriaChilena` | `presets/libreria_chilena.py`   | Implementacion de `Preset` para libreria chilena: valida autor chileno, ISBN unico (en `atributos['isbn_legacy']`), y trae 30 items de seed. |

### Flujo de arranque

`main.py` construye un `Inventario` con `PersistenciaJson` (path) y
`PRESET_LIBRERIA_CHILENA` (preset), llama a `inventario.cargar_inicial()`
para cargar datos seed si el archivo JSON esta vacio, y entra al loop
del menu. Toda la logica de dominio vive en el preset; el core no sabe
que esta manejando libros chilenos.

---

## 4. Presets

El sistema incluye un preset de referencia: `LibreriaChilena`. Para crear
un preset nuevo (p. ej. para electronic components, productos agricolas,
etc.) hay tres pasos:

1. Crear `presets/<dominio>.py` con:
   - Una instancia de la clase `Preset` (o una clase que satisfaga el
     Protocol en `presets/base.py`).
   - `atributos_requeridos: list[str]` (p. ej. `["marca", "modelo"]`).
   - `validar_item(item: Item) -> bool` -- logica de dominio.
   - `seed: list[Item]` -- items precargados para primera ejecucion.
2. Exportar la instancia como `PRESET_<DOMINIO>` en `presets/<dominio>.py`.
3. En `main.py`, reemplazar la linea `preset=PRESET_LIBRERIA_CHILENA` por
   `preset=PRESET_<DOMINIO>` y ajustar el path de `PersistenciaJson` a
   `data/inventario_<dominio>.json`.

No requiere tocar `modulos/` -- el core es agnostico al dominio.

---

## 5. Estructura del proyecto

```
inventario-cli-python/
+-- main.py                              # Punto de entrada + loop del menu
+-- README.md
+-- LICENSE
+-- CONTRIBUTING.md
+-- pyproject.toml                       # Metadatos + ruff/mypy config
+-- .pre-commit-config.yaml              # ruff + trailing-whitespace + EOF fixer
+-- AGENTS.md                             # Governance (English)
+-- CLAUDE.md                             # Claude Code settings (English)
+-- data/
|   +-- inventario_libreria_chilena.json  # Datos persistentes (30 items)
+-- modulos/
|   +-- __init__.py                       # Re-exports + __all__ (API publica)
|   +-- item.py                           # Item dataclass generico
|   +-- inventario.py                     # Inventario class (estado + CRUD)
|   +-- persistencia.py                   # PersistenciaJson (Strategy)
|   +-- gestion_datos.py                  # Funciones CLI CRUD (presentation)
|   +-- menu.py                           # mostrar_menu + pedir_opcion
|   +-- validaciones.py                   # Place-holder (Fase 3: input validators)
|   +-- funciones_utiles.py               # input_float, generar_id
+-- presets/
|   +-- __init__.py
|   +-- base.py                           # Preset Protocol
|   +-- libreria_chilena.py               # LibreriaChilena preset
+-- scripts/
    +-- ascii_cleanup.py                  # Script de housekeeping ASCII
```

---

## 6. Instalacion y ejecucion

**Requisitos:** Python 3.11 o superior. No requiere dependencias externas.

```bash
# 1. Clonar el repositorio
git clone https://github.com/javiersandovaltap-beep/inventario-cli-python.git

# 2. Entrar a la carpeta
cd inventario-cli-python

# 3. (Opcional) crear y activar venv
python -m venv .venv
source .venv/Scripts/activate    # Git Bash en Windows
# .venv\Scripts\activate.bat     # cmd.exe
# .venv\Scripts\Activate.ps1     # PowerShell

# 4. Ejecutar
python main.py
```

En la primera ejecucion se cargan 30 items desde el seed del preset
`LibreriaChilena` y se persisten en `data/inventario_libreria_chilena.json`.
A partir de la segunda ejecucion, el sistema carga el estado guardado.

Para desarrolladores: el hook `pre-commit` valida `ruff check --fix` +
`ruff format` + trailing-whitespace + end-of-file-fixer en cada commit.

```bash
pre-commit install
pre-commit run --all-files
```

---

## 7. Roadmap

El proyecto sigue un roadmap por fases. Estado actual:

- **Fase 0** (cierre): arquitectura Nivel 2 completa, governance ASCII,
  branding "Inventario CLI" consolidado, 7 commits locales listos para push.
- **Fase 1** (siguiente): L-04 iterative ID gen, L-03 JSON schema validation.
- **Fase 3** (planificado): type hints, migracion de validadores a
  `modulos/validaciones.py`, sustitucion de `sys.exit(0)` por `break`.

El roadmap completo vive fuera del repo (governance privada). Para
contribuir, ver `CONTRIBUTING.md`.

---

## 8. Licencia

Ver `LICENSE`.

---

## 9. Autor

**Javier Sandoval Tapia**
[GitHub](https://github.com/javiersandovaltap-beep)
