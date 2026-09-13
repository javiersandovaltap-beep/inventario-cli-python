"""Inventory persistence layer with injectable path.

Provides PersistenciaJson (configurable path, Item-based serialization)
and PersistenciaError for error handling.

"""

from __future__ import annotations

import json
from pathlib import Path

from modulos.item import Item


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
                self._ruta,
                mensaje=f"Expected list, got {type(datos).__name__}",
            )
        return [Item.from_dict(d) for d in datos]

    def _asegurar_directorio(self) -> None:
        """Create the parent directory if it does not exist."""
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
