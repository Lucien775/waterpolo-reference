"""
Créer une nouvelle compétition dans la base de données.
Usage:
	python create_competition.py 
		--nom "World Championship U16W 2026" 
		--sport-code ASF
		--lieu Zagreb
		--date-debut 25/07/2026
		--date-fin 31/07/2026
		--source-slug CroatiaU16W
"""
import argparse
from datetime import datetime
from sqlalchemy.orm import Session
from data.database import engine
from data.model import Competition


def create_competition(session: Session, nom: str, sport_code: str, lieu: str, source_slug: str,
                        date_debut: datetime, date_fin: datetime) -> Competition:
	competition = session.query(Competition).filter_by(source_slug=source_slug).first()
	if competition is not None:
		raise ValueError(f"Une competition avec le slug '{source_slug}' existe deja")

	competition = Competition(
		nom=nom, sport_code=sport_code, lieu=lieu,
		date_debut=date_debut, date_fin=date_fin, source_slug=source_slug,
	)
	session.add(competition)
	session.commit()
	return competition


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--nom", type=str, required=True)
	parser.add_argument("--sport-code", type=str, required=True)
	parser.add_argument("--lieu", type=str, required=True)
	parser.add_argument("--date-debut", type=str, required=True)
	parser.add_argument("--date-fin", type=str, required=True)
	parser.add_argument("--source-slug", type=str, required=True)
	args = parser.parse_args()

	date_debut = datetime.strptime(args.date_debut, "%d/%m/%Y").date()
	date_fin = datetime.strptime(args.date_fin, "%d/%m/%Y").date()

	with Session(engine) as session:
		competition = create_competition(
			session, args.nom, args.sport_code, args.lieu, args.source_slug, date_debut, date_fin
		)
		print(f"Competition creee avec id={competition.id}")