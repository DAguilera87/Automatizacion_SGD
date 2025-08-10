####Instrucciones para proyecto portable entre diferentes equipos####
# Dependencias para el script de extracción de documentos SGD
# Generado para Python 3.8+

##############################################
# Crear el entorno virtual
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
##############################################


# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate

# En Mac/Linux:
source .venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar que todo esté instalado
pip list

###Librerías###
beautifulsoup4==4.13.4
xlsxwriter==3.2.5
pandas==2.3.1
openpyxl==3.1.2
colorama==0.4.6
numpy==2.2.6
pytz==2025.2
six==1.17.0
soupsieve==2.7
typing_extensions==4.14.1
tzdata==2025.2

# Barra de progreso
tqdm==4.67.1

# Utilidades del sistema (incluidas en Python estándar)
# os - incluido en Python
# shutil - incluido en Python  
# re - incluido en Python
# pathlib - incluido en Python
# datetime - incluido en Python

#Estructura recomendada de tu proyecto:
tu_proyecto/
├── .venv/
├── requirements.txt
├── main.py (tu script)
└── README.md (opcional)
#################################
1. 📁 Verifica que tienes el archivo .gitignore
En la raíz de tu proyecto, verifica si ya existe un archivo llamado .gitignore.

✅ Si ya existe:
Ve al siguiente paso.

❌ Si no existe:
Créalo con este comando (o manualmente):

bash
Copiar
Editar
echo .venv/ > .gitignore
O si prefieres hacerlo a mano:

Crea un archivo nuevo llamado .gitignore (sin extensión)

Abrelo con cualquier editor de texto (como Notepad o VSCode)

2. 📝 Abre .gitignore y agrega la línea:
bash
Copiar
Editar
.venv/
Esto le dice a Git que ignore toda la carpeta del entorno virtual .venv.

⚠️ Asegúrate de que no haya espacios al comienzo de la línea y que sea una línea por sí sola.

3. 💾 Guarda y cierra el archivo
4. 🧹 (Opcional) Si .venv ya estaba siendo rastreado por Git:
Si creaste el entorno virtual antes de ignorarlo, Git ya lo tiene en el índice, y seguirá queriendo subirlo a GitHub. Para solucionarlo:

bash
Copiar
Editar
git rm -r --cached .venv
Este comando elimina .venv solo del control de versiones (no del disco), permitiendo que ya no se suba a GitHub.

5. 📦 Confirma los cambios en Git
bash
Copiar
Editar
git add .gitignore
git commit -m "Agrego .venv al .gitignore para excluir entorno virtual"
Y luego:

bash
Copiar
Editar
git push
#################################
📁 Automatización SGD
Este repositorio contiene un conjunto de scripts diseñados para automatizar la lectura del archivo index.html, descargar los documentos enlazados y extraer metadatos estructurados hacia un archivo de inventario en formato .csv compatible con Excel.

Actualmente se encuentra en fase de prueba.

🔧 Scripts disponibles
scraping_enviados.py
Script principal para procesar el archivo enviados.html, copiar los documentos enlazados y extraer metadatos hacia una tabla estructurada.

Pasos del proceso:
1. 📚 Importación de librerías necesarias
BeautifulSoup: análisis y manipulación del HTML.

pandas: manejo de datos tabulares.

os: manejo de rutas y archivos.

shutil: copiado de archivos (simula descarga).

2. 📄 Ruta del archivo HTML
Define la ruta absoluta del archivo enviados.html, que contiene la tabla de documentos.

3. 🗂 Construcción de ruta hacia los archivos enlazados
Se calcula en base a la ubicación del HTML:

os.path.dirname(ruta) sube un nivel.

"documentos" accede a la carpeta de los archivos.

os.path.abspath() genera la ruta absoluta final.

4. 📥 Creación de carpeta Documentos_Descargados
Se crea automáticamente junto al HTML para almacenar copias de los documentos.
exist_ok=True evita errores si ya existe.

5. 🔍 Análisis del HTML
Se abre y analiza el contenido con BeautifulSoup, generando el objeto soup.

6. 🔎 Búsqueda de la tabla id="tbl_documentos"
Se localiza la tabla que contiene los datos documentales.

7. 🧾 Preparación de estructura
Se inicializa una lista vacía para guardar los registros extraídos.

8. 🔁 Iteración sobre filas (<tr>)
Se recorren las filas del <tbody> de la tabla.

9. ⚠️ Validación de columnas
Se omiten las filas con menos de 7 celdas para evitar errores.

10. 🔗 Extracción del enlace
Se obtiene el href del primer <a> (si existe), y se limpia con .strip().

11. 📝 Extracción de datos
Se capturan los siguientes campos:

fecha (también desde la primera celda),

número de documento,

remitente,

destinatario,

asunto, etc.

12. 📦 Almacenamiento del registro
Los datos se estructuran en un diccionario que se añade a la lista documentos.

13–18. 📤 Copia de documentos
Se construye la ruta del archivo fuente desde el href.

Se verifica su existencia.

Se genera un nuevo nombre de archivo basado en el número de documento.

Se copia a la carpeta Documentos_Descargados usando shutil.copy2().

19. 📊 Conversión a DataFrame
La lista de diccionarios se transforma en un DataFrame de pandas.

20. 🧩 Procesamiento adicional (opcional)
Se puede abrir cada HTML referenciado por los enlaces para extraer datos adicionales (extendible).

21. 💾 Exportación a CSV
El DataFrame se guarda como documentos_extraidos.csv (UTF-8-SIG).
También se muestran las primeras filas por consola para verificación.