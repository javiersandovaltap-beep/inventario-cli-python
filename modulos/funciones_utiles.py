# modulos/funciones_utiles.py

def validar_input_numero(prompt, min_val=None, max_val=None):
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

def validar_input_flotante(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Error: Ingrese un valor numérico válido (ej. 15000.50).")

def generar_id_recursivo(ids_set, current_id=1):
    if current_id in ids_set:
        return generar_id_recursivo(ids_set, current_id + 1)
    return current_id