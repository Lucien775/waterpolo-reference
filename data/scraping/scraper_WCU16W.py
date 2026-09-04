"""
JSON à récupérer:
TeamRoster_ASF.JSON => Roster des équipes
SCH_DDMMYYYY.JSON => contient tous les match jouées la date correspondante 
STA_*.JSON => stats détaillé pour un match
"""

import requests
import os
import time
import json
from datetime import date, timedelta

BASE_URL = "https://results.microplustimingservices.com/WorldAquatics/2026/WP/CroatiaU16W/assets/export/WPWC/{}.JSON"
HEADERS = {"User-Agent" : "Mozilla/5.0"}
OUTPUT_DIR = "cache_WCU16W"
DELAY = 0.3
DATE_DEBUT = date(2026,7,25)
DATE_FIN = date(2026,7,31)

def date_range(d1,d2):
	for n in range((d2-d1).days + 1):
		yield d1 + timedelta(days=n)

def build_code(row):
	"""Reconstruit le code STA_* à partir des champs bruts du match."""
	return f"STA_{row['c0']}{row['c1']}{row['c2']}{row['c3']}{row['c4']}{row['c5']}"

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

	# 2. SCH_*.JSON
	rows = []
	for d in date_range(DATE_DEBUT, DATE_FIN):
		days_code = d.strftime("%d%m%Y")
		code = f"SCH_{days_code}"
		data = fetch_json(code)
		if data is not None:
			filepath = os.path.join(OUTPUT_DIR, f"{code}.json")
			with open(filepath, "w", encoding="utf-8") as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
			for match in data["e"]:
				rows.append({
				# Champs nécessaire pour reconstruire l'URL des stats détaillées
				# (STA_{c0}{c1}{c2}{c3}{c4}{c5}.JSON)
				"c0" : match.get("c0"),
				"c1" : match.get("c1"),
				"c2" : match.get("c2"),
				"c3" : match.get("c3"),
				"c4" : match.get("c4"),
				"c5" : match.get("c5"),
			})
			print(f"{code} -> done\n")
		time.sleep(DELAY)

	# 3. STA_*.JSON
	for row in rows:
		code = build_code(row)
		data = fetch_json(code)
		if data is not None:
			filepath = os.path.join(OUTPUT_DIR, f"{code}.json")
			with open(filepath, "w", encoding="utf-8") as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
			print(f"{row['c4']} vs {row['c5']} ({code}) -> OK")

		time.sleep(DELAY)


if __name__ == "__main__":
	main()
