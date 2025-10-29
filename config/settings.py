from pathlib import Path
import os

# --- Caminho Raiz ---
# Isto encontra automaticamente o caminho raiz do seu projeto
# (a pasta 'projeto-analise-deputados')
PROJECT_ROOT = Path(__file__).parent.parent


# --- Caminhos de Dados ---
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GRAPHICS_DATA_DIR = DATA_DIR / "Graphics"


# --- Arquivos de Entrada ---
# 1. Arquivo original de deputados
DEPUTADOS_XLS_IN = RAW_DATA_DIR / "deputados.xls"


# --- Arquivos de Saída (Processados) ---
# 2. Saída do script 01_enrich_deputies.py
DEPUTADOS_INSTA_XLSX_OUT = PROCESSED_DATA_DIR / "deputados_com_instagram.xlsx"

# 3. Saídas do script 02_extract_instagram_data.py
APIFY_JSON_OUT = PROCESSED_DATA_DIR / "deputados.json"
APIFY_CSV_OUT = PROCESSED_DATA_DIR / "deputados.csv"


# --- Constantes de Scraping e API ---
CAMARA_SEARCH_URL = "https://www.camara.leg.br/deputados/quem-sao"
APIFY_ACTOR_ID = "shu8hvrXbJbY3Eb9W" # (Isto não é um segredo, então pode ficar aqui)

# --- Gráficos de AEDV
PLOT_1 = GRAPHICS_DATA_DIR / "plot_1_desigualdade_real.png"
PLOT_2 = GRAPHICS_DATA_DIR / "plot_2_dicotomia_real.png"
PLOT_3 = GRAPHICS_DATA_DIR / "plot_3_quadrantes_real.png"
PLOT_4 = GRAPHICS_DATA_DIR / "plot_4_frequencia_real.png"