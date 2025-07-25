#Automatización SGD
El presente es una prueba de script para automatizar la lectura del index.html, descargar sus archivos y tratar de indexar datos a inventario establecido en excel. 

-Uso del scraping_enviados.py
Se utilizará para 
    Pasos a seguir:

Paso 1: 🔹 Importación de librerías necesarias:
    (BeautifulSoup): para analizar y manipular HTML.
    (pandas): para trabajar con los datos como tablas (DataFrame).
    (os): para manejar rutas y archivos.
    (shutil): para copiar archivos (en este caso, simula la descarga).
Paso 2: 📄 Define la ruta absoluta del archivo enviados.html que contiene la tabla con los documentos.
Paso 3: 📁 Construye la ruta donde están los archivos enlazados:
    (os.path.dirname(ruta)): toma la carpeta del HTML.
    (..): sube un nivel.
    ("documentos"): va a la carpeta donde están los archivos reales.
    (os.path.abspath): convierte todo en una ruta absoluta.
Paso 4: 📥 Crea una carpeta llamada Documentos_Descargados al mismo nivel del HTML para guardar copias de los archivos.
    (exist_ok=True): evita error si ya existe.
Paso 5: 🧪 Abre y analiza el HTML para poder trabajar con su contenido. soup es el objeto que representa el HTML.
Paso 6: 🔍 Busca la tabla dentro del HTML cuyo id es tbl_documentos.
Paso 7: 📋 Prepara una lista para guardar los datos que se extraen de la tabla.
Paso 8: 🔁 Recorre cada fila de la tabla (<tr>) dentro del cuerpo de la tabla (<tbody>).
Paso 9: 📏 Extrae las celdas de la fila. Si hay menos de 7 columnas, la fila se omite (para evitar errores).
Paso 10: 📎 Si hay un <a> (hipervínculo) en la primera celda, extrae el href (enlace) y lo limpia con .strip().
Paso 11: 📝 Extrae el texto de cada celda:
    (fecha): también está en la primera columna.
    (no_doc): número del documento.
    (remitente, destinatario, asunto, etc).
Paso 12: 📦 Guarda los datos extraídos en un diccionario y lo añade a la lista documentos.
Paso 13:🔁 Recorre cada documento recopilado para proceder a la copia del archivo correspondiente.
Paso 14: 🗂️ Obtiene el enlace del documento y su número para usar como nombre del archivo destino.
Paso 15: 📍 Genera la ruta del archivo fuente basándose en el nombre del archivo del enlace (basename(enlace)).
Paso 16: ✅ Verifica si el archivo existe. Si no, muestra una advertencia y pasa al siguiente.
Paso 17: 📦 Obtiene la extensión del archivo original y construye la ruta de destino usando el Nro Documento.
Paso 18: 📤 Copia el archivo a la carpeta de salida, manteniendo metadatos (copy2). Luego informa la acción.
Paso 19: 📊 Convierte la lista de documentos en un DataFrame para facilitar su manipulación o exportación.
Paso 20: 📂 Abre cada HTML referenciado por los enlaces para extraer más datos internos si fuera necesario (esto es extensible según el caso).
Paso 21: 🧾 Muestra las primeras filas del DataFrame por consola y guarda todo como un archivo CSV llamado documentos_extraidos.csv.


-Uso del scraping_Recibidos.py
