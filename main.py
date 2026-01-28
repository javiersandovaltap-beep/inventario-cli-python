#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from modulos.datos_basicos import DATOS_INICIALES
from modulos.menu import mostrar_menu, pedir_opcion
from modulos.gestion_datos import (
    listar_libros, agregar_libro, buscar_libro,
    actualizar_stock, eliminar_libro, generar_reporte
)

libros_db = []
ids_set = set()
isbns_set = set()

def cargar_datos_iniciales():
    print("Cargando base de datos inicial...")
    count = 0
    for dato in DATOS_INICIALES:
        nuevo_id = len(libros_db) + 1
        nuevo_libro = {
            'id': nuevo_id,
            'titulo': dato['titulo'],
            'autor': dato['autor'],
            'isbn': dato['isbn'],
            'precio': dato['precio'],
            'stock': dato['stock']
        }
        libros_db.append(nuevo_libro)
        ids_set.add(nuevo_id)
        isbns_set.add(dato['isbn'])
        count += 1
    print(f"Se cargaron {count} libros exitosamente.\n")

def main():
    cargar_datos_iniciales()
    
    while True:
        mostrar_menu()
        opcion = pedir_opcion()
        
        if opcion == -1:
            print("Error: Debe ingresar un número válido.")
            continue
        
        if opcion == 0:
            print("Saliendo del sistema... ¡Gracias por usar la Librería!")
            sys.exit(0)
        
        elif opcion == 1:
            listar_libros(libros_db)
        elif opcion == 2:
            agregar_libro(libros_db, ids_set, isbns_set)
        elif opcion == 3:
            buscar_libro(libros_db)
        elif opcion == 4:
            actualizar_stock(libros_db)
        elif opcion == 5:
            eliminar_libro(libros_db, ids_set, isbns_set)
        elif opcion == 6:
            generar_reporte(libros_db)
        else:
            print("Opción fuera de rango.")

if __name__ == "__main__":
    main()