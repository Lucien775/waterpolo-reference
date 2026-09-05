"""
Orchestre le pipeline complet pour une competition :
  1. Cree la competition si elle n'existe pas deja
  2. Lance le scraping (remplit le cache local de JSON)
  3. Charge le roster (equipes, staff, joueuses)
  4. Charge le calendrier (tous les fichiers SCH_*.json du cache)
  5. Charge les stats detaillees (tous les fichiers STA_*.json du cache)

Usage:
	python orchestrate.py \\
		--source-slug CroatiaU16W --categorie U16 --genre Femme \\
		--nom "World Championship U16W 2026" --sport-code ASF \\
		--lieu Zagreb --date-debut 25/07/2026 --date-fin 31/07/2026
"""

import argparse
import glob
import json
import os
from datetime import datetime

from sqlalchemy.orm import Session

from data.database import engine
from data.model import Competition
from data.loading.create_competition import create_competition
from data.loading.load_roster import load_roster
from data.loading.load_schedule import load_schedule
from data.loading.load_stats import load_stats
from data.scraping import scraper_WCU16W


def ensure_competition(session: Session, args) -> Competition:
	"""Cree la competition si absente, reutilise l'existante sinon.
	(create_competition() leve une erreur si elle existe deja """
	competition = session.query(Competition).filter_by(source_slug=args.source_slug).first()
	if competition is not None:
		print(f"Competition existante reutilisee (id={competition.id})")
		return competition

	competition = create_competition(
		session, args.nom, args.sport_code, args.lieu, args.source_slug,
		args.date_debut, args.date_fin,
	)
	print(f"Competition creee (id={competition.id})")
	return competition


def run_scraping() -> str:
	"""Lance le scraper et renvoie le dossier ou il a ecrit les fichiers.
	On lit OUTPUT_DIR directement depuis le module plutot que de le
	redefinir ici, pour ne jamais avoir deux valeurs qui divergent."""
	print("Scraping en cours...")
	scraper_WCU16W.main()
	return scraper_WCU16W.OUTPUT_DIR


def load_all_schedule_files(session: Session, cache_dir: str, competition_id: int,
                             categorie: str, genre: str) -> None:
	fichiers = sorted(glob.glob(os.path.join(cache_dir, "SCH_*.json")))
	print(f"Chargement du calendrier ({len(fichiers)} journee(s) trouvee(s))...")

	for filepath in fichiers:
		try:
			with open(filepath, encoding="utf-8") as f:
				data = json.load(f)
			load_schedule(session, data, competition_id, categorie, genre)
			print(f"  OK: {os.path.basename(filepath)}")
		except Exception as e:
			# Une journee en erreur ne doit pas bloquer les autres.
			print(f"  ECHEC sur {os.path.basename(filepath)}: {e}")


def load_all_stats_files(session: Session, cache_dir: str, competition_id: int,
                          categorie: str, genre: str) -> None:
	fichiers = sorted(glob.glob(os.path.join(cache_dir, "STA_*.json")))
	print(f"Chargement des stats detaillees ({len(fichiers)} match(s) trouve(s))...")

	echecs = []
	for filepath in fichiers:
		try:
			with open(filepath, encoding="utf-8") as f:
				data = json.load(f)
			load_stats(session, data, competition_id, categorie, genre)
			print(f"  OK: {os.path.basename(filepath)}")
		except Exception as e:
			# Meme logique : un match rate n'empeche pas de charger les autres.
			echecs.append((os.path.basename(filepath), str(e)))
			print(f"  ECHEC sur {os.path.basename(filepath)}: {e}")

	if echecs:
		print(f"\n{len(echecs)} match(s) non charge(s) :")
		for nom, erreur in echecs:
			print(f"  - {nom}: {erreur}")


def main(args) -> None:
	with Session(engine) as session:
		competition = ensure_competition(session, args)

		if not args.skip_scrape:
			cache_dir = run_scraping()
		else:
			cache_dir = scraper_WCU16W.OUTPUT_DIR
			print(f"Scraping ignore (--skip-scrape), utilisation du cache existant: {cache_dir}")

		roster_path = os.path.join(cache_dir, "TeamRoster_ASF.json")
		print("Chargement du roster...")
		with open(roster_path, encoding="utf-8") as f:
			roster_data = json.load(f)
		load_roster(session, roster_data, competition.id, args.categorie, args.genre)
		print("  OK")

		load_all_schedule_files(session, cache_dir, competition.id, args.categorie, args.genre)
		load_all_stats_files(session, cache_dir, competition.id, args.categorie, args.genre)

	print("\nPipeline termine.")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--source-slug", required=True)
	parser.add_argument("--categorie", required=True, help="ex: U16")
	parser.add_argument("--genre", required=True, help="ex: Femme")
	parser.add_argument("--nom", required=True, help="Nom complet de la competition")
	parser.add_argument("--sport-code", required=True, help="ex: ASF")
	parser.add_argument("--lieu", required=True)
	parser.add_argument("--date-debut", required=True, help="format DD/MM/YYYY")
	parser.add_argument("--date-fin", required=True, help="format DD/MM/YYYY")
	parser.add_argument("--skip-scrape", action="store_true",
	                     help="Ne relance pas le scraping, utilise le cache existant")
	args = parser.parse_args()

	args.date_debut = datetime.strptime(args.date_debut, "%d/%m/%Y").date()
	args.date_fin = datetime.strptime(args.date_fin, "%d/%m/%Y").date()

	main(args)