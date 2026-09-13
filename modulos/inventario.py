"""Inventory state encapsulation with injected persistence and preset."""

from __future__ import annotations

from collections import Counter
from typing import Any

from modulos.item import Item
from modulos.persistencia import PersistenciaJson
from presets.base import Preset


class Inventario:
    """Encapsulate inventory state and delegate persistence and validation.

    The Inventario class holds the internal item list, SKU set, and ID set
    as private attributes. Persistence and domain validation are injected
    via the constructor, following the Strategy and Dependency Injection
    patterns. No global state is used.

    Attributes:
        _persistencia: The persistence backend (e.g. PersistenciaJson).
        _preset: The domain preset providing validation and seed data.
        _items: Internal list of Item instances.
        _skus: Set of casefolded SKUs for duplicate detection.
        _ids: Set of integer IDs for ID generation.

    """

    def __init__(self, persistencia: PersistenciaJson, preset: Preset) -> None:
        """Initialize the inventory with injected dependencies.

        Args:
            persistencia: The persistence backend for loading and saving.
            preset: The domain preset for validation and seed data.

        """
        self._persistencia: PersistenciaJson = persistencia
        self._preset: Preset = preset
        self._items: list[Item] = []
        self._skus: set[str] = set()
        self._ids: set[int] = set()

    def agregar(self, item: Item) -> bool:
        """Add an item to the inventory after validation.

        Validates the item against the preset and checks for duplicate
        SKUs. Does not persist the change; the caller must call guardar().

        Args:
            item: The Item to add.

        Returns:
            True if the item was added. False if validation failed or
            the SKU already exists in the inventory.

        """
        ok, _msg = self._preset.validar_item(item)
        if not ok:
            return False
        if item.sku.casefold() in self._skus:
            return False
        self._items.append(item)
        self._skus.add(item.sku.casefold())
        self._ids.add(item.id)
        return True

    def eliminar(self, sku: str) -> bool:
        """Remove an item from the inventory by SKU.

        Args:
            sku: The SKU of the item to remove. Matched case-insensitively.

        Returns:
            True if the item was found and removed. False if no item
            with the given SKU exists.

        """
        target = sku.casefold()
        for i, item in enumerate(self._items):
            if item.sku.casefold() == target:
                self._items.pop(i)
                self._skus.discard(target)
                self._ids.discard(item.id)
                return True
        return False

    def buscar(self, sku_o_nombre: str) -> list[Item]:
        """Find items by exact SKU or partial name match.

        The search is case-insensitive. Returns all items whose SKU
        exactly matches the input OR whose nombre contains the input
        as a substring.

        Args:
            sku_o_nombre: The SKU or name fragment to search for.

        Returns:
            A list of matching Item instances. Empty list if no matches.

        """
        termino = sku_o_nombre.casefold()
        return [
            item
            for item in self._items
            if item.sku.casefold() == termino or termino in item.nombre.casefold()
        ]

    def actualizar_stock(self, sku: str, delta: int, es_venta: bool) -> bool:
        """Update the stock of an item identified by SKU.

        Args:
            sku: The SKU of the item to update. Matched case-insensitively.
            delta: The quantity to apply. For sales, this is the number of
                units sold (positive int). For restocks, the number of
                units added (positive int).
            es_venta: If True, delta is subtracted from stock (sale). If
                False, delta is added to stock (restock).

        Returns:
            True if the stock was updated. False if the SKU was not found
            or if a sale would result in negative stock.

        """
        target = sku.casefold()
        for item in self._items:
            if item.sku.casefold() == target:
                if es_venta:
                    if item.stock - delta < 0:
                        return False
                    item.stock -= delta
                else:
                    item.stock += delta
                return True
        return False

    def listar(self) -> list[Item]:
        """Return a shallow copy of the internal item list.

        Returns:
            A new list containing all Item instances. Callers can iterate
            and mutate the returned list without affecting internal state.

        """
        return list(self._items)

    def cargar(self) -> None:
        """Load items from the persistence backend.

        Replaces the internal item list, SKU set, and ID set with the
        data loaded from persistence. If persistence returns an empty
        list, the internal state is cleared.
        """
        items = self._persistencia.cargar()
        self._items = list(items)
        self._skus = {item.sku.casefold() for item in self._items}
        self._ids = {item.id for item in self._items}

    def cargar_inicial(self) -> None:
        """Load from persistence, or seed from preset if empty.

        Calls cargar() first. If the inventory is empty after loading
        (file does not exist or is empty), populates from the preset
        seed and persists the seed data. Idempotent: a second call when
        items already exist does nothing.
        """
        self.cargar()
        if not self._items:
            for datos in self._preset.seed:
                item = Item.from_dict(datos)
                self._items.append(item)
                self._skus.add(item.sku.casefold())
                self._ids.add(item.id)
            self.guardar()

    def guardar(self) -> None:
        """Persist the current item list to the persistence backend."""
        self._persistencia.guardar(self._items)

    def generar_reporte(self) -> dict[str, Any]:
        """Generate a summary report of the current inventory.

        Returns:
            A dictionary with keys: total_items (int), total_unidades
            (int), valor_inventario (float), stock_bajo (list[Item]
            with stock < 5), top_autor (str or None).

        """
        if not self._items:
            return {
                "total_items": 0,
                "total_unidades": 0,
                "valor_inventario": 0.0,
                "stock_bajo": [],
                "top_autor": None,
            }

        total_items = len(self._items)
        total_unidades = sum(item.stock for item in self._items)
        valor_inventario = sum(item.precio * item.stock for item in self._items)
        stock_bajo = [item for item in self._items if item.stock < 5]

        autores = [
            item.atributos.get("autor") for item in self._items if item.atributos.get("autor")
        ]
        top_autor = Counter(autores).most_common(1)[0][0] if autores else None

        return {
            "total_items": total_items,
            "total_unidades": total_unidades,
            "valor_inventario": valor_inventario,
            "stock_bajo": stock_bajo,
            "top_autor": top_autor,
        }
