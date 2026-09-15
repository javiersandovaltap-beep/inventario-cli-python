"""modulos package -- inventory CLI business modules."""

from modulos.funciones_utiles import generar_id_recursivo
from modulos.gestion_datos import (
    actualizar_stock,
    agregar_libro,
    buscar_libro,
    eliminar_libro,
    generar_reporte,
    listar_libros,
)

__all__ = [
    "actualizar_stock",
    "agregar_libro",
    "buscar_libro",
    "eliminar_libro",
    "generar_id_recursivo",
    "generar_reporte",
    "listar_libros",
]
