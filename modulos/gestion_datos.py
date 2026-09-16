"""CRUD operations on Inventario instances, preserving CLI interaction."""

from modulos.funciones_utiles import generar_id, validar_input_flotante, validar_input_numero
from modulos.inventario import Inventario
from modulos.item import Item


def listar_libros(inventario: Inventario) -> None:
    """Display the complete inventory in a table format.

    Args:
        inventario: The Inventario instance to list items from.

    """
    items = inventario.listar()
    if not items:
        print("\n>> No hay libros registrados en el sistema.")
        return

    print(f"\n{'=' * 72}")
    print(f"  {'#':<4} {'SKU':<10} {'TÍTULO':<38} {'AUTOR':<20}")
    print(f"  {'':4} {'':10} {'PRECIO':>10}   {'STOCK':>6}")
    print(f"{'=' * 72}")

    for idx, item in enumerate(items, 1):
        titulo = item.nombre[:35] + "..." if len(item.nombre) > 35 else item.nombre
        autor = item.atributos.get("autor", "")
        autor = autor[:18] + ".." if len(autor) > 18 else autor
        print(f"  {idx:<4} {item.sku:<10} {titulo:<38} {autor:<20}")
        print(f"  {'':4} {'':10} ${item.precio:>9,.0f}   {item.stock:>5} uds.")
        print(f"  {'-' * 68}")

    print(f"  Total de títulos en catálogo: {len(items)}\n")


def agregar_libro(inventario: Inventario) -> None:
    """Prompt the user for data and add a new book to the inventory.

    Args:
        inventario: The Inventario instance to add the new book to.

    """
    print("\n--- AGREGAR LIBRO ---")

    titulo = input("Título del libro: ").strip()
    if not titulo:
        print("Error: El título no puede estar vacío.")
        return

    autor = input("Autor: ").strip()

    isbn = input("ISBN: ").strip()
    if not isbn:
        print("Error: El ISBN no puede estar vacío.")
        return

    precio = validar_input_flotante("Precio (CLP): $", min_val=0.0)
    stock = validar_input_numero("Stock inicial: ", min_val=0)

    nuevo_id = generar_id(inventario._ids)
    nuevo_item = Item(
        id=nuevo_id,
        sku=isbn,
        nombre=titulo,
        precio=precio,
        stock=stock,
        atributos={"autor": autor.title()},
    )

    if inventario.agregar(nuevo_item):
        inventario.guardar()
        print(f"\n✔ Libro '{titulo}' agregado exitosamente con ID: {nuevo_id}")
        print("  💾 Datos guardados.")
    else:
        print("Error: No se pudo agregar el libro (SKU duplicado o autor no válido).")


def buscar_libro(inventario: Inventario) -> None:
    """Search for books by exact SKU or partial title match.

    Args:
        inventario: The Inventario instance to search in.

    """
    if not inventario.listar():
        print("\n>> No hay libros en el sistema para buscar.")
        return

    termino = input("\nIngrese ISBN o título a buscar: ").strip().lower()
    if not termino:
        print("Error: Ingrese un término de búsqueda.")
        return

    resultados = inventario.buscar(termino)
    if resultados:
        print(f"\n>> Se encontraron {len(resultados)} resultado(s):")
        for item in resultados:
            print(f"  • [{item.sku}] {item.nombre}")
            autor = item.atributos.get("autor", "Desconocido")
            print(f"    Autor: {autor} | Stock: {item.stock} | Precio: ${item.precio:,.0f}")
    else:
        print(f">> Sin resultados para '{termino}'.")


def actualizar_stock(inventario: Inventario) -> None:
    """Register a stock entry or sale for a book identified by SKU.

    Args:
        inventario: The Inventario instance to update.

    """
    if not inventario.listar():
        print("\n>> No hay libros en el sistema.")
        return

    sku = input("Ingrese ISBN del libro: ").strip().lower()
    resultados = inventario.buscar(sku)
    exactos = [item for item in resultados if item.sku.casefold() == sku.casefold()]
    if not exactos:
        print(f"Error: ISBN '{sku.upper()}' no encontrado en el sistema.")
        return
    item = exactos[0]

    print(f"\n  Libro : {item.nombre}")
    print(f"  Stock actual: {item.stock} unidades")
    tipo = input("  Movimiento — [E]ntrada o [V]enta: ").strip().upper()

    if tipo not in ["E", "V"]:
        print("Error: Ingrese 'E' para entrada o 'V' para venta.")
        return

    cantidad = validar_input_numero("  Cantidad: ", min_val=1)

    if tipo == "V" and cantidad > item.stock:
        print(f"Error: Stock insuficiente. Disponible: {item.stock} unidades.")
        return

    es_venta = tipo == "V"
    if inventario.actualizar_stock(item.sku, cantidad, es_venta=es_venta):
        if es_venta:
            print(f"✔ Venta registrada. Nuevo stock: {item.stock} unidades.")
        else:
            print(f"✔ Entrada registrada. Nuevo stock: {item.stock} unidades.")
        inventario.guardar()
        print("  💾 Datos guardados.")
    else:
        print("Error: No se pudo actualizar el stock.")


def eliminar_libro(inventario: Inventario) -> None:
    """Remove a book from the inventory after user confirmation.

    Args:
        inventario: The Inventario instance to remove the book from.

    """
    if not inventario.listar():
        print("\n>> No hay libros en el sistema.")
        return

    sku = input("Ingrese ISBN del libro a eliminar: ").strip().lower()
    resultados = inventario.buscar(sku)
    exactos = [item for item in resultados if item.sku.casefold() == sku.casefold()]
    if not exactos:
        print(f"Error: ISBN '{sku.upper()}' no encontrado en el sistema.")
        return
    item = exactos[0]

    autor = item.atributos.get("autor", "Desconocido")
    print(f"\n  Libro a eliminar: '{item.nombre}' — {autor}")
    confirmacion = input("  ¿Confirma la eliminación? (s/n): ").strip().lower()

    if confirmacion == "s":
        if inventario.eliminar(item.sku):
            inventario.guardar()
            print("✔ Libro eliminado correctamente.")
            print("  💾 Datos guardados.")
        else:
            print("Error: No se pudo eliminar el libro.")
    else:
        print("Operación cancelada.")


def generar_reporte(inventario: Inventario) -> None:
    """Generate and display a statistical report of the inventory.

    Args:
        inventario: The Inventario instance to report on.

    """
    reporte = inventario.generar_reporte()
    if reporte["total_items"] == 0:
        print("\n>> Sin datos para generar reporte.")
        return

    print("\n" + "=" * 45)
    print("       REPORTE DE INVENTARIO")
    print("=" * 45)
    print(f"  Títulos en catálogo  : {reporte['total_items']}")
    print(f"  Unidades totales     : {reporte['total_unidades']}")
    print(f"  Valor del inventario : ${reporte['valor_inventario']:>12,.0f}")
    top_autor = reporte["top_autor"] or "N/A"
    print(f"  Autor con más títulos: {top_autor}")
    print(f"  Títulos bajo stock   : {len(reporte['stock_bajo'])} (menos de 5 uds.)")

    if reporte["stock_bajo"]:
        print("\n  ⚠ Títulos con stock crítico:")
        for item in reporte["stock_bajo"]:
            print(f"    - [{item.sku}] {item.nombre} → {item.stock} uds.")
    print("=" * 45)
