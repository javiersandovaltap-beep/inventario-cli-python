#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Librería Autores Chilenos — Sistema de Gestión de Inventario | Python puro | PEP 8 + Zen of Python
"""

import sys
from modulos.datos_basicos import DATOS_INICIALES
from modulos.menu import mostrar_menu, pedir_opcion
from modulos.persistencia import cargar_libros, guardar_libros, existe_archivo
from modulos.gestion_datos import (
    listar_libros, agregar_libro, buscar_libro,
    actualizar_stock, eliminar_libro, generar_reporte
)

libros_db = []
ids_set = set()
isbns_set = set()


def cargar_datos_iniciales():
    """Carga libros desde libros.json si existe, o desde datos_basicos.py si es primera ejecución."""
    global libros_db

    if existe_archivo():
        datos = cargar_libros()
        libros_db.extend(datos)
        for libro in libros_db:
            ids_set.add(libro['id'])
            isbns_set.add(libro['isbn'])
        print(f"📂 Datos cargados desde archivo — {len(libros_db)} libros.")
    else:
        for dato in DATOS_INICIALES:
            nuevo_id = len(libros_db) + 1
            libros_db.append({
                'id': nuevo_id,
                'titulo': dato['titulo'],
                'autor': dato['autor'],
                'isbn': dato['isbn'],
                'precio': dato['precio'],
                'stock': dato['stock']
            })
            ids_set.add(nuevo_id)
            isbns_set.add(dato['isbn'])
        guardar_libros(libros_db)
        print(f"🆕 Primera ejecución — {len(libros_db)} libros cargados y guardados.")


def main():
    """Punto de entrada del sistema. Inicializa datos y ejecuta el bucle principal."""
    cargar_datos_iniciales()

    opciones = {
        1: lambda: listar_libros(libros_db),
        2: lambda: agregar_libro(libros_db, ids_set, isbns_set),
        3: lambda: buscar_libro(libros_db),
        4: lambda: actualizar_stock(libros_db),
        5: lambda: eliminar_libro(libros_db, ids_set, isbns_set),
        6: lambda: generar_reporte(libros_db),
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
