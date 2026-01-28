# modulos/gestion_datos.py
from modulos.validaciones import validar_autor_chileno
from modulos.funciones_utiles import generar_id_recursivo, validar_input_flotante

def listar_libros(libros_db):
    if not libros_db:
        print("\n>> No hay libros registrados.")
        return
    
    print("\n=== LISTADO DE LIBROS ===")
    for idx, libro in enumerate(libros_db, 1):
        print(f"{idx}. ISBN: {libro['isbn']} | {libro['titulo']}")
        print(f"   Autor: {libro['autor']} | Stock: {libro['stock']}")
        print(f"   Precio: ${libro['precio']:,.0f}")
        print("-" * 40)

def agregar_libro(libros_db, ids_set, isbns_set):
    print("\n--- AGREGAR LIBRO ---")
    
    titulo = input("Título del libro: ").strip()
    if not titulo:
        print("Error: El título no puede estar vacío.")
        return

    autor = input("Autor: ").strip()
    if not validar_autor_chileno(autor):
        print("Error: El autor no está en la base de autores chilenos permitidos.")
        return

    isbn = input("ISBN: ").strip()
    if isbn in isbns_set:
        print("Error: El ISBN ya existe en el sistema.")
        return
    
    precio = validar_input_flotante("Precio: ")
    stock = validar_input_flotante("Stock inicial: ")
    
    if precio < 0 or stock < 0:
        print("Error: Valores negativos no permitidos.")
        return

    nuevo_id = generar_id_recursivo(ids_set)
    
    nuevo_libro = {
        'id': nuevo_id,
        'titulo': titulo,
        'autor': autor.title(),
        'isbn': isbn,
        'precio': precio,
        'stock': int(stock)
    }
    
    libros_db.append(nuevo_libro)
    ids_set.add(nuevo_id)
    isbns_set.add(isbn)
    
    print(f"Libro agregado exitosamente con ID: {nuevo_id}")

def buscar_libro(libros_db):
    termino = input("\nIngrese ISBN o Título a buscar: ").strip().lower()
    encontrados = []
    
    for libro in libros_db:
        if termino == libro['isbn'].lower() or termino in libro['titulo'].lower():
            encontrados.append(libro)
            
    if encontrados:
        print(f"\n>> Se encontraron {len(encontrados)} coincidencias:")
        for libro in encontrados:
            print(f" - {libro['titulo']} ({libro['autor']}) | Stock: {libro['stock']}")
    else:
        print(">> No se encontraron resultados.")

def actualizar_stock(libros_db):
    isbn = input("Ingrese ISBN del libro a modificar stock: ").strip()
    for libro in libros_db:
        if libro['isbn'] == isbn:
            print(f"Libro encontrado: {libro['titulo']} (Stock actual: {libro['stock']})")
            tipo = input("Tipo de movimiento [E]ntrada o [V]enta: ").upper()
            
            if tipo not in ['E', 'V']:
                print("Opción inválida.")
                return
            
            cantidad = validar_input_flotante("Cantidad: ")
            
            if tipo == 'V':
                if cantidad > libro['stock']:
                    print("Error: Stock insuficiente para la venta.")
                    return
                libro['stock'] -= int(cantidad)
                print(f"Venta realizada. Nuevo stock: {libro['stock']}")
            else:
                libro['stock'] += int(cantidad)
                print(f"Entrada realizada. Nuevo stock: {libro['stock']}")
            return
            
    print("Error: ISBN no encontrado.")

def eliminar_libro(libros_db, ids_set, isbns_set):
    isbn = input("Ingrese ISBN del libro a eliminar: ").strip()
    for i, libro in enumerate(libros_db):
        if libro['isbn'] == isbn:
            print(f"¿Está seguro de eliminar '{libro['titulo']}'? (s/n): ", end="")
            confirmacion = input().lower()
            
            if confirmacion == 's':
                ids_set.discard(libro['id'])
                isbns_set.discard(libro['isbn'])
                libros_db.pop(i)
                print("Libro eliminado correctamente.")
            else:
                print("Operación cancelada.")
            return
    print("Error: ISBN no encontrado.")

def generar_reporte(libros_db):
    if not libros_db:
        print("Sin datos para reporte.")
        return
        
    total_libros = len(libros_db)
    valor_inventario = sum(l['precio'] * l['stock'] for l in libros_db)
    stock_bajo = [l for l in libros_db if l['stock'] < 5]
    
    print("\n=== REPORTE DE INVENTARIO ===")
    print(f"Total de títulos: {total_libros}")
    print(f"Valor total inventario: ${valor_inventario:,.0f}")
    print(f"Títulos con bajo stock (<5): {len(stock_bajo)}")
    if stock_bajo:
        for l in stock_bajo:
            print(f"  - {l['titulo']} (Stock: {l['stock']})")