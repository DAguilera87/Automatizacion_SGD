from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil
import re

# Crear carpeta con prefijo numérico
def crear_carpeta_con_prefijo(base_path, nombre_base, contador):
    while True:
        nombre_final = f"{str(contador).zfill(2)}_{nombre_base}"
        carpeta_destino = os.path.join(base_path, nombre_final)
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino, exist_ok=True)
            return carpeta_destino
        contador += 1

# Configuración inicial
contador_global = 1
ruta_html = r"C:/Users/DEYKE/Desktop/Repositorio/respaldo_298/documentos/enviados.html" # Ruta del archivo HTML fuente
carpeta_documentos = os.path.abspath(os.path.join(os.path.dirname(ruta_html), "..", "documentos"))
carpeta_destino = r"C:/Users/DEYKE/Desktop/Repositorio/respaldo_298/Doc. Enviados"

# Preparar entorno
os.makedirs(carpeta_destino, exist_ok=True)
print(f"📄 HTML base: {ruta_html}")
print(f"📁 Carpeta de documentos: {carpeta_documentos}")
print(f"📂 Carpetas destino: {carpeta_destino}")

# Leer y parsear el HTML
with open(ruta_html, "r", encoding="utf-8") as f:
    print("🔍 Cargando HTML...")
    soup = BeautifulSoup(f, "html.parser")
    print("✅ HTML cargado correctamente.")

# Buscar tabla con id: documentos
tabla = soup.find("table", {"id": "tbl_documentos"})
if not tabla:
    print("❌ No se encontró la tabla con ID 'tbl_documentos'.")
    exit(1)
print("✅ Tabla encontrada.")

# Extraer datos de la tabla
documentos = []
filas = tabla.find("tbody").find_all("tr")
print(f"🔎 {len(filas)} filas encontradas.")

for fila in filas:
    celdas = fila.find_all("td")
    doc = {
        "Nro Documento": celdas[0].get_text(strip=True)
    }
    if len(celdas) < 7:
        continue
    
# Asegurarse de que hay suficientes columnas
    enlace_tag = celdas[0].find("a")["href"].strip() if celdas[0].find("a") else ""
    documento = {
        "Fecha": celdas[0].get_text(strip=True),
        "Enlace": enlace_tag, # Enlace al documento sin documentos. Pendiente
        "Nro Documento": celdas[1].get_text(strip=True),
        "De": celdas[2].get_text(strip=True),
        "Para": celdas[3].get_text(strip=True),
        "Asunto": celdas[4].get_text(strip=True),
        "Tipo Documento": celdas[5].get_text(strip=True),
        "Firma Digital": celdas[6].get_text(strip=True)
    }
    documentos.append(documento)
print(f"✅ Documentos extraídos.")

# Crear carpeta individual
for doc in documentos:
    nro_doc_original = doc["Nro Documento"].strip()
    nro_doc = re.sub(r'[/:*?"<>|\\]', '_', nro_doc_original)

    try:
        ruta_individual_carpeta = crear_carpeta_con_prefijo(carpeta_destino, nro_doc, contador_global)
        print(f"📁 Carpetas creadas: {len(os.listdir(carpeta_destino))}")
    except Exception as e:
        print(f"❌ Error al crear carpeta para {nro_doc}: {e}")
        continue

# Crear DataFrame y guardar CSV
df = pd.DataFrame(documentos)
csv_path = os.path.join(carpeta_destino, "documentos_extraidos.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"\n📁 CSV generado")
print(df.head())

# Abrir HTMLs enlazados y procesar
for i, row in df.iterrows():
    enlace = row["Enlace"]
    if not enlace:
        continue

# Extra opcional: abrir cada HTML y extraer más info si se requiere
for i, row in df.iterrows():
    enlace = row["Enlace"]
    if not enlace:
        continue
    
    ruta_completa = os.path.join(carpeta_documentos, os.path.basename(enlace))
    if not os.path.exists(ruta_completa):
        print(f"❌ Archivo no encontrado: {ruta_completa}")
        continue

    with open(ruta_completa, encoding="utf-8") as f:
        html_individual = BeautifulSoup(f, "html.parser")
        # Aquí podrías extraer más info si deseas, por ejemplo:
        # detalle = html_individual.find("div", {"id": "detalle_documento"})
        # df.loc[i, "Detalle"] = detalle.get_text(strip=True) if detalle else ""

print("\n🟢 Proceso completado con éxito.")
# Fin del script