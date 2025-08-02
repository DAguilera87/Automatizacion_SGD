
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
carpeta_destino = r"C:/Users/DEYKE/Desktop/Repositorio/298_Respaldo_SGD_Clara_Analista/Doc. Enviados"

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

    enlace_tag = celdas[0].find("a")["href"].strip() if celdas[0].find("a") else ""
    documento = {
        "Fecha": celdas[0].get_text(strip=True),
        "Enlace": enlace_tag,
        "Nro Documento": celdas[1].get_text(strip=True),
        "De": celdas[2].get_text(strip=True),
        "Para": celdas[3].get_text(strip=True),
        "Asunto": celdas[4].get_text(strip=True),
        "Tipo Documento": celdas[5].get_text(strip=True),
        "Firma Digital": celdas[6].get_text(strip=True),
        "Con Copia a": ""
    }
    documentos.append(documento)
print(f"✅ Documentos extraídos.")

df = pd.DataFrame(documentos)
logs_por_fila = []

print("📊 DataFrame creado con los documentos.")

for i, row in tqdm(df.iterrows(), total=len(df), desc="📦 Procesando documentos", ncols=100):
    enlace = row["Enlace"]
    nro_doc_original = row["Nro Documento"].strip()
    nro_doc = re.sub(r'[/:*?"<>|\\]', '_', nro_doc_original)
    log_msg = "⚠️ Sin log generado"

    if not enlace:
        log_msg = "❌ Sin enlace al HTML secundario"
        logs_por_fila.append(log_msg)
        continue

    ruta_html_secundario = os.path.join(carpeta_documentos, os.path.basename(enlace))
    if not os.path.exists(ruta_html_secundario):
        log_msg = f"❌ Archivo HTML no encontrado"
        logs_por_fila.append(log_msg)
        continue

    try:
        with open(ruta_html_secundario, encoding="utf-8") as f:
            html_individual = BeautifulSoup(f, "html.parser")
            div_datos = html_individual.find("div", {"id": "div_datos1"})
            if not div_datos:
                log_msg = f"⚠️ Div 'div_datos1' no encontrado"
                logs_por_fila.append(log_msg)
                continue

        enlace_pdf_tag = div_datos.find("a", href=True)
        if not enlace_pdf_tag:
            log_msg = f"⚠️ Enlace PDF no encontrado"
            logs_por_fila.append(log_msg)
            continue

        href_pdf = enlace_pdf_tag["href"]
        ruta_pdf = os.path.normpath(os.path.join(
            os.path.dirname(ruta_html_secundario), href_pdf))
        if not os.path.exists(ruta_pdf):
            log_msg = f"❌ PDF no encontrado"
            logs_por_fila.append(log_msg)
            continue

        ruta_individual_carpeta = crear_carpeta_con_prefijo(
            carpeta_destino, nro_doc, contador_global
        )

        tabla_info = div_datos.find("table")
        filas_info = tabla_info.find_all("tr") if tabla_info else []
        nombre_pdf_deseado = None
        de_valor = para_valor = copia_valor = ""

        for tr in filas_info:
            columnas = tr.find_all("td")
            if len(columnas) < 2:
                continue
            campo = columnas[0].get_text(strip=True).lower()
            valor_raw = " ".join(columnas[1].stripped_strings).replace("\xa0", " ").strip()

            if "no. de documento" in campo:
                nombre_pdf_deseado = valor_raw.replace(" ", "")
            elif campo == "de:":
                de_valor = valor_raw
            elif campo == "para:":
                para_valor = valor_raw
            elif campo == "con copia a:":
                copia_valor = valor_raw

        if de_valor:
            df.at[i, "De"] = f"{de_valor}"
        if para_valor:
            df.at[i, "Para"] = f"{para_valor}"
        if copia_valor:
            df.at[i, "Con Copia a"] = f"{copia_valor}"

        if not nombre_pdf_deseado:
            nombre_pdf_deseado = os.path.splitext(os.path.basename(ruta_pdf))[0]

        nuevo_nombre_pdf = f"{nombre_pdf_deseado}.pdf"
        ruta_pdf_destino = os.path.join(ruta_individual_carpeta, nuevo_nombre_pdf)
        shutil.copy(ruta_pdf, ruta_pdf_destino)
        log_msg = f"📥 PDF copiado exitosamente"

    except Exception as e:
        log_msg = f"❌ Error al copiar PDF {e}"

    logs_por_fila.append(log_msg)

if len(df) != len(logs_por_fila):
    print("⚠️ Advertencia: la cantidad de logs no coincide con la cantidad de documentos.")
else:
    print("✅ Todos los logs coinciden con los documentos.")

df["Logs"] = logs_por_fila

timestamp = datetime.now().strftime("%Y-%m-%d")
excel_path = os.path.join(
    carpeta_destino, f"doc._enviados_extraidos_{timestamp}.xlsx")
with ExcelWriter(excel_path, engine="xlsxwriter", engine_kwargs={"options": {"strings_to_urls": False}}) as writer:
    df.to_excel(writer, index=False, sheet_name="Doc._Enviados")

print(f"💾 Archivo Excel generado con datos y logs integrados.")
print(f"📬 Elementos creados: {len(os.listdir(carpeta_destino))} de {len(filas)} filas encontradas en la tabla.")
print("🎯 Proceso completado con éxito.")
