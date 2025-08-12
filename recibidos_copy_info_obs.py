from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil
import re
import requests
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
ruta_html = r"C:\Users\DEYKE\Desktop\Repositorio\298_Respaldo_SGD_Clara_Analista\documentos\recibidos.html"
carpeta_documentos = os.path.abspath(os.path.join(
    os.path.dirname(ruta_html), "..", "documentos"))
carpeta_destino = r"C:\Users\DEYKE\Desktop\Repositorio\298_Respaldo_SGD_Clara_Analista\Doc. Recibidos"

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

    enlace_tag = celdas[0].find(
        "a")["href"].strip() if celdas[0].find("a") else ""
    documento = {
        "Fecha": celdas[0].get_text(strip=True),
        "Enlace": enlace_tag,
        "Nro Documento": celdas[1].get_text(strip=True),
        "De": celdas[2].get_text(strip=True),
        "Para": celdas[3].get_text(strip=True),
        "Asunto": celdas[4].get_text(strip=True),
        "Tipo Documento": celdas[5].get_text(strip=True),
        "Firma Digital": celdas[6].get_text(strip=True),
        "Con Copia a": "",
        "Anexos": 0  # Nueva columna para contar anexos
        # Observaciones se añadirá despues al DataFrame
    }
    documentos.append(documento)
print(f"✅ Documentos extraídos.")

df = pd.DataFrame(documentos)
# Asegurar columna Observaciones existe
if "Observaciones" not in df.columns:
    df["Observaciones"] = ""

logs_por_fila = []
print("📊 DataFrame creado con los documentos.")

# Contadores para estadísticas finales
total_anexos_descargados = 0

for i, row in tqdm(df.iterrows(), total=len(df), desc="📦 Procesando documentos", ncols=100):
    enlace = row["Enlace"]
    nro_doc_original = row["Nro Documento"].strip()
    nro_doc = re.sub(r'[/:*?"<>|\\]', '_', nro_doc_original)
    log_msg = "⚠️ Sin log generado"
    anexos_descargados = 0  # Contador de anexos para este documento
    observaciones_concat = ""  # acumulador de observaciones desde div_datos3

    if not enlace:
        log_msg = "❌ Sin enlace al HTML secundario"
        logs_por_fila.append(log_msg)
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat
        continue

    ruta_html_secundario = os.path.join(
        carpeta_documentos, os.path.basename(enlace))
    if not os.path.exists(ruta_html_secundario):
        log_msg = f"❌ Archivo HTML no encontrado"
        logs_por_fila.append(log_msg)
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat
        continue

    try:
        with open(ruta_html_secundario, encoding="utf-8") as f:
            html_individual = BeautifulSoup(f, "html.parser")
            div_datos = html_individual.find("div", {"id": "div_datos1"})
            if not div_datos:
                log_msg = f"⚠️ Div 'div_datos1' no encontrado"
                logs_por_fila.append(log_msg)
                df.at[i, "Anexos"] = anexos_descargados
                df.at[i, "Observaciones"] = observaciones_concat
                continue

        enlace_pdf_tag = div_datos.find("a", href=True)
        if not enlace_pdf_tag:
            log_msg = f"⚠️ Enlace PDF no encontrado"
            logs_por_fila.append(log_msg)
            df.at[i, "Anexos"] = anexos_descargados
            df.at[i, "Observaciones"] = observaciones_concat
            continue

        href_pdf = enlace_pdf_tag["href"]
        ruta_pdf = os.path.normpath(os.path.join(
            os.path.dirname(ruta_html_secundario), href_pdf))
        if not os.path.exists(ruta_pdf):
            log_msg = f"❌ PDF no encontrado"
            logs_por_fila.append(log_msg)
            df.at[i, "Anexos"] = anexos_descargados
            df.at[i, "Observaciones"] = observaciones_concat
            continue

        ruta_individual_carpeta = crear_carpeta_con_prefijo(
            carpeta_destino, nro_doc, contador_global
        )

        # Copiar anexos en div_datos2 a la carpeta individual
        div_datos2 = html_individual.find("div", {"id": "div_datos2"})
        if div_datos2:
            bloques_anexos = div_datos2.find_all("table", {"border": "1"})
            anexo_index = 0  # secuencial por documento
            for bloque in bloques_anexos:
                siguiente_tabla = bloque.find_next_sibling("table")
                if not siguiente_tabla:
                    continue

                filas = siguiente_tabla.find_all("tr")
                nombre_archivo = None
                enlace_pdf = None

                for fila2 in filas:
                    columnas = fila2.find_all("td")
                    if len(columnas) < 2:
                        continue

                    campo = columnas[0].get_text(strip=True).lower()
                    valor = columnas[1].get_text(
                        strip=True).replace("\xa0", " ").strip()

                    if "nombre:" in campo:
                        nombre_archivo = valor
                    elif "archivo:" in campo:
                        enlace_tag = columnas[1].find("a", href=True)
                        if enlace_tag:
                            enlace_pdf = enlace_tag["href"]

                if enlace_pdf and nombre_archivo:
                    ruta_adicional = os.path.normpath(os.path.join(
                        os.path.dirname(ruta_html_secundario), enlace_pdf))
                    if os.path.exists(ruta_adicional):
                        extension = os.path.splitext(ruta_adicional)[1]
                        nombre_limpio = re.sub(
                            r'[/:*?"<>|\\]', '_', nombre_archivo)
                        anexo_index += 1
                        nombre_final = f"Anexo{anexo_index}_{nombre_limpio}"
                        destino_adicional = os.path.join(
                            ruta_individual_carpeta, nombre_final)
                        try:
                            shutil.copy(ruta_adicional, destino_adicional)
                            anexos_descargados += 1  # Incrementar contador de anexos
                            log_msg += f" | 📎 Anexo {anexo_index} copiado como {nombre_final}"
                        except Exception as e:
                            log_msg += f" | ⚠️ Error al copiar anexo {anexo_index}: {e}"
                    else:
                        log_msg += f" | ⚠️ Anexo {anexo_index+1} no encontrado"

        # Extraer información de la tabla dentro de div_datos1
        tabla_info = div_datos.find("table")
        filas_info = tabla_info.find_all("tr") if tabla_info else []
        nombre_pdf_deseado = None
        de_valor = para_valor = copia_valor = ""

        for tr in filas_info:
            columnas = tr.find_all("td")
            if len(columnas) < 2:
                continue
            campo = columnas[0].get_text(strip=True).lower()
            valor_raw = " ".join(columnas[1].stripped_strings).replace(
                "\xa0", " ").strip()

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

        # Extraer Observaciones desde div_datos3
        div_datos3 = html_individual.find("div", {"id": "div_datos3"})
        if div_datos3:
            filas_d3 = div_datos3.find_all("tr")
            # si la primera fila es cabecera con 'Fecha','De','Para','Acción','Observación', saltarla
            start_idx = 0
            if filas_d3 and filas_d3[0].find_all("td"):
                headers_text = " ".join([td.get_text(strip=True).lower() for td in filas_d3[0].find_all("td")])
                if "acción" in headers_text and "observación" in headers_text:
                    start_idx = 1
            for tr_d3 in filas_d3[start_idx:]:
                cols_d3 = tr_d3.find_all("td")
                if len(cols_d3) >= 5:
                    accion_text = cols_d3[3].get_text(strip=True).lower()
                    observ_text = " ".join(cols_d3[4].stripped_strings).replace("\xa0", " ").strip()
                    # Si accion contiene 'reasignar' o 'informar', y hay observación, guardarla
                    if (("reasignar" in accion_text) or ("informar" in accion_text)) and observ_text:
                        if observaciones_concat:
                            observaciones_concat += " | " + observ_text
                        else:
                            observaciones_concat = observ_text

        # Guardar contador de anexos y observaciones
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat
        total_anexos_descargados += anexos_descargados

        if not nombre_pdf_deseado:
            nombre_pdf_deseado = os.path.splitext(
                os.path.basename(ruta_pdf))[0]

        nuevo_nombre_pdf = f"{nombre_pdf_deseado}.pdf"
        ruta_pdf_destino = os.path.join(
            ruta_individual_carpeta, nuevo_nombre_pdf)
        shutil.copy(ruta_pdf, ruta_pdf_destino)

        # Actualizar el log con información de anexos
        if anexos_descargados > 0:
            log_msg = f"📥 PDF Principal descargado | 📎 {anexos_descargados} anexo(s) descargado(s)"
        else:
            log_msg = f"📥 PDF Principal descargado | 📎 Sin anexos"

    except Exception as e:
        log_msg = f"❌ Error al descargar PDF principal {e}"
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat

    logs_por_fila.append(log_msg)

if len(df) != len(logs_por_fila):
    print("⚠️ Advertencia: la cantidad de logs no coincide con la cantidad de documentos.")
else:
    print("✅ Todos los logs coinciden con los documentos.")

df["Logs"] = logs_por_fila

# Estadísticas finales
documentos_con_anexos = len(df[df["Anexos"] > 0])
print(
    f"📬 Elementos creados: {len(os.listdir(carpeta_destino))} de {len(filas := tabla.find('tbody').find_all('tr'))} filas encontradas en la tabla.")
print(f"📋 Documentos con anexos: {documentos_con_anexos}")
print(f"📎 Total de anexos descargados: {total_anexos_descargados}")

timestamp = datetime.now().strftime("%Y-%m-%d")
excel_path = os.path.join(
    carpeta_destino, f"doc._recibidos_extraidos_{timestamp}.xlsx")
with ExcelWriter(excel_path, engine="xlsxwriter", engine_kwargs={"options": {"strings_to_urls": False}}) as writer:
    df.to_excel(writer, index=False, sheet_name="Doc._Recibidos")
print(f"💾 Archivo Excel generado con datos y logs integrados.")
print("🎯 Proceso completado con éxito.")
# Fin del script
# Fin del script
