Sistema de Gestión de Librería - Autores Chilenos
Sistema de gestión de datos desarrollado en Python,segun los requerimientos de la segunda version del ABP del modulo 3. El sistema permite gestionar el inventario de una librería especializada en autores chilenos, aplicando estructuras de control, funciones y módulos.

Descripción del Sistema
Este software permite la administración eficiente de un catálogo de libros, ofreciendo funcionalidades para listar, buscar, agregar, modificar y eliminar registros. Además, incluye un módulo de reportes estadísticos y validaciones de negocio restrictivas (autores permitidos).

El desarrollo se centra en la modularización, priorizando un código limpio, legible y eficiente.

Estructuras de Datos Utilizadas
El proyecto implementa las estructuras fundamentales de Python para la manipulación de información:

Listas (list): Utilizada como base de datos principal (libros_db) para almacenar colecciones mutables de libros.
Diccionarios (dict): Empleado para representar cada entidad de "Libro", mapeando claves como id, titulo, autor, isbn, precio y stock a sus valores correspondientes.
Tuplas (tuple):
Para almacenar los datos iniciales precargados (DATOS_INICIALES), asegurando inmutabilidad.
Para la lista de validación de autores chilenos (AUTORES_CHILENOS).
Conjuntos (set): Utilizados para garantizar la unicidad de identificadores (ids_set) y códigos ISBN (isbns_set), evitando duplicados en el sistema.
Funcionalidades Implementadas
El sistema ofrece un menú interactivo con las siguientes opciones:

Listar libros: Muestra en pantalla el inventario actual con formato tabular y moneda.
Agregar libro: Permite ingresar nuevos libros validando que el autor sea chileno y que el ISBN sea único. Utiliza recursividad para la generación automática de IDs.
Buscar libro: Filtra el inventario por título o ISBN de forma insensible a mayúsculas/minúsculas.
Actualizar stock: Gestiona entradas y salidas de mercancía, validando stock disponible antes de registrar una venta.
Eliminar libro: Permite borrar registros del sistema con confirmación de usuario.
Generar reporte: Calcula y muestra estadísticas en tiempo real (valor total del inventario, títulos con bajo stock).
Requisitos y Ejecución
Este proyecto fue desarrollado con Python 3.14.

Clonar o descargar el repositorio.
Asegurarse de tener la siguiente estructura de carpetas:
/LibreriaAutoresChilenos    ├── main.py    └── modulos/        ├── __init__.py        ├── datos_basicos.py        ├── menu.py        ├── validaciones.py        ├── funciones_utiles.py        └── gestion_datos.py
Ejecutar el archivo principal desde la terminal:
python main.py
Tecnologías Utilizadas
Lenguaje: Python 3.
IDE sugerido: Visual Studio Code.
Estándar: PEP 8 (Style Guide for Python Code).
Librerías: Solo librerías estándar (sys).
Autor
Javier Sandoval Tapia 
