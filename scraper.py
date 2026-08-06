"""
Scraper pour les résultats de la compétition World Aquatics WP CroatiaU16W
(système Microplus Timing Services)
 
Le site expose un fichier JSON statique par journée de compétition, au format :
https://results.microplustimingservices.com/WorldAquatics/2026/WP/CroatiaU16W/assets/export/WPWC/SCH_DDMMYYYY.JSON

En sortie, on obtient un fichier avec tous les matchs de la compétition
"""



import requests
import time
import pandas as pd 
from datetime import date, timedelta

BASE_URL = "https://results.microplustimingservices.com/WorldAquatics/2026/WP/CroatiaU16W/assets/export/WPWC/SCH_{}.JSON"
HEADERS = {"User-Agent" : "Mozilla/5.0"}

# Date de la compétition
DATE_DEBUT = date(2026,7,25)
DATE_FIN = date(2026,7,31)

def date_range(d1,d2):
	for n in range((d2-d1).days + 1):
		yield d1 + timedelta(days=n)

def fetch_days(d):
	"""Récupère le JSON d'un jour donné, ou NONE s'il n'y a pas de fichier"""
	filename = d.strftime("%d%m%Y")
	url = BASE_URL.format(filename)
	resp = requests.get(url, headers=HEADERS, timeout=15)
	if resp.status_code == 404:
		return None
	resp.raise_for_status()
	return resp.json()

def parse_days(day_json):
	"""Transforme la liste d'événement brut en lignes exploitables"""
	rows = []
	if not day_json or "e" not in day_json:
		return rows

	for match in day_json["e"]:
		rows.append({
			"date" : match.get("gi"),
			"heure" : match.get("h"),
			"match_num" : match.get("nm"),
			"phase": match.get("d_en"),
			"equipe1": match.get("dt1"),
			"equipe2": match.get("dt2"),
			"code1": match.get("c4"),
			"code2": match.get("c5"),
			"score1": match.get("s1_p"),
			"score2": match.get("s2_p"),
			"statut": match.get("sch_st"),
			"lieu": match.get("v"),
			# Champs nécessaire pour reconstruire l'URL des stats détaillées
			# (STA_{c0}{c1}{c2}{c3}{c4}{c5}.JSON)
			"c0" : match.get("c0"),
			"c1" : match.get("c1"),
			"c2" : match.get("c2"),
			"c3" : match.get("c3"),
			"c4" : match.get("c4"),
			"c5" : match.get("c5"),
		})
	return rows

def main():
	all_rows = []

	for d in date_range(DATE_DEBUT, DATE_FIN):
		day_json = fetch_days(d)
		rows = parse_days(day_json)
		if rows:
			print(f"  -> {len(rows)} matchs trouvés")
		all_rows.extend(rows)
		time.sleep(0.5)

	df = pd.DataFrame(all_rows)
	df["score1"] = pd.to_numeric(df["score1"], errors="coerce")
	df["score2"] = pd.to_numeric(df["score2"], errors="coerce")

	output_path = "resultats_waterpolo.csv"
	df.to_csv(output_path, index=False, encoding="utf-8-sig")
	print(f"\n{len(df)} matchs enregistrés dans {output_path}")

	return df


if __name__ == "__main__":
	main()



