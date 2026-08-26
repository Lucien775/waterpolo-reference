"""
1. On récupère l'id de la compétition avec le slug
2. Equipe -> Engagement
3. Staff tech -> Engagement_Perso
4. Joueur -> Roster

Usage:
	python load_roster.py TeamRoster_ASF.json --source-slug CroatiaU16W --categorie U16 --genre Femme
"""

import argparse
import json

from sqlalchemy.orm import Session

from database import engine
from model import Competition, Equipe, Engagement

def get_or_create_equipe(session: Session, code: str, nom_pays: str, categorie: str, genre: str)->Equipe:
	equipe = session.query(Equipe).filter_by(code=code, categorie=categorie, genre=genre).first()
	if equipe is None:
		equipe = Equipe(code=code, nom_pays=nom_pays, categorie=categorie, genre=genre)
		session.add(equipe)
		session.flush()
	return equipe

def get_or_create_engagement(session: Session, equipe_id: int, competition_id: int)-> Engagement:
	engagement = session.query(Engagement).filter_by(id_equipe=equipe_id, id_competition=competition_id).first()
	if engagement is None:
		engagement = Engagement(id_equipe=equipe_id, id_competition=competition_id)
		session.add(engagement)
		session.flush()
	return engagement


def load_roster(session: Session, data: dict, competition_id: int, categorie: str, genre: str) -> None:
	for team_entry in data["n"]:
		equipe = get_or_create_equipe(
			session,
			code=team_entry["teamCod"],
			nom_pays=team_entry["d_en"],
			categorie=categorie,
			genre=genre,
		)
		engagement = get_or_create_engagement(session, equipe.id, competition_id)
	session.commit()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("fichier_json")
	parser.add_argument("--source-slug", type=str, required=True)
	parser.add_argument("--categorie", type=str, required=True)
	parser.add_argument("--genre", type=str, required=True)
	args = parser.parse_args()

	with open(args.fichier_json, encoding="utf-8") as f:
		data = json.load(f)

	with Session(engine) as session:
		competition = session.query(Competition).filter_by(source_slug=args.source_slug).first()
		if competition is None:
			raise ValueError(f"La competition avec le slug '{args.source_slug}' n'existe pas")
		
		load_roster(session, data, competition.id, args.categorie, args.genre)

