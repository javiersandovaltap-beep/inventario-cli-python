# modulos/gestion_datos.py

from modulos.validaciones import validar_autor_chileno, mostrar_autores_validos
from modulos.funciones_utiles import generar_id_recursivo, validar_input_flotante, validar_input_numero
from modulos.persistencia import guardar_libros


def listar_libros(libros_db):
    """Muestra en consola el inventario completo con formato de tabla.

    Args:
        libros_db (list): Lista de diccionarios con los datos de los libros.
    """
    if not libros_db:
        print("\n>> No hay libros registrados en el sistema.")
        return

    print(f"\n{'='*72}")
    print(f"  {'#':<4} {'ISBN':<10} {'TÍTULO':<38} {'AUTOR':<20}")
    print(f"  {'':4} {'':10} {'PRECIO':>10}   {'STOCK':>6}")
    print(f"{'='*72}")

    for idx, libro in enumerate(libros_db, 1):
        titulo = libro['titulo'][:35] + "..." if len(libro['titulo']) > 35 else libro['titulo']
        autor = libro['autor'][:18] + ".." if len(libro['autor']) > 18 else libro['autor']
        print(f"  {idx:<4} {libro['isbn']:<10} {titulo:<38} {autor:<20}")
        print(f"  {'':4} {'':10} ${libro['precio']:>9,.0f}   {libro['stock']:>5} uds.")
        print(f"  {'-'*68}")

    print(f"  Total de títulos en catálogo: {len(libros_db)}\n")


def agregar_libro(libros_db, ids_set, isbns_set):
    """Agrega un nuevo libro al inventario con validaciones de negocio.

    Args:
        libros_db (list): Lista principal de libros.
        ids_set (set): Conjunto de IDs existentes.
        isbns_set (set): Conjunto de ISBNs existentes.
    """
    print("\n--- AGREGAR LIBRO ---")

    titulo = input("Título del libro: ").strip()
    if not titulo:
        print("Error: El título no puede estar vacío.")
        return

    autor = input("Autor: ").strip()
    if not validar_autor_chileno(autor):
        print(f"Error: '{autor}' no está en el catálogo de autores permitidos.")
        mostrar_autores_validos()
        return

    isbn = input("ISBN: ").strip()
    if not isbn:
        print("Error: El ISBN no puede estar vacío.")
        return
    if isbn in isbns_set:
        print("Error: El ISBN ya existe en el sistema.")
        return

    precio = validar_input_flotante("Precio (CLP): $", min_val=0.0)
    stock = validar_input_numero("Stock inicial: ", min_val=0)

    nuevo_id = generar_id_recursivo(ids_set)
    nuevo_libro = {
        'id': nuevo_id,
        'titulo': titulo,
        'autor': autor.title(),
        'isbn': isbn,
        'precio': precio,
        'stock': stock
    }

    libros_db.append(nuevo_libro)
    ids_set.add(nuevo_id)
    isbns_set.add(isbn)
    guardar_libros(libros_db)  # 💾 Guardado automático

    print(f"\n✔ Libro '{titulo}' agregado exitosamente con ID: {nuevo_id}")
    print("  💾 Datos guardados.")


def buscar_libro(libros_db):
    """Busca libros por ISBN exacto o por coincidencia parcial de título.

    Args:
        libros_db (list): Lista de diccionarios con los datos de los libros.
    """
    if not libros_db:
        print("\n>> No hay libros en el sistema para buscar.")
        return

    termino = input("\nIngrese ISBN o título a buscar: ").strip().lower()
    if not termino:
        print("Error: Ingrese un término de búsqueda.")
        return

    encontrados = [
        libro for libro in libros_db
        if termino == libro['isbn'].lower() or termino in libro['titulo'].lower()
    ]

    if encontrados:
        print(f"\n>> Se encontraron {len(encontrados)} resultado(s):")
        for libro in encontrados:
            print(f"  • [{libro['isbn']}] {libro['titulo']}")
            print(f"    Autor: {libro['autor']} | Stock: {libro['stock']} | Precio: ${libro['precio']:,.0f}")
    else:
        print(f">> Sin resultados para '{termino}'.")


def actualizar_stock(libros_db):
    """Registra una entrada o venta de stock para un libro por ISBN.

    Args:
        libros_db (list): Lista de diccionarios con los datos de los libros.
    """
    if not libros_db:
        print("\n>> No hay libros en el sistema.")
        return

    isbn = input("Ingrese ISBN del libro: ").strip().lower()
    for libro in libros_db:
        if libro['isbn'].lower() == isbn:
            print(f"\n  Libro : {libro['titulo']}")
            print(f"  Stock actual: {libro['stock']} unidades")
            tipo = input("  Movimiento — [E]ntrada o [V]enta: ").strip().upper()

            if tipo not in ['E', 'V']:
                print("Error: Ingrese 'E' para entrada o 'V' para venta.")
                return

            cantidad = validar_input_numero("  Cantidad: ", min_val=1)

            if tipo == 'V':
                if cantidad > libro['stock']:
                    print(f"Error: Stock insuficiente. Disponible: {libro['stock']} unidades.")
                    return
                libro['stock'] -= cantidad
                print(f"✔ Venta registrada. Nuevo stock: {libro['stock']} unidades.")
            else:
                libro['stock'] += cantidad
                print(f"✔ Entrada registrada. Nuevo stock: {libro['stock']} unidades.")

            guardar_libros(libros_db)  # 💾 Guardado automático
            print("  💾 Datos guardados.")
            return

    print(f"Error: ISBN '{isbn.upper()}' no encontrado en el sistema.")


def eliminar_libro(libros_db, ids_set, isbns_set):
    """Elimina un libro del inventario previa confirmación del usuario.

    Args:
        libros_db (list): Lista principal de libros.
        ids_set (set): Conjunto de IDs para mantener consistencia.
        isbns_set (set): Conjunto de ISBNs para mantener consistencia.
    """
    isbn = input("Ingrese ISBN del libro a eliminar: ").strip().lower()
    for i, libro in enumerate(libros_db):
        if libro['isbn'].lower() == isbn:
            print(f"\n  Libro a eliminar: '{libro['titulo']}' — {libro['autor']}")
            confirmacion = input("  ¿Confirma la eliminación? (s/n): ").strip().lower()

            if confirmacion == 's':
                ids_set.discard(libro['id'])
                isbns_set.discard(libro['isbn'])
                libros_db.pop(i)
                guardar_libros(libros_db)  # 💾 Guardado automático
                print("✔ Libro eliminado correctamente.")
                print("  💾 Datos guardados.")
            else:
                print("Operación cancelada.")
            return

    print(f"Error: ISBN '{isbn.upper()}' no encontrado en el sistema.")


def generar_reporte(libros_db):
    """Genera y muestra un reporte estadístico del inventario actual.

    Args:
        libros_db (list): Lista de diccionarios con los datos de los libros.
    """
    if not libros_db:
        print("\n>> Sin datos para generar reporte.")
        return

    total_titulos = len(libros_db)
    total_unidades = sum(l['stock'] for l in libros_db)
    valor_inventario = sum(l['precio'] * l['stock'] for l in libros_db)
    stock_bajo = [l for l in libros_db if l['stock'] < 5]
    autor_mas_titulos = max(
        set(l['autor'] for l in libros_db),
        key=lambda a: sum(1 for l in libros_db if l['autor'] == a)
    )

    print("\n" + "=" * 45)
    print("       REPORTE DE INVENTARIO")
    print("=" * 45)
    print(f"  Títulos en catálogo  : {total_titulos}")
    print(f"  Unidades totales     : {total_unidades}")
    print(f"  Valor del inventario : ${valor_inventario:>12,.0f}")
    print(f"  Autor con más títulos: {autor_mas_titulos}")
    print(f"  Títulos bajo stock   : {len(stock_bajo)} (menos de 5 uds.)")

    if stock_bajo:
        print("\n  ⚠ Títulos con stock crítico:")
        for l in stock_bajo:
            print(f"    - [{l['isbn']}] {l['titulo']} → {l['stock']} uds.")
    print("=" * 45)
