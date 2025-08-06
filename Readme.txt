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