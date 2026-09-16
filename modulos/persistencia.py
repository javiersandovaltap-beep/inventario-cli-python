"""Inventory persistence layer with injectable path.

Provides PersistenciaJson (configurable path, Item-based serialization)
and PersistenciaError for error handling. cargar() validates the JSON
schema and isolates corrupt files to {ruta}.corrupt-{timestamp} before
raising PersistenciaError (Tarea 3.1, L-03).

"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from modulos.item import Item

_LOGGER = logging.getLogger(__name__)

# Schema for the JSON persistence format (Tarea 3.1, L-03).
# Maps each required top-level key to its accepted type(s).
# Bool is a subclass of int in Python -- the validator rejects bool
# for non-bool fields explicitly to avoid silent type coercion.
_SCHEMA: dict[str, tuple[type, ...]] = {
    "id": (int,),
    "sku": (str,),
    "nombre": (str,),
    "precio": (int, float),
    "stock": (int,),
    "atributos": (dict,),
}


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
        file if it already exists. The output ends with a trailing newline
        to satisfy the end-of-file-fixer pre-commit hook.

        Args:
            items: List of Item instances to serialize.

        Raises:
            PersistenciaError: If the file cannot be written.

        """
        self._asegurar_directorio()
        datos = [item.to_dict() for item in items]
        try:
            self._ruta.write_text(
                json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
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
                (corrupt JSON, non-list structure, or schema validation
                failure). The corrupt file is renamed to
                ``{ruta}.corrupt-{timestamp}`` before raising, so the
                caller (typically ``Inventario.cargar_inicial``) can
                fall back to ``preset.seed`` without re-reading the
                corrupt data.

        """
        if not self.existe():
            return []
        try:
            datos = json.loads(self._ruta.read_text(encoding="utf-8"))
            if not isinstance(datos, list):
                raise ValueError(f"Expected list, got {type(datos).__name__}")
            self._validar_schema(datos)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            corrupt_path = self._aislar_corrupto()
            _LOGGER.warning(
                "Persistencia error en %s, aislado en %s: %s",
                self._ruta,
                corrupt_path,
                exc,
            )
            raise PersistenciaError(
                self._ruta,
                causa=exc,
                mensaje=f"Datos corruptos, aislados en {corrupt_path}",
            ) from exc
        return [Item.from_dict(d) for d in datos]

    def _aislar_corrupto(self) -> Path:
        """Rename the persistence file to a forensic ``.corrupt-{timestamp}`` path.

        The original file is moved to
        ``{ruta}.corrupt-{YYYYMMDDTHHMMSSffffff}``. The timestamp uses
        compact ISO 8601 with microsecond resolution (no colons) for
        Windows filesystem compatibility. If a corrupt file with the
        same timestamp already exists (extremely unlikely with
        microsecond resolution), a counter is appended.

        Returns:
            The new path of the renamed file.

        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        corrupt_path = self._ruta.with_name(f"{self._ruta.name}.corrupt-{timestamp}")
        counter = 1
        while corrupt_path.exists():
            corrupt_path = self._ruta.with_name(f"{self._ruta.name}.corrupt-{timestamp}-{counter}")
            counter += 1
        self._ruta.rename(corrupt_path)
        return corrupt_path

    def _validar_schema(self, datos: list) -> None:
        """Validate that ``datos`` is a list of dicts matching the Item schema.

        Args:
            datos: Parsed JSON data (expected list of dicts).

        Raises:
            ValueError: If any item is missing a required key or has a
                wrong type. Bool values are rejected for non-bool fields
                (bool subclasses int in Python, so an explicit check is
                needed to prevent silent type coercion).

        """
        for i, item in enumerate(datos):
            if not isinstance(item, dict):
                raise ValueError(f"Item {i}: expected dict, got {type(item).__name__}")
            for key, expected_types in _SCHEMA.items():
                if key not in item:
                    raise ValueError(f"Item {i}: missing key '{key}'")
                value = item[key]
                if isinstance(value, bool) and bool not in expected_types:
                    expected_names = "/".join(t.__name__ for t in expected_types)
                    raise ValueError(f"Item {i}: key '{key}' got bool, expected {expected_names}")
                if not isinstance(value, expected_types):
                    actual = type(value).__name__
                    expected_names = "/".join(t.__name__ for t in expected_types)
                    raise ValueError(
                        f"Item {i}: key '{key}' expected {expected_names}, got {actual}"
                    )

    def _asegurar_directorio(self) -> None:
        """Create the parent directory if it does not exist."""
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
