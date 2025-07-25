import os
import time
import pandas as pd
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager

# Ruta del archivo local
path = r'C:\Users\DEYKE\Desktop\Repositorio\respaldo_298\documentos\enviados.html' # Cambia esta ruta según sea necesario
file_url = "file:///" + path.replace("\\", "/")

if not os.path.exists(path):
    print(f"❌ Archivo no encontrado: {path}")
    exit()

print(f"✅ Abriendo archivo local: {file_url}")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(file_url)

# Esperar carga y cambiar a frame izquierdo
time.sleep(10)  # Ajusta el tiempo según sea necesario
driver.switch_to.frame("left_frame")
#print("✅ Cambiado al frame 'left_frame'")

# Click en el menú 'Recibidos'
#try:
#    menu_recibidos = driver.find_element(By.ID, "div_menu_2")
#    menu_recibidos.click()
#    print("✅ Clic en 'Recibidos' realizado")
#except Exception as e:
#    print(f"❌ Error al hacer clic en 'Recibidos': {e}")

# Esperar para ver resultados antes de cerrar
#time.sleep(10)  # Ajusta el tiempo según sea necesario
driver.quit()
