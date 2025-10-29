# Importa as configurações do seu novo arquivo
# (Adicione 'sys' e 'os' para garantir que ele encontre a pasta config)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Prepare the Actor input
from config import settings
from apify_client import ApifyClient
import json
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

df = pd.read_excel(settings.DEPUTADOS_INSTA_XLSX_OUT).dropna(subset=['Instagram'])

run_input = {
    "directUrls": list(df['Instagram'].unique()),
    "addParentData": False,
    "enhanceUserSearchWithFacebookPage": False,
    "isUserReelFeedURL": False,
    "isUserTaggedFeedURL": False,
    "resultsLimit": 515,
    "resultsType": "details",
    "searchType": "user"
}

api_token = os.getenv("APIFY_API_TOKEN")

client = ApifyClient(api_token)

# Run the Actor and wait for it to finish
run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)

items = []

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    items.append(item)
    
# Salva o item como um arquivo JSON
with open(settings.APIFY_JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=4)

# 7. Salvar os resultados em CSV
print(f"Salvando resultados em CSV: {settings.APIFY_CSV_OUT}")
df_results = pd.DataFrame(items) # <-- Converte a lista 'items' em DataFrame
df_results.to_csv(settings.APIFY_CSV_OUT, index=False, sep=';', encoding='utf-8') # <-- Salva como CSV

print("Processo concluído com sucesso!")