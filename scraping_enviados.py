from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil

# Ruta del archivo HTML local
ruta = r"C:/Users/DEYKE/Desktop/Repositorio/respaldo_298/documentos/enviados.html"

# Carpeta donde están los documentos referenciados
carpeta_documentos = os.path.abspath(os.path.join(os.path.dirname(ruta), "..", "documentos"))

# Carpeta de destino para las copias descargadas
carpeta_salida = os.path.abspath(os.path.join(os.path.dirname(ruta), "Documentos_Descargados"))
os.makedirs(carpeta_salida, exist_ok=True)

# Parsear el HTML
with open(ruta, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Encuentra la tabla por ID
tabla = soup.find("table", {"id": "tbl_documentos"})

# Lista para almacenar los datos
documentos = []

# Extraer filas
for fila in tabla.find("tbody").find_all("tr"):
    columnas = fila.find_all("td")
    if len(columnas) < 7:
        continue

    # Extrae la información por columna
    enlace = columnas[0].find("a")["href"].strip() if columnas[0].find("a") else ""
    fecha = columnas[0].get_text(strip=True)
    no_doc = columnas[1].get_text(strip=True)
    remitente = columnas[2].get_text(strip=True)
    destinatario = columnas[3].get_text(strip=True)
    asunto = columnas[4].get_text(strip=True)
    tipo_doc = columnas[5].get_text(strip=True)
    firma_digital = columnas[6].get_text(strip=True)

    documentos.append({
        "Fecha": fecha,
        "Enlace": enlace,
        "Nro Documento": no_doc,
        "De": remitente,
        "Para": destinatario,
        "Asunto": asunto,
        "Tipo Documento": tipo_doc,
        "Firma Digital": firma_digital
    })

# Procesar descargas
for doc in documentos:
    enlace = doc["Enlace"]
    no_doc = doc["Nro Documento"]

    # Ruta absoluta del archivo de origen
    origen = os.path.abspath(os.path.join(carpeta_documentos, os.path.basename(enlace)))

    # Validación: existe el archivo?
    if not os.path.exists(origen):
        print(f"⚠️ Archivo no encontrado: {origen}")
        continue

    # Determinar extensión y destino
    extension = os.path.splitext(origen)[1]
    destino = os.path.join(carpeta_salida, f"{no_doc}{extension}")

    # Copiar
    shutil.copy2(origen, destino)
    print(f"✅ {no_doc} -> {destino}")

print("\n🟢 Proceso finalizado.")

# Convertir a DataFrame
df = pd.DataFrame(documentos)

# abrir cada HTML del enlace y sacar más info
base_dir = os.path.dirname(ruta)
for enlace in df["Enlace"]:
    ruta_completa = os.path.abspath(os.path.join(base_dir, enlace))
    print(f"Abrir archivo: {ruta_completa}")
    with open(ruta_completa, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        # Extraer más información según sea necesario


# Mostrar o guardar
print(df.head())
df.to_csv("documentos_extraidos.csv", index=False, encoding="utf-8-sig")
