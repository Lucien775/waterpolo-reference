"""
JSON à récupérer:
TeamRoster_ASF.JSON => Roster des équipes
SCH_* => contient tous les match jouées pour 1 date avec le code permettant d'avoir les stats détaillés
STA_* => stats détaillé pour un match
"""

import requests
import os
import time
import json

BASE_URL = "https://results.microplustimingservices.com/WorldAquatics/2026/WP/CroatiaU16W/assets/export/WPWC/{}.JSON"
HEADERS = {"User-Agent" : "Mozilla/5.0"}
OUTPUT_DIR = "cache_WCU16W"
DELAY = 0.3

def fetch_json(code):
	"""
	Récupère le JSON correspondant au code donné, ou NONE si erreur
	"""
	url = BASE_URL.format(code)
	resp = requests.get(url, headers=HEADERS, timeout=15)
	if resp.status_code == 404:
		return None
	resp.raise_for_status()
	return resp.json()

def main():
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	# 1. TeamRoster_ASF
	code = "TeamRoster_ASF"
	data = fetch_json(code)

	if data is not None:
		filepath = os.path.join(OUTPUT_DIR, f"{code}.json")
		with open(filepath, "w", encoding="utf-8") as f:
			json.dump(data, f, ensure_ascii=False, indent=2)
		print("Roster -> done\n")

	time.sleep(DELAY)

if __name__ == "__main__":
	main()
