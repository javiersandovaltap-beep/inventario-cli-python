# modulos/validaciones.py
AUTORES_CHILENOS = (
    'Pablo Neruda', 'Isabel Allende', 'Luis Sepúlveda', 'Antonio Skármeta',
    'Ariel Dorfman', 'Diamela Eltit', 'Roberto Bolaño', 'Marcela Serrano',
    'José Donoso', 'Francisco Coloane', 'Mariano Latorre', 'Vicente Huidobro',
    'Juan Emar', 'Volodia Teitelboim', 'María Luisa Bombal', 'Jorge Edwards',
    'Manuel Rojas'
)

def validar_autor_chileno(autor):
    return autor.title() in AUTORES_CHILENOS