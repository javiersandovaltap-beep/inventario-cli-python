#!/usr/bin/env python3
"""Inventory CLI - main entry point.

Constructs the Inventario instance with injected persistence and preset,
loads initial data, and runs the menu loop.
"""

import sys

from modulos.gestion_datos import (
    actualizar_stock,
    agregar_libro,
    buscar_libro,
    eliminar_libro,
    generar_reporte,
    listar_libros,
)
from modulos.inventario import Inventario
from modulos.menu import mostrar_menu, pedir_opcion
from modulos.persistencia import PersistenciaJson
from presets.libreria_chilena import PRESET_LIBRERIA_CHILENA


def main() -> None:
    """Entry point. Initializes inventory and runs the menu loop."""
    inventario = Inventario(
        persistencia=PersistenciaJson("data/libros.json"),
        preset=PRESET_LIBRERIA_CHILENA,
    )
    inventario.cargar_inicial()
    print(f"📂 Datos cargados — {len(inventario.listar())} libros.\n")

    opciones = {
        1: lambda: listar_libros(inventario),
        2: lambda: agregar_libro(inventario),
        3: lambda: buscar_libro(inventario),
        4: lambda: actualizar_stock(inventario),
        5: lambda: eliminar_libro(inventario),
        6: lambda: generar_reporte(inventario),
    }

    while True:
        mostrar_menu()
        opcion = pedir_opcion()

        if opcion == -1:
            print("Entrada inválida. Por favor ingrese un número entre 0 y 6.")
            continue

        if opcion == 0:
            print("\n¡Hasta pronto! Cerrando el sistema...\n")
            sys.exit(0)

        opciones[opcion]()


if __name__ == "__main__":
    main()
