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

def mostrar_menu():
    """Imprime el menú principal de la aplicación en consola."""
    print("\n" + "=" * 40)
    print("    LIBRERÍA AUTORES CHILENOS 📚")
    print("=" * 40)
    print("  1. Listar libros")
    print("  2. Agregar libro")
    print("  3. Buscar libro")
    print("  4. Actualizar stock")
    print("  5. Eliminar libro")
    print("  6. Generar reporte")
    print("  0. Salir")
    print("-" * 40)


def pedir_opcion():
    """Solicita y valida una opción del menú entre 0 y 6.
    
    Returns:
        int: Opción válida entre 0 y 6, o -1 si la entrada no es numérica.
    """
    opcion_str = input("Seleccione una opción (0-6): ").strip()
    try:
        opcion = int(opcion_str)
        if opcion < 0 or opcion > 6:
            print("Error: Opción fuera de rango. Ingrese un número entre 0 y 6.")
            return -1
        return opcion
    except ValueError:
        return -1

    print("-" * 30)

def pedir_opcion():
    opcion_str = input("Seleccione una opción: ").strip()
    try:
        return int(opcion_str)
    except ValueError:
        return -1
 
