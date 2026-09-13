"""Domain preset protocol for inventory CLI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from modulos.item import Item


class Preset(Protocol):
    """Contract for domain-specific inventory presets.

    A preset encapsulates domain knowledge (name, slug, attribute
    schema, validators, seed data) so the core inventory module stays
    domain-agnostic.

    Attributes:
        nombre: Human-readable domain name.
        slug: Machine-readable identifier.
        schema_atributos: Mapping of attribute name to expected type.
        atributos_requeridos: Subset of schema_atributos keys that must
            be present in every valid item. Missing required attributes
            cause validar_item to return (False, error msg).
        validadores_atributo: Mapping of attribute name to validator
            callable. Each validator takes the attribute value and
            returns True if valid, False otherwise.
        seed: List of dicts, each compatible with Item.from_dict,
            used to bootstrap an empty inventory.

    """

    nombre: str
    slug: str
    schema_atributos: dict[str, type]
    atributos_requeridos: frozenset[str]
    validadores_atributo: dict[str, Callable[[Any], bool]]
    seed: list[dict[str, Any]]

    def validar_item(self, item: Item) -> tuple[bool, str | None]:
        """Validate an Item against this preset's contract.

        Validation rules:
        1. Every attribute in atributos_requeridos must be present in
           item.atributos. Missing required -> (False, error msg).
        2. For every attribute in validadores_atributo that is present
           in item.atributos, the validator is applied. Validator
           returning False -> (False, error msg naming the attribute).
        3. Attributes in item.atributos not in schema_atributos are
           ignored (presets do not reject unknown attributes; this
           allows items to carry extra metadata the preset does not
           care about).

        Args:
            item: The Item to validate.

        Returns:
            A tuple (ok, error). ok is True if all required attributes
            are present and all validators pass. ok is False otherwise;
            error contains a human-readable message.

        """
        ...
