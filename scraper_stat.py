"""
Récupère le fichier STA_*.JSON (stats détaillées) de chaque match listé
dans le CSV produit par scrape_waterpolo.py.
 
L'URL est reconstruite directement à partir des champs c0/c1/c2/c3/code1/code2
déjà présents dans le CSV : pas besoin de deviner le pattern des phases finales,
il est identique à celui des poules.
"""

import requests
import time
import json
import os
import pandas as pd

BASE_URL = "https://results.microplustimingservices.com/WorldAquatics/2026/WP/CroatiaU16W/assets/export/WPWC/STA_{}.JSON"
HEADERS = {"User-Agent" : "Mozilla/5.0"}
INPUT_CSV = "resultats_waterpolo.csv"
OUTPUT_DIR = "stats_matchs"
DELAY = 0.3

def build_code(row):
	"""Reconstruit le code STA_* à partir des champs bruts du match."""
	return f"{row['c0']}{row['c1']}{row['c2']}{row['c3']}{row['c4']}{row['c5']}"

def fetch_stat(code):
	url = BASE_URL.format(code)
	resp = requests.get(url, headers=HEADERS, timeout=15)
	if resp.status_code == 404:
		return None
	resp.raise_for_status()
	return resp.json()

def main():
	df = pd.read_csv(INPUT_CSV)
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	for i, row in df.iterrows():
		code = build_code(row)
		data = fetch_stat(code)

		if data is not None:
			filepath = os.path.join(OUTPUT_DIR, f"STA_{code}.json")
			with open(filepath, "w", encoding="utf-8") as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
			print(f"[{i+1}/{len(df)}] {row['equipe1']} vs {row['equipe2']} ({code}) -> OK")

		time.sleep(DELAY)

if __name__ == "__main__":
	main()
