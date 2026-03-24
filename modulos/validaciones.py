# modulos/validaciones.py

AUTORES_CHILENOS = (
    'Pablo Neruda', 'Isabel Allende', 'Luis Sepúlveda', 'Antonio Skármeta',
    'Ariel Dorfman', 'Diamela Eltit', 'Roberto Bolaño', 'Marcela Serrano',
    'José Donoso', 'Francisco Coloane', 'Mariano Latorre', 'Vicente Huidobro',
    'Juan Emar', 'Volodia Teitelboim', 'María Luisa Bombal', 'Jorge Edwards',
    'Manuel Rojas'
)


def validar_autor_chileno(autor):
    """Verifica si el autor pertenece al catálogo de autores chilenos permitidos.

    Args:
        autor (str): Nombre del autor a validar.

    Returns:
        bool: True si el autor está en el catálogo, False en caso contrario.
    """
    return autor.title() in AUTORES_CHILENOS


def mostrar_autores_validos():
    """Imprime en consola la lista de autores chilenos permitidos en el sistema."""
    print("\n  Autores chilenos disponibles en el catálogo:")
    for i, autor in enumerate(sorted(AUTORES_CHILENOS), 1):
        print(f"    {i:>2}. {autor}")
