# modulos/persistencia.py

import json
import os

RUTA_DATOS = os.path.join(os.path.dirname(__file__), '..', 'data', 'libros.json')


def _asegurar_carpeta():
    """Crea la carpeta data/ si no existe."""
    carpeta = os.path.dirname(RUTA_DATOS)
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


def guardar_libros(libros_db):
    """Serializa y guarda la lista de libros en libros.json.

    Args:
        libros_db (list): Lista de diccionarios con los datos de los libros.
    """
    _asegurar_carpeta()
    with open(RUTA_DATOS, 'w', encoding='utf-8') as f:
        json.dump(libros_db, f, ensure_ascii=False, indent=2)


def cargar_libros():
    """Carga la lista de libros desde libros.json si el archivo existe.

    Returns:
        list | None: Lista de libros guardados, o None si no existe el archivo.
    """
    if not os.path.exists(RUTA_DATOS):
        return None
    with open(RUTA_DATOS, 'r', encoding='utf-8') as f:
        return json.load(f)


def existe_archivo():
    """Verifica si el archivo de datos persistentes ya existe.

    Returns:
        bool: True si libros.json existe, False en caso contrario.
    """
    return os.path.exists(RUTA_DATOS)
