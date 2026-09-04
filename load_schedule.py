"""
Charge un fichier de calendrier SCH_*.json dans la base de donnees.

Ordre de dependances : necessite que load_roster.py ait deja ete execute
pour la competition concernee (on a besoin des Equipe/Engagement existants
pour retrouver a qui appartient chaque match).

Usage:
	python load_schedule.py SCH_25072026.JSON --source-slug CroatiaU16W --categorie U16 --genre Femme
"""

import argparse
import json
from datetime import datetime, date, time

from sqlalchemy.orm import Session

from database import engine
from model import Competition, Equipe, Engagement, Phase, Engagement_Phase, Match, Match_Engagement


def parse_date(value: str) -> "date | None":
	if not value:
		return None
	return datetime.strptime(value, "%d/%m/%Y").date()


def parse_time(value: str) -> "time | None":
	if not value:
		return None
	return datetime.strptime(value, "%H:%M").time()


def build_raw_code(entry: dict) -> str:
	"""Reconstruit le code STA_* a partir des champs du calendrier.
	Meme logique que pour construire l'URL des stats detaillees, ce qui nous
	permet de retrouver le meme Match depuis le fichier STA plus tard."""
	return f"{entry['c0']}{entry['c1']}{entry['c2']}{entry['c3']}{entry['c4']}{entry['c5']}"


def find_engagement(session: Session, team_code: str, categorie: str, genre: str,
                     competition_id: int) -> Engagement:
	"""Retrouve l'Engagement d'une equipe deja creee par load_roster.py.
	Leve une erreur explicite si l'equipe n'existe pas encore : signe que
	load_roster.py n'a pas ete execute avant, ou que le code equipe est faux."""
	equipe = session.query(Equipe).filter_by(code=team_code, categorie=categorie, genre=genre).first()
	if equipe is None:
		raise ValueError(f"Equipe '{team_code}' introuvable.")

	engagement = session.query(Engagement).filter_by(id_equipe=equipe.id, id_competition=competition_id).first()
	if engagement is None:
		raise ValueError(f"Aucun engagement pour '{team_code}' dans cette competition.")
	return engagement


def get_or_create_phase(session: Session, competition_id: int, raw_code: str, nom: str) -> Phase:
	phase = session.query(Phase).filter_by(id_competition=competition_id, raw_code=raw_code).first()
	if phase is None:
		phase = Phase(id_competition=competition_id, raw_code=raw_code, nom=nom.strip())
		session.add(phase)
		session.flush()
	return phase


def get_or_create_engagement_phase(session: Session, engagement_id: int, phase_id: int) -> Engagement_Phase:
	ep = session.query(Engagement_Phase).filter_by(id_engagement=engagement_id, id_phase=phase_id).first()
	if ep is None:
		ep = Engagement_Phase(id_engagement=engagement_id, id_phase=phase_id)
		session.add(ep)
		session.flush()
	return ep


def get_or_update_match(session: Session, raw_code: str, phase_id: int, date_: date,
                         heure_debut: time, lieu: str, statut: str) -> Match:
	"""On met a jour un match existant plutot que de sauter, car un statut
	(SCHEDULED -> FINISHED) ou un horaire peut changer si on recharge le
	calendrier plus tard dans le tournoi."""
	match = session.query(Match).filter_by(raw_code=raw_code).first()
	if match is None:
		match = Match(
			raw_code=raw_code, id_phase=phase_id, date=date_,
			heure_debut=heure_debut, lieu=lieu, statut=statut,
		)
		session.add(match)
		session.flush()
	else:
		match.statut = statut
		match.date = date_
		match.heure_debut = heure_debut
		match.lieu = lieu
	return match


def get_or_update_match_engagement(session: Session, match_id: int, engagement_id: int,
                                    cote: str, score: int) -> Match_Engagement:
	me = session.query(Match_Engagement).filter_by(id_match=match_id, id_engagement=engagement_id).first()
	if me is None:
		me = Match_Engagement(id_match=match_id, id_engagement=engagement_id, cote=cote, score=score)
		session.add(me)
		session.flush()
	else:
		me.score = score
	return me


def load_schedule(session: Session, data: dict, competition_id: int, categorie: str, genre: str) -> None:
	for entry in data["e"]:
		raw_code = build_raw_code(entry)

		phase = get_or_create_phase(session, competition_id, raw_code=entry["c2"], nom=entry["d_en"])

		engagement1 = find_engagement(session, entry["c4"], categorie, genre, competition_id)
		engagement2 = find_engagement(session, entry["c5"], categorie, genre, competition_id)

		get_or_create_engagement_phase(session, engagement1.id, phase.id)
		get_or_create_engagement_phase(session, engagement2.id, phase.id)

		match = get_or_update_match(
			session,
			raw_code=raw_code,
			phase_id=phase.id,
			date_=parse_date(entry["gi"]),
			heure_debut=parse_time(entry["h"]),
			lieu=entry["v"],
			statut=entry["sch_st"],
		)

		get_or_update_match_engagement(
			session, match.id, engagement1.id, cote="equipe1",
			score=int(entry["s1_p"]) if entry["s1_p"] else None,
		)
		get_or_update_match_engagement(
			session, match.id, engagement2.id, cote="equipe2",
			score=int(entry["s2_p"]) if entry["s2_p"] else None,
		)

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

		load_schedule(session, data, competition.id, args.categorie, args.genre)

	print("Calendrier charge.")