# 📚 Librería Autores Chilenos

Sistema de gestión de inventario desarrollado en **Python puro**, sin frameworks ni librerías externas. Permite administrar el catálogo de una librería especializada en literatura chilena, con persistencia de datos en JSON y una interfaz de consola interactiva.

---

## 🖥️ Demo

```
========================================
    LIBRERÍA AUTORES CHILENOS 📚
========================================
  1. Listar libros
  2. Agregar libro
  3. Buscar libro
  4. Actualizar stock
  5. Eliminar libro
  6. Generar reporte
  0. Salir
----------------------------------------

       REPORTE DE INVENTARIO
=============================================
  Títulos en catálogo  : 30
  Unidades totales     : 218
  Valor del inventario : $  4.345.000
  Autor con más títulos: Pablo Neruda
  Títulos bajo stock   : 4 (menos de 5 uds.)
=============================================
```

---

## ✨ Funcionalidades

- **Listar libros** — tabla formateada con ISBN, título, autor, precio y stock
- **Agregar libro** — validación de autor chileno, ISBN único y campos obligatorios
- **Buscar libro** — por ISBN exacto o coincidencia parcial de título
- **Actualizar stock** — registra entradas y ventas con validación de stock disponible
- **Eliminar libro** — con confirmación previa del usuario
- **Generar reporte** — estadísticas en tiempo real: valor total, stock crítico y autor destacado
- **Persistencia JSON** — los datos se guardan automáticamente en `data/libros.json` tras cada operación

---

## 🏗️ Estructura del Proyecto

```
LibreriaAutoresChilenos/
├── main.py                  # Punto de entrada y bucle principal
├── README.md
├── .gitignore
├── data/
│   └── libros.json          # Generado automáticamente en la primera ejecución
└── modulos/
    ├── __init__.py
    ├── datos_basicos.py     # 30 libros precargados (tupla inmutable)
    ├── menu.py              # Presentación y captura del menú
    ├── validaciones.py      # Catálogo de autores chilenos y validaciones
    ├── funciones_utiles.py  # Inputs validados y generador recursivo de IDs
    ├── gestion_datos.py     # Lógica CRUD completa
    └── persistencia.py      # Lectura y escritura en JSON
```

---

## 🧠 Conceptos Aplicados

| Concepto | Implementación |
|---|---|
| Modularización | 6 módulos con responsabilidad única |
| Estructuras de datos | `list`, `dict`, `tuple`, `set` |
| Funciones recursivas | `generar_id_recursivo()` en `funciones_utiles.py` |
| Persistencia | Serialización/deserialización JSON con módulo `json` |
| Validaciones | Autor chileno, ISBN único, rangos numéricos |
| PEP 8 | Nombres, espaciado, longitud de línea |
| Docstrings | Todas las funciones documentadas con Args y Returns |

---

## ▶️ Instalación y Ejecución

**Requisitos:** Python 3.8 o superior. No requiere dependencias externas.

```bash
# 1. Clonar el repositorio
git clone https://github.com/javiersandovaltap-beep/libreria-autores-chilenos-python.git

# 2. Entrar a la carpeta
cd libreria-autores-chilenos-python

# 3. Ejecutar
python main.py
```

En la **primera ejecución** se crea automáticamente `data/libros.json` con 30 libros precargados. A partir de la segunda ejecución, el sistema carga el estado guardado.

---

## 👤 Autor

**Javier Sandoval Tapia**  
[GitHub](https://github.com/javiersandovaltap-beep)

