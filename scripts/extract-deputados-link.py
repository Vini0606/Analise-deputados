"""
Script: preencher_instagram_deputados.py
Objetivo: Completar a planilha de deputados federais com links oficiais de Instagram,
buscando apenas no site oficial da Câmara dos Deputados.
Autor: ChatGPT
"""

# Importa as configurações do seu novo arquivo
# (Adicione 'sys' e 'os' para garantir que ele encontre a pasta config)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# === IMPORTAÇÕES ===
from config import settings
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# === CONFIGURAÇÃO DO SELENIUM ===
chrome_options = Options()
#chrome_options.add_argument("--headless")  # remove esta linha se quiser ver o navegador abrindo
#chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

wait = WebDriverWait(driver, 10)

# === 1. CARREGAR PLANILHA ===
df = pd.read_excel(settings.DEPUTADOS_XLS_IN)

# Garantir que há uma coluna 'Instagram'
if "Instagram" not in df.columns:
    df["Instagram"] = ""


def buscar_instagram_deputado(nome):
    try:
        # Abrir página principal de busca
        driver.get("https://www.camara.leg.br/deputados/quem-sao")
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.ID, "parametro-nome-2"))).send_keys(nome)

        wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[text()='Buscar'])[3]"))).click()

        wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@class='nome-deputado']"))).click()

        # Procurar links de redes sociais
        link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='username-insta']"))).get_attribute("href")

        return link

    except Exception as e:
        print(f"Erro ao buscar {nome}: {e}")
        return None# === 3. LOOP SOBRE OS DEPUTADOS ===

total = len(df)
for i, row in df.iterrows():
    nome = row["Nome Parlamentar"]
    if pd.isna(row["Instagram"]) or str(row["Instagram"]).strip() == "":
        print(f"[{i+1}/{total}] Buscando Instagram de {nome}...")
        link_instagram = buscar_instagram_deputado(nome)
        if link_instagram:
            df.at[i, "Instagram"] = link_instagram
            print(f"✅ Encontrado: {link_instagram}")
        else:
            print("❌ Não encontrado")
    else:
        print(f"[{i+1}/{total}] Já possui Instagram: {row['Instagram']}")

# === 4. SALVAR NOVA PLANILHA ===
df.to_excel(settings.DEPUTADOS_INSTA_XLSX_OUT, index=False)
print(f"\n✅ Planilha atualizada salva como: {settings.DEPUTADOS_INSTA_XLSX_OUT}")

# === 5. ENCERRAR DRIVER ===
driver.quit()
