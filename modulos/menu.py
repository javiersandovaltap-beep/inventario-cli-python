# modulos/menu.py

def mostrar_menu():
    print("\n" + "=" * 30)
    print("  LIBRERÍA AUTORES CHILENOS")
    print("=" * 30)
    print("1. Listar libros")
    print("2. Agregar libro")
    print("3. Buscar libro")
    print("4. Actualizar stock")
    print("5. Eliminar libro")
    print("6. Generar reporte")
    print("0. Salir")
    print("-" * 30)

def pedir_opcion():
    opcion_str = input("Seleccione una opción: ").strip()
    try:
        return int(opcion_str)
    except ValueError:
        return -1
 
