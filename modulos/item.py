"""Generic inventory item dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    """Generic inventory item with extensible domain attributes.

    Attributes:
        id: Unique identifier for the item.
        sku: Stock Keeping Unit, universal identifier (replaces ISBN).
        nombre: Name or title of the item.
        precio: Price of the item.
        stock: Quantity available in inventory.
        atributos: Dictionary for domain-specific fields (autor, categoria,
            marca, etc.). Defaults to an empty dict per instance.

    """

    id: int
    sku: str
    nombre: str
    precio: float
    stock: int
    atributos: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the Item to a JSON-serializable dictionary.

        Returns:
            A dictionary representation of the Item. The atributos dict is
            shallow-copied so the caller can mutate the result without
            affecting the original Item.

        """
        return {
            "id": self.id,
            "sku": self.sku,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
            "atributos": dict(self.atributos),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Item:
        """Create an Item from a dictionary.

        Unknown keys in the input data are ignored silently. If atributos
        is missing, it defaults to an empty dict. The input data is not
        mutated.

        Args:
            data: Dictionary containing item data.

        Returns:
            A new Item instance constructed from the known keys in data.

        """
        return cls(
            id=data.get("id", 0),
            sku=data.get("sku", ""),
            nombre=data.get("nombre", ""),
            precio=data.get("precio", 0.0),
            stock=data.get("stock", 0),
            atributos=dict(data.get("atributos", {})),
        )
