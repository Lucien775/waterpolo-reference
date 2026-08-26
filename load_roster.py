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
from datetime import datetime, date
from sqlalchemy.orm import Session

from database import engine
from model import Competition, Equipe, Engagement, Personnel_Technique, Engagement_Personnel

def parse_date(value: str) -> "date | None":
	"""Convertit 'DD/MM/YYYY' en objet date, ou None si vide."""
	if not value:
		return None
	return datetime.strptime(value, "%d/%m/%Y").date()


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

def get_or_create_personnel(session: Session, code_federation: str, prenom: str, nom: str, 
							nationalite: str, date_naissance: date) -> Personnel_Technique:
	personnel = session.query(Personnel_Technique).filter_by(code_federation=code_federation).first()
	if personnel is None:
		personnel = Personnel_Technique(
			code_federation=code_federation,
			prenom=prenom,
			nom=nom,
			nationalite=nationalite,
			date_naissance=date_naissance
		)
		session.add(personnel)
		session.flush()
	return personnel
	


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

		for staff in team_entry["Staf"]:
			personnel = get_or_create_personnel(
				session,
				code_federation=staff["Cod"],
				prenom=staff["PlaNome"],
				nom=staff["PlaCogn"],
				nationalite=staff["PlaNaz"],
				date_naissance=parse_date(staff["PlaDatNas"])
			)

			deja_engage = (
				session.query(Engagement_Personnel)
				.filter_by(id_engagement=engagement.id, id_personnel=personnel.id)
				.first()
			)
			if deja_engage is None:
				session.add(Engagement_Personnel(
					id_engagement=engagement.id,
					id_personnel=personnel.id, 
					role_code=staff["RuoCod"],
					role_label=staff["RuoDescrEng"]
				))
				session.flush()


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

