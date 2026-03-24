# modulos/__init__.py
from .gestion_datos import (
    listar_libros, agregar_libro, buscar_libro,
    actualizar_stock, eliminar_libro, generar_reporte
)
from .validaciones import validar_autor_chileno, AUTORES_CHILENOS
from .funciones_utiles import generar_id_recursivo
