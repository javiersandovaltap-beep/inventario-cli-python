"""Concrete Preset for the Chilean bookstore domain."""

from __future__ import annotations

import unicodedata
from typing import Any

from modulos.item import Item


def _normalizar_nombre(nombre: str) -> str:
    """Normalize a name for accent-insensitive comparison.

    Uses NFKD decomposition to split accented chars into base + combining
    mark, drops the combining marks, then casefolds. This lets a user
    typing "Skarmeta" match the catalog entry "Skarmeta".

    Args:
        nombre: Name as typed or as stored in the catalog.

    Returns:
        A lowercase, accent-stripped representation of the name.

    """
    nfkd = unicodedata.normalize("NFKD", nombre)
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_acentos.casefold()


AUTORES_CHILENOS: tuple[str, ...] = (
    "Pablo Neruda",
    "Isabel Allende",
    "Luis Sepulveda",
    "Antonio Skarmeta",
    "Ariel Dorfman",
    "Diamela Eltit",
    "Roberto Bolano",
    "Marcela Serrano",
    "Jose Donoso",
    "Francisco Coloane",
    "Mariano Latorre",
    "Vicente Huidobro",
    "Juan Emar",
    "Volodia Teitelboim",
    "Maria Luisa Bombal",
    "Jorge Edwards",
    "Manuel Rojas",
)

_AUTORES_NORMALIZADOS: frozenset[str] = frozenset(_normalizar_nombre(a) for a in AUTORES_CHILENOS)


def _validar_autor(autor: str) -> bool:
    """Check if the author is in the Chilean authors catalog.

    Comparison is accent-insensitive and case-insensitive: "Skarmeta"
    matches "Skarmeta", "BOLANO" matches "Bolano".

    Args:
        autor: Author name as stored in Item.atributos["autor"].

    Returns:
        True if the author matches a catalog entry (after normalization),
        False otherwise.

    """
    return _normalizar_nombre(autor) in _AUTORES_NORMALIZADOS


class LibreriaChilena:
    """Preset for a Chilean bookstore inventory.

    Migrates the 30-book seed from modulos/datos_basicos.py and the
    Chilean author validator from modulos/validaciones.py. The seed
    maps the legacy ISBN field to the universal sku field and stores
    autor as an atributo, per the AGENTS.md section 4.9 contract.

    """

    nombre: str = "Libreria Chilena"
    slug: str = "libreria_chilena"
    schema_atributos: dict[str, type] = {"autor": str}
    atributos_requeridos: frozenset[str] = frozenset({"autor"})
    validadores_atributo: dict[str, Any] = {"autor": _validar_autor}

    seed: list[dict[str, Any]] = [
        {
            "id": 1,
            "sku": "ISBN001",
            "nombre": "Veinte poemas de amor",
            "precio": 12000.0,
            "stock": 15,
            "atributos": {"autor": "Pablo Neruda"},
        },
        {
            "id": 2,
            "sku": "ISBN002",
            "nombre": "La casa de los espiritus",
            "precio": 18500.0,
            "stock": 10,
            "atributos": {"autor": "Isabel Allende"},
        },
        {
            "id": 3,
            "sku": "ISBN003",
            "nombre": "El viejo que leia novelas de amor",
            "precio": 14000.0,
            "stock": 8,
            "atributos": {"autor": "Luis Sepulveda"},
        },
        {
            "id": 4,
            "sku": "ISBN004",
            "nombre": "Ardiente paciencia",
            "precio": 9900.0,
            "stock": 20,
            "atributos": {"autor": "Antonio Skarmeta"},
        },
        {
            "id": 5,
            "sku": "ISBN005",
            "nombre": "La muerte y la doncella",
            "precio": 11000.0,
            "stock": 5,
            "atributos": {"autor": "Ariel Dorfman"},
        },
        {
            "id": 6,
            "sku": "ISBN006",
            "nombre": "Residencia en la tierra",
            "precio": 15000.0,
            "stock": 12,
            "atributos": {"autor": "Pablo Neruda"},
        },
        {
            "id": 7,
            "sku": "ISBN007",
            "nombre": "Historia de una gaviota y del gato...",
            "precio": 13000.0,
            "stock": 9,
            "atributos": {"autor": "Luis Sepulveda"},
        },
        {
            "id": 8,
            "sku": "ISBN008",
            "nombre": "Mas alla del invierno",
            "precio": 19000.0,
            "stock": 7,
            "atributos": {"autor": "Isabel Allende"},
        },
        {
            "id": 9,
            "sku": "ISBN009",
            "nombre": "Los detectives salvajes",
            "precio": 22000.0,
            "stock": 4,
            "atributos": {"autor": "Roberto Bolano"},
        },
        {
            "id": 10,
            "sku": "ISBN010",
            "nombre": "Por la patria",
            "precio": 16000.0,
            "stock": 6,
            "atributos": {"autor": "Diamela Eltit"},
        },
        {
            "id": 11,
            "sku": "ISBN011",
            "nombre": "Canto general",
            "precio": 25000.0,
            "stock": 3,
            "atributos": {"autor": "Pablo Neruda"},
        },
        {
            "id": 12,
            "sku": "ISBN012",
            "nombre": "El cuaderno de Maya",
            "precio": 17500.0,
            "stock": 11,
            "atributos": {"autor": "Isabel Allende"},
        },
        {
            "id": 13,
            "sku": "ISBN013",
            "nombre": "Nombre de perro",
            "precio": 10500.0,
            "stock": 14,
            "atributos": {"autor": "Antonio Skarmeta"},
        },
        {
            "id": 14,
            "sku": "ISBN014",
            "nombre": "Manchas de sangre",
            "precio": 13500.0,
            "stock": 8,
            "atributos": {"autor": "Ariel Dorfman"},
        },
        {
            "id": 15,
            "sku": "ISBN015",
            "nombre": "El gaucho insufrible",
            "precio": 14500.0,
            "stock": 5,
            "atributos": {"autor": "Roberto Bolano"},
        },
        {
            "id": 16,
            "sku": "ISBN016",
            "nombre": "Poema 20",
            "precio": 5000.0,
            "stock": 25,
            "atributos": {"autor": "Pablo Neruda"},
        },
        {
            "id": 17,
            "sku": "ISBN017",
            "nombre": "Paula",
            "precio": 15500.0,
            "stock": 9,
            "atributos": {"autor": "Isabel Allende"},
        },
        {
            "id": 18,
            "sku": "ISBN018",
            "nombre": "Yakamari",
            "precio": 11500.0,
            "stock": 10,
            "atributos": {"autor": "Francisco Coloane"},
        },
        {
            "id": 19,
            "sku": "ISBN019",
            "nombre": "El camino de Santiago",
            "precio": 18000.0,
            "stock": 4,
            "atributos": {"autor": "Roberto Bolano"},
        },
        {
            "id": 20,
            "sku": "ISBN020",
            "nombre": "Lumperica",
            "precio": 17000.0,
            "stock": 6,
            "atributos": {"autor": "Diamela Eltit"},
        },
        {
            "id": 21,
            "sku": "ISBN021",
            "nombre": "Crepusculos",
            "precio": 12000.0,
            "stock": 8,
            "atributos": {"autor": "Mariano Latorre"},
        },
        {
            "id": 22,
            "sku": "ISBN022",
            "nombre": "Altazor",
            "precio": 16500.0,
            "stock": 7,
            "atributos": {"autor": "Vicente Huidobro"},
        },
        {
            "id": 23,
            "sku": "ISBN023",
            "nombre": "El obsceno pajaro de la noche",
            "precio": 21000.0,
            "stock": 3,
            "atributos": {"autor": "Jose Donoso"},
        },
        {
            "id": 24,
            "sku": "ISBN024",
            "nombre": "La ultima niebla",
            "precio": 12500.0,
            "stock": 9,
            "atributos": {"autor": "Maria Luisa Bombal"},
        },
        {
            "id": 25,
            "sku": "ISBN025",
            "nombre": "Adios, Munken",
            "precio": 14000.0,
            "stock": 5,
            "atributos": {"autor": "Jorge Edwards"},
        },
        {
            "id": 26,
            "sku": "ISBN026",
            "nombre": "Un ano de vida",
            "precio": 19500.0,
            "stock": 2,
            "atributos": {"autor": "Volodia Teitelboim"},
        },
        {
            "id": 27,
            "sku": "ISBN027",
            "nombre": "La ciudad de los cesares",
            "precio": 13000.0,
            "stock": 6,
            "atributos": {"autor": "Francisco Coloane"},
        },
        {
            "id": 28,
            "sku": "ISBN028",
            "nombre": "Miltin 1934",
            "precio": 15000.0,
            "stock": 4,
            "atributos": {"autor": "Juan Emar"},
        },
        {
            "id": 29,
            "sku": "ISBN029",
            "nombre": "El lugar sin limites",
            "precio": 16000.0,
            "stock": 5,
            "atributos": {"autor": "Jose Donoso"},
        },
        {
            "id": 30,
            "sku": "ISBN030",
            "nombre": "Hijo de ladron",
            "precio": 11000.0,
            "stock": 12,
            "atributos": {"autor": "Manuel Rojas"},
        },
    ]

    def validar_item(self, item: Item) -> tuple[bool, str | None]:
        """Validate item.atributos against the preset's contract.

        Validation rules (per Preset protocol):
        1. Every attribute in atributos_requeridos must be present.
            Missing required -> (False, error msg naming the attribute).
        2. For every attribute in validadores_atributo that is present,
            the validator is applied. Validator returning False ->
            (False, error msg naming the attribute).
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
        for req in self.atributos_requeridos:
            if req not in item.atributos:
                return False, f"Missing required attribute '{req}'"
        for attr_name, validator in self.validadores_atributo.items():
            if attr_name in item.atributos:
                value = item.atributos[attr_name]
                if not validator(value):
                    return False, f"Invalid value for attribute '{attr_name}'"
        return True, None


PRESET_LIBRERIA_CHILENA: LibreriaChilena = LibreriaChilena()
