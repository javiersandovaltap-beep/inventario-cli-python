# modulos/funciones_utiles.py


def validar_input_numero(prompt, min_val=None, max_val=None):
    """Solicita un número entero al usuario con validación de rango.

    Args:
        prompt (str): Mensaje a mostrar al usuario.
        min_val (int, optional): Valor mínimo permitido.
        max_val (int, optional): Valor máximo permitido.

    Returns:
        int: Número entero válido dentro del rango especificado.

    """
    while True:
        try:
            valor = int(input(prompt))
            if min_val is not None and valor < min_val:
                print(f"Error: El valor debe ser mayor o igual a {min_val}.")
                continue
            if max_val is not None and valor > max_val:
                print(f"Error: El valor debe ser menor o igual a {max_val}.")
                continue
            return valor
        except ValueError:
            print("Error: Por favor ingrese un número entero válido.")


def validar_input_flotante(prompt, min_val=0.0):
    """Solicita un número decimal al usuario con validación de mínimo.

    Args:
        prompt (str): Mensaje a mostrar al usuario.
        min_val (float): Valor mínimo permitido. Por defecto 0.0.

    Returns:
        float: Número decimal válido mayor o igual al mínimo.

    """
    while True:
        try:
            valor = float(input(prompt))
            if valor < min_val:
                print(f"Error: El valor debe ser mayor o igual a {min_val}.")
                continue
            return valor
        except ValueError:
            print("Error: Ingrese un valor numérico válido (ej. 15000.50).")


def generar_id(ids_en_uso: set[int]) -> int:
    """Genera un ID unico iterativamente que no exista en el conjunto dado.

    Resuelve L-04: la version anterior recursiva no era de cola y causaba
    stack overflow en IDs grandes. Implementacion iterativa con while
    loop, O(n) worst case donde n es el tamano del conjunto.

    Args:
        ids_en_uso: Conjunto de IDs ya utilizados.

    Returns:
        Primer ID entero positivo (>=1) no presente en ids_en_uso.

    """
    candidato = 1
    while candidato in ids_en_uso:
        candidato += 1
    return candidato
