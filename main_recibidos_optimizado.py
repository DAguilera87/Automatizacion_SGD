from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil
import re
import textwrap
from pathlib import Path
from pandas import ExcelWriter
from datetime import datetime
from tqdm import tqdm


# Ruta del archivo HTML fuente
ruta_html = r"c:\Users\deiker.aguilera\Desktop\WorkSpace\Script_SGD\302_Respaldo_SGD_Deiker_Prueba\documentos\recibidos.html"
carpeta_documentos = os.path.abspath(os.path.join(os.path.dirname(ruta_html), "..", "documentos"))
carpeta_destino = r"c:\Users\deiker.aguilera\Desktop\WorkSpace\Script_SGD\302_Respaldo_SGD_Deiker_Prueba\Doc. Recibidos"

# Crear carpeta con prefijo numérico
def crear_carpeta_con_prefijo(base_path, nombre_base, contador):
    while True:
        nombre_final = f"{str(contador).zfill(2)}_{nombre_base}"
        carpeta_destino = os.path.join(base_path, nombre_final)
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino, exist_ok=True)
            return carpeta_destino
        contador += 1


def crear_pdf_hoja_recorrido(ruta_pdf, titulo, datos_recorrido):
    """
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors
        import textwrap

        # Documento en horizontal para mejor visualización
        doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(A4), 
                            rightMargin=5*mm, leftMargin=5*mm, 
                            topMargin=5*mm, bottomMargin=5*mm)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=10, spaceAfter=4, alignment=TA_CENTER)
        
        elements = []
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 5*mm))
        
        if not datos_recorrido:
            elements.append(Paragraph("No se encontraron registros de recorrido.", styles['Normal']))
        else:
            # Crear tabla con encabezados
            table_data = [['Fecha', 'De', 'Para', 'Acción', 'Observación']]
            
            for registro in datos_recorrido:
                fecha = registro.get('fecha', '')
                if 'GMT' in fecha:
                    fecha = fecha.split('GMT')[0].strip()
                
                # Truncar textos largos
                de_texto = registro.get('de', '')
                if len(de_texto) > 40:
                    de_texto = de_texto[:40] + '...'
                
                para_texto = registro.get('para', '')
                if len(para_texto) > 40:
                    para_texto = para_texto[:40] + '...'
                
                accion_texto = registro.get('accion', '')
                
                # Formatear observación con saltos de línea
                observacion = registro.get('observacion', '')
                if len(observacion) > 70:
                    observacion = '\n'.join(textwrap.wrap(observacion, 70))
                
                table_data.append([fecha, de_texto, para_texto, accion_texto, observacion])
            
            # Crear anchos específicos y estilizar tabla
            table = Table(table_data, colWidths=[30*mm, 47*mm, 47*mm, 47*mm, 90*mm])
            
            # Aplicar estilos a la tabla
            table.setStyle(TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                
                # Cuerpo de la tabla
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                
                # Bordes y formato
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                
                # Espaciado interno
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            elements.append(table)
            
        # Construir el documento
        doc.build(elements)
        return True, f"PDF creado exitosamente: {ruta_pdf}"
    
    except ImportError as e:
        # Error de importación de ReportLab
        return crear_fallback_txt(ruta_pdf, titulo, datos_recorrido, f"ReportLab no disponible: {e}")
        
    except Exception as e:
        # Cualquier otro error
        return crear_fallback_txt(ruta_pdf, titulo, datos_recorrido, f"Error creando PDF: {e}")
        
def crear_fallback_txt(ruta_pdf, titulo, datos_recorrido, error_msg):
        # Función auxiliar para crear archivo TXT como fallback con formato tabla
        try:
            ruta_txt = os.path.splitext(ruta_pdf)[0] + ".txt"
        
            with open(ruta_txt, "w", encoding="utf-8") as fh:
                fh.write(titulo + "\n")
                fh.write("=" * len(titulo) + "\n\n")
                fh.write(f"NOTA: {error_msg}\n\n")
                
                if not datos_recorrido:
                    fh.write("No se encontraron registros de recorrido.\n")
                else:
                    # Encabezados con formato fijo
                    fh.write(f"{'Fecha':<25} {'De':<30} {'Para':<30} {'Acción':<25} {'Observación'}\n")
                    fh.write("-" * 150 + "\n")
                    
                    for registro in datos_recorrido:
                        fecha = registro.get('fecha', '').split('GMT')[0].strip() if 'GMT' in registro.get('fecha', '') else registro.get('fecha', '')
                        de_texto = registro.get('de', '')[:28]
                        para_texto = registro.get('para', '')[:28]
                        accion_texto = registro.get('accion', '')[:23]
                        observacion = registro.get('observacion', '')
                        
                        # Escribir línea principal
                        fh.write(f"{fecha:<25} {de_texto:<30} {para_texto:<30} {accion_texto:<25} ")
                        
                        # Manejar observaciones largas con wrap
                        if len(observacion) > 50:
                            obs_lines = textwrap.wrap(observacion, 50)
                            fh.write(f"{obs_lines[0]}\n")
                            for line in obs_lines[1:]:
                                fh.write(f"{'':<111} {line}\n")
                        else:
                            fh.write(f"{observacion}\n")
                        fh.write("-" * 150 + "\n")
                        
            return False, f"ReportLab no disponible: creado tabla TXT en {ruta_txt}"
        except Exception as e2:
            return False, f"Error creando fallback txt: {e2}"
def verificar_reportlab():
    try:
        import reportlab
        print(f"✅ ReportLab disponible - versión: {reportlab.Version}")
        return True
    except ImportError:
        print("❌ ReportLab NO está instalado")
        print("💡 Para instalar: pip install reportlab")
        return False

# Llamar la verificación al inicio
verificar_reportlab()

# Configuración inicial
contador_global = 1


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
        "Con Copia a": "",
        "Anexos": 0,
        "Observaciones": ""
    }
    documentos.append(documento)
print(f"✅ Documentos extraídos.")

df = pd.DataFrame(documentos)
logs_por_fila = []
print("📊 DataFrame creado con los documentos.")

# Contadores para estadísticas finales
total_anexos_descargados = 0

for i, row in tqdm(df.iterrows(), total=len(df), desc="📦 Procesando documentos", ncols=100):
    enlace = row["Enlace"]
    nro_doc_original = row["Nro Documento"].strip()
    nro_doc = re.sub(r'[/:*?"<>|\\]', '_', nro_doc_original)
    log_msg = "⚠️ Sin log generado"
    anexos_descargados = 0
    observaciones_concat = ""

    if not enlace:
        log_msg = "❌ Sin enlace al HTML secundario"
        logs_por_fila.append(log_msg)
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat
        continue

    ruta_html_secundario = os.path.join(carpeta_documentos, os.path.basename(enlace))
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
        ruta_pdf = os.path.normpath(os.path.join(os.path.dirname(ruta_html_secundario), href_pdf))
        if not os.path.exists(ruta_pdf):
            log_msg = f"❌ PDF no encontrado"
            logs_por_fila.append(log_msg)
            df.at[i, "Anexos"] = anexos_descargados
            df.at[i, "Observaciones"] = observaciones_concat
            continue

        ruta_individual_carpeta = crear_carpeta_con_prefijo(carpeta_destino, nro_doc, contador_global)

        # ------------------------
        # Anexos (procesamiento)
        # ------------------------
        div_datos2 = html_individual.find("div", {"id": "div_datos2"})
        if div_datos2:
            bloques_anexos = div_datos2.find_all("table", {"border": "1"})
            anexo_index = 0
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
                    valor = columnas[1].get_text(strip=True).replace("\xa0", " ").strip()

                    if "nombre:" in campo:
                        nombre_archivo = valor
                    elif "archivo:" in campo:
                        enlace_tag = columnas[1].find("a", href=True)
                        if enlace_tag:
                            enlace_pdf = enlace_tag["href"]

                if enlace_pdf and nombre_archivo:
                    ruta_adicional = os.path.normpath(os.path.join(os.path.dirname(ruta_html_secundario), enlace_pdf))
                    if os.path.exists(ruta_adicional):
                        extension = os.path.splitext(ruta_adicional)[1]
                        nombre_limpio = re.sub(r'[/:*?"<>|\\]', '_', nombre_archivo)
                        anexo_index += 1
                        nombre_final = f"Anexo{anexo_index}_{nombre_limpio}"
                        destino_adicional = os.path.join(ruta_individual_carpeta, nombre_final)
                        try:
                            shutil.copy(ruta_adicional, destino_adicional)
                            anexos_descargados += 1
                            log_msg += f" | 📎 Anexo {anexo_index} copiado como {nombre_final}"
                        except Exception as e:
                            log_msg += f" | ⚠️ Error al copiar anexo {anexo_index}: {e}"
                    else:
                        log_msg += f" | ⚠️ Anexo {anexo_index+1} no encontrado"

        # ------------------------
        # Extraer información de div_datos1
        # ------------------------
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

        # ------------------------
        # Detectar Reasignar / Informar en div_datos3
        # ------------------------
        div_datos3 = html_individual.find("div", {"id": "div_datos3"})
        datos_recorrido = []  # Lista de diccionarios para la tabla
        ha_reasignado = False
        ha_informado = False

        if div_datos3:
            filas_d3 = div_datos3.find_all("tr")
            start_idx = 0
            
            # Saltar encabezados si existen
            if filas_d3 and filas_d3[0].find_all("td"):
                headers_text = " ".join([td.get_text(strip=True).lower() for td in filas_d3[0].find_all("td")])
                if "acción" in headers_text and "observación" in headers_text:
                    start_idx = 1

            # Procesar cada fila y crear estructura para tabla
            for tr_d3 in filas_d3[start_idx:]:
                cols_d3 = tr_d3.find_all("td")
                if len(cols_d3) >= 5:
                    fecha_text = cols_d3[0].get_text(strip=True)
                    de_text = cols_d3[1].get_text(strip=True)
                    para_text = cols_d3[2].get_text(strip=True)
                    accion_text = cols_d3[3].get_text(strip=True)
                    observ_text = " ".join(cols_d3[4].stripped_strings).replace("\xa0", " ").strip()

                    # Añadir registro a los datos de la tabla
                    datos_recorrido.append({
                        'fecha': fecha_text,
                        'de': de_text,
                        'para': para_text,
                        'accion': accion_text,
                        'observacion': observ_text
                    })

                    # Detectar palabras clave
                    accion_lower = accion_text.lower()
                    if "reasignar" in accion_lower:
                        ha_reasignado = True
                    if "informar" in accion_lower:
                        ha_informado = True

        # Crear Hoja Recorrido si hay datos y acciones relevantes
        if ha_reasignado or ha_informado:
            # Preparar observaciones para Excel
            notas = []
            if ha_informado:
                notas.append("Doc. Informado")
            if ha_reasignado:
                notas.append("Doc. Reasignado")
            observaciones_concat = " - ".join(notas)

            # Crear Hoja Ruta en formato tabla
            titulo_pdf = f"HOJA RUTA {nro_doc_original}"
            ruta_hoja_pdf = os.path.join(ruta_individual_carpeta, f"#Hoja Ruta_{nro_doc_original}.pdf")
            ok, msg = crear_pdf_hoja_recorrido(ruta_hoja_pdf, titulo_pdf, datos_recorrido)
            if ok:
                log_msg += " | 🗺️ Hoja Ruta (tabla) creada"
            else:
                log_msg += f" | ⚠️ Hoja Ruta (fallback): {msg}"
        else:
            observaciones_concat = ""

        # Guardar contador de anexos y observaciones
        df.at[i, "Anexos"] = anexos_descargados
        df.at[i, "Observaciones"] = observaciones_concat
        total_anexos_descargados += anexos_descargados

        if not nombre_pdf_deseado:
            nombre_pdf_deseado = os.path.splitext(os.path.basename(ruta_pdf))[0]

        nuevo_nombre_pdf = f"{nombre_pdf_deseado}.pdf"
        ruta_pdf_destino = os.path.join(ruta_individual_carpeta, nuevo_nombre_pdf)
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
documentos_con_observaciones = len(df[df["Observaciones"] != ""])
print(f"📬 Elementos creados: {len(os.listdir(carpeta_destino))} de {len(filas := tabla.find('tbody').find_all('tr'))} filas encontradas en la tabla.")
print(f"📋 Documentos con anexos: {documentos_con_anexos}")
print(f"📎 Total de anexos descargados: {total_anexos_descargados}")
print(f"🗺️ Documentos con Hoja Recorrido: {documentos_con_observaciones}")

timestamp = datetime.now().strftime("%Y-%m-%d")
excel_path = os.path.join(
    carpeta_destino, f"doc._recibidos_extraidos_{timestamp}.xlsx") # Nombre del archivo Excel
with ExcelWriter(excel_path, engine="xlsxwriter", engine_kwargs={"options": {"strings_to_urls": False}}) as writer:
    df.to_excel(writer, index=False, sheet_name="Doc._Recibidos")
print(f"💾 Archivo Excel generado con datos y logs integrados.")
print("🎯 Proceso completado con éxito.")
# Fin del script