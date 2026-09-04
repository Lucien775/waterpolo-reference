"""
Charge un fichier de stats detaillees STA_*.json dans la base de donnees.

Ordre de dependances : necessite que load_roster.py (joueuses, staff) et
load_schedule.py (le Match et ses deux Match_Engagement) aient deja ete
executes pour cette competition.

Usage:
	python load_stats.py STA_ASF1A011GREMEX.JSON --source-slug CroatiaU16W --categorie U16 --genre Femme
"""

import argparse
import json
from datetime import datetime, date, time

from sqlalchemy.orm import Session

from data.database import engine
from data.model import (
	Competition, Equipe, Engagement, Match, Match_Engagement, Match_Engagement_Periode,
	Officiel, Match_Officiel, Joueur, Apparition,
)


# ---------- Utilitaires de conversion ----------

def parse_date(value: str) -> "date | None":
	if not value:
		return None
	return datetime.strptime(value, "%d/%m/%Y").date()


def parse_time(value: str) -> "time | None":
	if not value:
		return None
	return datetime.strptime(value, "%H:%M").time()


def parse_int(value: str) -> "int | None":
	if value in (None, ""):
		return None
	return int(value)


def parse_ratio(value: str) -> tuple:
	"""'2/3' -> (2, 3) ; '' -> (None, None). Position [0] = tentes, [1] = reussis
	dans le format source, mais nos colonnes veulent (reussis, tentes) dans cet
	ordre car c'est ainsi que sont nommees nos colonnes _reussis/_tentes."""
	if not value:
		return (None, None)
	reussis, tentes = value.split("/")
	return (int(reussis), int(tentes))


def parse_percent(value: str) -> "float | None":
	"""'100,0%' -> 100.0 ; '' -> None. Le format source utilise la virgule."""
	if not value:
		return None
	return float(value.replace(",", ".").replace("%", ""))


def parse_flag(value: str) -> bool:
	"""Pour EX/4EX_ : n'importe quelle valeur non vide et non '0' compte comme vrai.
	A verifier sur de vraies donnees de phase finale ou ces champs sont probablement
	renseignes - dans nos exemples de poule ils valent toujours '0'."""
	return value not in (None, "", "0")


# ---------- Reconstruction du raw_code pour retrouver le Match ----------

def build_raw_code(data: dict) -> str:
	"""Les champs sont nommes differemment ici que dans le calendrier
	(Category.Cod, Competition.Cod, Round.Cod, Heat.Cod au lieu de c0-c3),
	mais la concatenation donne le meme code que celui construit par
	load_schedule.py, ce qui permet de retrouver le Match deja cree."""
	return (
		f"{data['Category']['Cod']}{data['Competition']['Cod']}"
		f"{data['Round']['Cod']}{data['Heat']['Cod']}{data['s1']}{data['s2']}"
	)


# ---------- Recherche des entites deja creees par les scripts precedents ----------

def find_engagement(session: Session, team_code: str, categorie: str, genre: str,
                     competition_id: int) -> Engagement:
	equipe = session.query(Equipe).filter_by(code=team_code, categorie=categorie, genre=genre).first()
	if equipe is None:
		raise ValueError(f"Equipe '{team_code}' introuvable. As-tu bien charge le roster avant ?")

	engagement = session.query(Engagement).filter_by(id_equipe=equipe.id, id_competition=competition_id).first()
	if engagement is None:
		raise ValueError(f"Aucun engagement pour '{team_code}' dans cette competition.")
	return engagement


def find_match(session: Session, raw_code: str) -> Match:
	match = session.query(Match).filter_by(raw_code=raw_code).first()
	if match is None:
		raise ValueError(f"Match '{raw_code}' introuvable. As-tu bien charge le calendrier avant ?")
	return match


def find_match_engagement(session: Session, match_id: int, engagement_id: int) -> Match_Engagement:
	me = session.query(Match_Engagement).filter_by(id_match=match_id, id_engagement=engagement_id).first()
	if me is None:
		raise ValueError("Match_Engagement introuvable - incoherence entre calendrier et stats.")
	return me


# ---------- get-or-create pour les entites qui peuvent deja exister ----------

def get_or_create_officiel(session: Session, code_federation: str, prenom: str, nom: str,
                            nationalite: str) -> Officiel:
	officiel = session.query(Officiel).filter_by(code_federation=code_federation).first()
	if officiel is None:
		officiel = Officiel(code_federation=code_federation, prenom=prenom, nom=nom, nationalite=nationalite)
		session.add(officiel)
		session.flush()
	return officiel


def get_or_create_match_officiel(session: Session, match_id: int, officiel_id: int, role: str) -> None:
	existe = (
		session.query(Match_Officiel)
		.filter_by(id_match=match_id, id_officiel=officiel_id, role=role)
		.first()
	)
	if existe is None:
		session.add(Match_Officiel(id_match=match_id, id_officiel=officiel_id, role=role))


# ---------- Chargement des informations generales du match ----------

def update_match_details(match: Match, data: dict) -> None:
	match.heure_fin = parse_time(data.get("h_E", ""))
	match.reporte = data.get("postponed") == "1"
	match.retarde = data.get("delayed") == "1"
	match.interrompu = data.get("interrupted") == "1"
	match.raison_incident = data.get("reason") or None
	match.duree_reglementaire = data.get("DurTReg") or None


def load_periodes(session: Session, match_engagement1: Match_Engagement, match_engagement2: Match_Engagement,
                   quarters: list) -> None:
	for i, q in enumerate(quarters, start=1):
		for me, prefix in ((match_engagement1, "1"), (match_engagement2, "2")):
			periode = (
				session.query(Match_Engagement_Periode)
				.filter_by(id_match_engagement=me.id, numero_periode=i)
				.first()
			)
			if periode is None:
				periode = Match_Engagement_Periode(id_match_engagement=me.id, numero_periode=i)
				session.add(periode)

			periode.score = parse_int(q[f"r{prefix}"])
			periode.time_out = parse_int(q[f"t{prefix}"])
			periode.possessions_periode = parse_int(q[f"pp{prefix}"])
			periode.temps_possessions_periode = q[f"tpp{prefix}"] or None


def load_officiels(session: Session, match: Match, data: dict) -> None:
	roles = {
		"a": "arbitre_principal",
		"a_d": "delegue",
		"a_t": "officiel_table",
		"a_g": "officiel_general",
		"a_v": "var",
		"a_c": "commissaire",
	}
	for cle, role in roles.items():
		for personne in data.get(cle, []):
			officiel = get_or_create_officiel(
				session,
				code_federation=personne["cod"],
				prenom=personne["n"],
				nom=personne["c"],
				nationalite=personne.get("nn") or None,
			)
			get_or_create_match_officiel(session, match.id, officiel.id, role)


# ---------- Chargement des apparitions individuelles ----------

def build_gk_map(data: dict, cote: str) -> dict:
	"""Associe chaque numero de bonnet (nn) a ses stats de gardienne, si elle en a."""
	return {p["nn"]: p["s"] for p in data.get(f"s{cote}_gk", [])}


def load_apparitions(session: Session, match_engagement: Match_Engagement, players: list,
                     gk_map: dict, gk_labels: list) -> None:
	for p in players:
		joueur = session.query(Joueur).filter_by(code_federation=p["cg"]).first()
		if joueur is None:
			raise ValueError(f"Joueuse '{p['cg']}' introuvable. As-tu bien charge le roster avant ?")

		apparition = (
			session.query(Apparition)
			.filter_by(id_joueur=joueur.id, id_match_engagement=match_engagement.id)
			.first()
		)
		if apparition is None:
			apparition = Apparition(id_joueur=joueur.id, id_match_engagement=match_engagement.id)
			session.add(apparition)

		s = p["s"]
		apparition.numero_bonnet = parse_int(p["nn"])
		apparition.poste = p["rc_en"] or None
		apparition.est_capitaine = p.get("cap") == "(C)"
		apparition.minutes_jouees = s[0] or None

		apparition.tirs_reussis, apparition.tirs_tentes = parse_ratio(s[1])
		apparition.pourcentage_tir = parse_percent(s[2])
		apparition.action_shots_reussis, apparition.action_shots_tentes = parse_ratio(s[3])
		apparition.tirs_pointes_reussis, apparition.tirs_pointes_tentes = parse_ratio(s[4])
		apparition.tirs_zp_reussis, apparition.tirs_zp_tentes = parse_ratio(s[5])
		apparition.tirs_6m_reussis, apparition.tirs_6m_tentes = parse_ratio(s[6])
		apparition.penalty_jeu_reussis, apparition.penalty_jeu_tentes = parse_ratio(s[7])
		apparition.tirs_contre_attaque_reussis, apparition.tirs_contre_attaque_tentes = parse_ratio(s[8])
		apparition.penalty_shootout_reussis, apparition.penalty_shootout_tentes = parse_ratio(s[9])

		apparition.passes_decisives = parse_int(s[10])
		apparition.fautes_offensive = parse_int(s[11])
		apparition.interceptions = parse_int(s[12])
		apparition.contres = parse_int(s[13])
		apparition.sprint_engagement_gagne, apparition.sprint_engagement_total = parse_ratio(s[14])
		apparition.exclusion_center = parse_int(s[15])
		apparition.exclusion_field = parse_int(s[16])
		apparition.double_exclusion = parse_int(s[17])
		apparition.penalty_foul = parse_int(s[18])
		apparition.EDA = parse_flag(s[19])
		apparition.EDAP4P = parse_flag(s[20])

		if p["nn"] in gk_map:
			apparition.raw_gk_stats = dict(zip(gk_labels, gk_map[p["nn"]]))


# ---------- Orchestration ----------

def load_stats(session: Session, data: dict, competition_id: int, categorie: str, genre: str) -> None:
	raw_code = build_raw_code(data)
	match = find_match(session, raw_code)
	update_match_details(match, data)

	engagement1 = find_engagement(session, data["s1"], categorie, genre, competition_id)
	engagement2 = find_engagement(session, data["s2"], categorie, genre, competition_id)
	me1 = find_match_engagement(session, match.id, engagement1.id)
	me2 = find_match_engagement(session, match.id, engagement2.id)

	me1.score = parse_int(data["r1"])
	me1.possessions = parse_int(data["pp1"])
	me1.temps_possessions = data["tpp1"] or None
	me1.time_out = parse_int(data["t1"])

	me2.score = parse_int(data["r2"])
	me2.possessions = parse_int(data["pp2"])
	me2.temps_possessions = data["tpp2"] or None
	me2.time_out = parse_int(data["t2"])

	load_periodes(session, me1, me2, data["q"])
	load_officiels(session, match, data)

	gk_labels = data.get("s_gk_en", [])
	load_apparitions(session, me1, data.get("s1_s", []), build_gk_map(data, "1"), gk_labels)
	load_apparitions(session, me2, data.get("s2_s", []), build_gk_map(data, "2"), gk_labels)

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

		load_stats(session, data, competition.id, args.categorie, args.genre)

	print("Stats chargees.")