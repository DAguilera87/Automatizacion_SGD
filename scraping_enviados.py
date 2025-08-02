from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil
import re
from pathlib import Path
from pandas import ExcelWriter
from datetime import datetime
from tqdm import tqdm


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
# Ruta del archivo HTML fuente
ruta_html = r"C:/Users/DEYKE/Desktop/Repositorio/298_Respaldo_SGD_Clara_Analista/documentos/enviados.html"
carpeta_documentos = os.path.abspath(os.path.join(
    os.path.dirname(ruta_html), "..", "documentos"))
carpeta_destino = r"C:\Users\DEYKE\Desktop\Repositorio\298_Respaldo_SGD_Clara_Analista\Doc. Enviados"

# Preparar entorno
os.makedirs(carpeta_destino, exist_ok=True)
print(f"📑 HTML base: {ruta_html}")
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
print("🏁 Tabla encontrada.")

# Extraer datos de la tabla
documentos = []
filas = tabla.find("tbody").find_all("tr")
print(f"🔎 {len(filas)} filas encontradas.")

for fila in filas:
    celdas = fila.find_all("td")
    if len(celdas) < 7:
        continue

# Asegurarse de que hay suficientes columnas
    enlace_tag = celdas[0].find(
        "a")["href"].strip() if celdas[0].find("a") else ""
    documento = {
        "Fecha": celdas[0].get_text(strip=True),
        "Enlace": enlace_tag,  # Enlace al documento sin documentos. Pendiente
        "Nro Documento": celdas[1].get_text(strip=True),
        "De": celdas[2].get_text(strip=True),
        "Para": celdas[3].get_text(strip=True),
        "Asunto": celdas[4].get_text(strip=True),
        "Tipo Documento": celdas[5].get_text(strip=True),
        "Firma Digital": celdas[6].get_text(strip=True)
    }
    documentos.append(documento)
print(f"✅ Documentos extraídos.")
# Crear DataFrame y guardar logs
df = pd.DataFrame(documentos)
logs_por_fila = []
print("📊 DataFrame creado con los documentos.")

# Abrir HTMLs secundarios enlazados y procesar
print(f"⏳ Procesando fila")
for i, row in tqdm(df.iterrows(), total=len(df), desc="📦 Procesando documentos", ncols=100):
    enlace = row["Enlace"]
    nro_doc_original = row["Nro Documento"].strip()
    nro_doc = re.sub(r'[/:*?"<>|\\]', '_', nro_doc_original)
    log_msg = "⚠️ Sin log generado"

    if not enlace:
        log_msg = "❌ Sin enlace al HTML secundario"
        logs_por_fila.append(log_msg)
        print(log_msg)
        continue

# Verificar existencia del archivo HTML secundario
    ruta_html_secundario = os.path.join(carpeta_documentos, os.path.basename(enlace))
    if not os.path.exists(ruta_html_secundario):
        log_msg = f"❌ Archivo HTML no encontrado"
        logs_por_fila.append(log_msg)
        print(log_msg)
        continue
    
    # Abrir HTML secundario
    try:
        with open(ruta_html_secundario, encoding="utf-8") as f:
            html_individual = BeautifulSoup(f, "html.parser")
            div_datos = html_individual.find("div", {"id": "div_datos1"})
            if not div_datos:
                log_msg = f"⚠️ Div 'div_datos1' no encontrado"
                logs_por_fila.append(log_msg)
                print(log_msg)
                continue

        # Extraer enlace al PDF
        enlace_pdf_tag = div_datos.find("a", href=True)
        if not enlace_pdf_tag:
            log_msg = f"⚠️ Enlace PDF no encontrado"
            logs_por_fila.append(log_msg)
            continue

        # Verificar existencia del PDF
        href_pdf = enlace_pdf_tag["href"]
        ruta_pdf = os.path.normpath(os.path.join(
            os.path.dirname(ruta_html_secundario), href_pdf))
        if not os.path.exists(ruta_pdf):
            log_msg = f"❌ PDF no encontrado"
            logs_por_fila.append(log_msg)
            continue

        # Crear carpeta destino con número correlativo
        ruta_individual_carpeta = crear_carpeta_con_prefijo(
            carpeta_destino, nro_doc, contador_global
        )

        # Buscar el "No. de Documento" desde la tabla HTML secundaria
        tabla_info = div_datos.find("table")
        filas_info = tabla_info.find_all("tr")
        nombre_pdf_deseado = None
        for tr in filas_info:
            columnas = tr.find_all("td")
            if len(columnas) < 2:
                continue
            campo = columnas[0].get_text(strip=True)
            valor = columnas[1].get_text(strip=True)
            if "No. de Documento" in campo:
                nombre_pdf_deseado = valor.replace(" ", "").strip()  # elimina espacios
                break

        # Si no se encontró el nombre, usar nombre original del PDF
        if not nombre_pdf_deseado:
            nombre_pdf_deseado = os.path.splitext(os.path.basename(ruta_pdf))[0]

        # Crear nombre final con extensión .pdf
        nuevo_nombre_pdf = f"{nombre_pdf_deseado}.pdf"
        ruta_pdf_destino = os.path.join(ruta_individual_carpeta, nuevo_nombre_pdf)
        # Copiar y renombrar el PDF
        shutil.copy(ruta_pdf, ruta_pdf_destino)
        log_msg = f"📥 PDF copiado exitosamente"

    except Exception as e:
        log_msg = f"❌ Error al copiar PDF {e}"

    logs_por_fila.append(log_msg)

    # Verificar que los logs coincidan con el DataFrame
if len(df) != len(logs_por_fila):
    print("⚠️ Advertencia: la cantidad de logs no coincide con la cantidad de documentos.")
else:
    print("✅ Todos los logs coinciden con los documentos.")

# Añadir la columna de log al DataFrame
df["Logs"] = logs_por_fila

# Guardar DataFrame de logs actualizado en Excel junto con los documentos y Generar nombre de archivo Excel con timestamp
timestamp = datetime.now().strftime("%Y-%m-%d")
excel_path = os.path.join(
    carpeta_destino, f"doc._enviados_extraidos_{timestamp}.xlsx")
with ExcelWriter(excel_path, engine="xlsxwriter", engine_kwargs={"options": {"strings_to_urls": False}}) as writer:
    df.to_excel(writer, index=False, sheet_name="Doc._Enviados")


print(f"💾 Archivo Excel generado con datos y logs integrados.")
print(
    f"📬 Elementos creados: {len(os.listdir(carpeta_destino))} de {len(filas)} filas encontradas en la tabla.")
print("🎯 Proceso completado con éxito.")
# Fin del script
