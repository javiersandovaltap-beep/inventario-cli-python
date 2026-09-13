"""Inventory persistence layer with injectable path.

Provides PersistenciaJson (configurable path, Item-based serialization)
and legacy wrappers (guardar_libros, cargar_libros, existe_archivo)
that preserve backward compatibility with main.py and gestion_datos.py
during the transition to the new Inventario class (Tarea 0.5).

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modulos.item import Item

# Default path used by legacy wrappers. Will be removed in Tarea 0.5
# when main.py migrates to PersistenciaJson directly.
_RUTA_DEFAULT: Path = Path(__file__).resolve().parent.parent / "data" / "libros.json"


class PersistenciaError(Exception):
    """Raised when the persistence layer cannot read or write data.

    Attributes:
        ruta: Path of the file that caused the error.
        causa: Original exception (if any).

    """

    def __init__(
        self,
        ruta: Path,
        causa: Exception | None = None,
        mensaje: str = "",
    ) -> None:
        """Initialize a PersistenciaError exception.

        Args:
            ruta: Path of the file that caused the error.
            causa: Original exception (if any).
            mensaje: Custom error message (optional).

        """
        self.ruta = ruta
        self.causa = causa
        msg = mensaje or f"Persistencia error at {ruta}"
        if causa:
            msg = f"{msg}: {causa}"
        super().__init__(msg)


class PersistenciaJson:
    """JSON-based persistence for inventory items.

    The path is injected via the constructor, eliminating the module-level
    RUTA_DATOS global. Items are serialized via to_dict / from_dict so the
    on-disk format matches the Item contract (AGENTS.md section 4.1).

    """

    def __init__(self, ruta: Path | str) -> None:
        """Initialize the persistence layer with a file path.

        Args:
            ruta: Path to the JSON file. Can be a string or a Path object.

        """
        self._ruta: Path = Path(ruta)

    @property
    def ruta(self) -> Path:
        """Return the configured file path."""
        return self._ruta

    def existe(self) -> bool:
        """Check if the persistence file exists on disk.

        Returns:
            True if the file exists, False otherwise.

        """
        return self._ruta.exists()

    def guardar(self, items: list[Item]) -> None:
        """Serialize items to the JSON file.

        Creates parent directories if they do not exist. Overwrites the
        file if it already exists.

        Args:
            items: List of Item instances to serialize.

        Raises:
            PersistenciaError: If the file cannot be written.

        """
        self._asegurar_directorio()
        datos = [item.to_dict() for item in items]
        try:
            self._ruta.write_text(
                json.dumps(datos, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            raise PersistenciaError(self._ruta, causa=exc, mensaje="No se pudo escribir") from exc

    def cargar(self) -> list[Item]:
        """Deserialize items from the JSON file.

        Returns:
            List of Item instances. Returns an empty list if the file
            does not exist.

        Raises:
            PersistenciaError: If the file exists but cannot be parsed
                (corrupt JSON or non-list structure).

        """
        if not self.existe():
            return []
        try:
            datos = json.loads(self._ruta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PersistenciaError(
                self._ruta, causa=exc, mensaje="JSON corrupto o ilegible"
            ) from exc
        if not isinstance(datos, list):
            raise PersistenciaError(
                self._ruta, mensaje=f"Expected list, got {type(datos).__name__}"
            )
        return [Item.from_dict(d) for d in datos]

    def _asegurar_directorio(self) -> None:
        """Create the parent directory if it does not exist."""
        self._ruta.parent.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Legacy wrappers (backward compatibility with main.py and gestion_datos.py).
# These will be removed in Tarea 0.5 when callers migrate to PersistenciaJson
# directly. Do NOT use these in new code.
# ============================================================================

_SINGLETON: PersistenciaJson = PersistenciaJson(_RUTA_DEFAULT)


def _legacy_dict_to_item(d: dict[str, Any]) -> Item:
    """Convert a legacy dict (titulo/autor/isbn) to an Item instance.

    Legacy dicts use the original data shape from datos_basicos.py
    (deleted in Tarea 0.3). This function maps legacy keys to the
    Item contract: titulo -> nombre, isbn -> sku, autor -> atributos.autor.

    Args:
        d: Legacy dict with keys id, titulo, autor, isbn, precio, stock.

    Returns:
        An Item instance with the legacy data mapped to the new schema.

    """
    return Item(
        id=d["id"],
        sku=d.get("isbn", ""),
        nombre=d.get("titulo", ""),
        precio=d.get("precio", 0.0),
        stock=d.get("stock", 0),
        atributos={"autor": d.get("autor", "")},
    )


def _item_to_legacy_dict(item: Item) -> dict[str, Any]:
    """Convert an Item instance to a legacy dict (titulo/autor/isbn).

    Args:
        item: The Item instance to convert.

    Returns:
        A dict with keys id, titulo, autor, isbn, precio, stock --
        the format expected by main.py and gestion_datos.py.

    """
    return {
        "id": item.id,
        "titulo": item.nombre,
        "autor": item.atributos.get("autor", ""),
        "isbn": item.sku,
        "precio": item.precio,
        "stock": item.stock,
    }


def _is_legacy_format(datos: list[Any]) -> bool:
    """Detect if a list of dicts uses the legacy format.

    Legacy format dicts have a 'titulo' key. New format dicts have a
    'nombre' key. This function inspects the first dict to decide.

    Args:
        datos: List of dicts loaded from JSON.

    Returns:
        True if the data is in legacy format, False otherwise. Returns
        False for empty lists (treated as new format by default).

    """
    if not datos:
        return False
    first = datos[0]
    if not isinstance(first, dict):
        return False
    return "titulo" in first and "nombre" not in first


def guardar_libros(libros_db: list[dict[str, Any]]) -> None:
    """Legacy wrapper. Converts dicts to Items and delegates to PersistenciaJson.

    Args:
        libros_db: List of legacy dicts (with keys id, titulo, autor, isbn,
            precio, stock).

    """
    items = [_legacy_dict_to_item(d) for d in libros_db]
    _SINGLETON.guardar(items)


def cargar_libros() -> list[dict[str, Any]] | None:
    """Legacy wrapper. Returns legacy dicts, or None if file does not exist.

    Handles both legacy on-disk format (titulo/autor/isbn keys) and new
    format (nombre/sku/atributos keys). The returned dicts always use the
    legacy format expected by main.py and gestion_datos.py.

    Returns:
        List of legacy dicts, or None if the file does not exist.

    Raises:
        PersistenciaError: If the file exists but cannot be parsed.

    """
    if not _SINGLETON.existe():
        return None
    # Read raw JSON to detect format before Item conversion.
    try:
        datos = json.loads(_SINGLETON.ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersistenciaError(
            _SINGLETON.ruta, causa=exc, mensaje="JSON corrupto o ilegible"
        ) from exc
    if not isinstance(datos, list):
        raise PersistenciaError(
            _SINGLETON.ruta,
            mensaje=f"Expected list, got {type(datos).__name__}",
        )
    if _is_legacy_format(datos):
        # Already in legacy format, return as-is.
        return datos
    # New format: convert Items to legacy dicts.
    items = [Item.from_dict(d) for d in datos]
    return [_item_to_legacy_dict(item) for item in items]


def existe_archivo() -> bool:
    """Legacy wrapper. Checks if the persistence file exists."""
    return _SINGLETON.existe()
