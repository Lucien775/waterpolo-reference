from __future__ import annotations

from datetime import date, time
from typing import Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Equipe(Base):
	__tablename__ = "Equipe"

	id: Mapped[int] = mapped_column(primary_key=True)
	code: Mapped[str] = mapped_column(String(5)) 
	nom_pays: Mapped[Optional[str]] = mapped_column(String(100))
	categorie: Mapped[Optional[str]] = mapped_column(String(20))
	genre: Mapped[Optional[str]] = mapped_column(String(10))

	engagements: Mapped[list["Engagement"]] = relationship(back_populates="equipe")

	__table_args__ = (UniqueConstraint("code", "categorie", "genre"),)


class Joueur(Base):
	__tablename__ = "Joueur"

	id: Mapped[int] = mapped_column(primary_key=True)
	code_federation: Mapped[str] = mapped_column(String(20), unique=True)
	prenom: Mapped[Optional[str]] = mapped_column(String(100))
	nom: Mapped[Optional[str]] = mapped_column(String(100))
	date_naissance: Mapped[Optional[date]] = mapped_column()
	nationalite: Mapped[Optional[str]] = mapped_column(String(5))
	taille_cm: Mapped[Optional[int]] = mapped_column()
	poids_kg: Mapped[Optional[int]] = mapped_column()
	main_dominante: Mapped[Optional[str]] = mapped_column(String(1))

	rosters: Mapped[list["Roster"]] = relationship(back_populates="joueur")
	apparitions: Mapped[list["Apparition"]] = relationship(back_populates="joueur")


class Officiel(Base):
	__tablename__ = "Officiel"

	id: Mapped[int] = mapped_column(primary_key=True)
	code_federation: Mapped[str] = mapped_column(String(20), unique=True)
	prenom: Mapped[Optional[str]] = mapped_column(String(100))
	nom: Mapped[Optional[str]] = mapped_column(String(100))
	nationalite: Mapped[Optional[str]] = mapped_column(String(5))

	matchs_officies: Mapped[list["Match_Officiel"]] = relationship(back_populates="officiel")


class Personnel_Technique(Base):
	__tablename__ = "Personnel_Technique"

	id: Mapped[int] = mapped_column(primary_key=True)
	code_federation: Mapped[str] = mapped_column(String(20), unique=True)
	prenom: Mapped[Optional[str]] = mapped_column(String(100))
	nom: Mapped[Optional[str]] = mapped_column(String(100))
	nationalite: Mapped[Optional[str]] = mapped_column(String(5))
	date_naissance: Mapped[Optional[date]] = mapped_column()

	engagements_personnel: Mapped[list["Engagement_Personnel"]] = relationship(back_populates="personnel")


class Competition(Base):
	__tablename__ = "Competition"

	id: Mapped[int] = mapped_column(primary_key=True)
	nom: Mapped[Optional[str]] = mapped_column(String(150))
	sport_code: Mapped[Optional[str]] = mapped_column(String(10))
	lieu: Mapped[Optional[str]] = mapped_column(String(150))
	date_debut: Mapped[Optional[date]] = mapped_column()
	date_fin: Mapped[Optional[date]] = mapped_column()
	source_slug: Mapped[Optional[str]] = mapped_column(String(100), unique = True)

	engagements: Mapped[list["Engagement"]] = relationship(back_populates="competition")
	phases: Mapped[list["Phase"]] = relationship(back_populates="competition")


class Engagement(Base):
	__tablename__ = "Engagement"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_equipe: Mapped[int] = mapped_column(ForeignKey("Equipe.id"))
	id_competition: Mapped[int] = mapped_column(ForeignKey("Competition.id"))

	equipe: Mapped["Equipe"] = relationship(back_populates="engagements")
	competition: Mapped["Competition"] = relationship(back_populates="engagements")
	engagements_phase: Mapped[list["Engagement_Phase"]] = relationship(back_populates="engagement")
	rosters: Mapped[list["Roster"]] = relationship(back_populates="engagement")
	engagements_personnel: Mapped[list["Engagement_Personnel"]] = relationship(back_populates="engagement")
	matchs_engagements: Mapped[list["Match_Engagement"]] = relationship(back_populates="engagement")

	__table_args__ = (UniqueConstraint("id_equipe", "id_competition"),)


class Phase(Base):
	__tablename__ = "Phase"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_competition: Mapped[int] = mapped_column(ForeignKey("Competition.id"))
	nom: Mapped[Optional[str]] = mapped_column(String(100))
	ordre: Mapped[Optional[int]] = mapped_column()
	raw_code: Mapped[Optional[str]] = mapped_column(String(20))

	competition: Mapped["Competition"] = relationship(back_populates="phases")
	engagements_phase: Mapped[list["Engagement_Phase"]] = relationship(back_populates="phase")
	matchs: Mapped[list["Match"]] = relationship(back_populates="phase")

	__table_args__ = (UniqueConstraint("raw_code", "id_competition"),)


class Engagement_Phase(Base):
	__tablename__ = "Engagement_Phase"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_engagement: Mapped[int] = mapped_column(ForeignKey("Engagement.id"))
	id_phase: Mapped[int] = mapped_column(ForeignKey("Phase.id"))
	groupe: Mapped[Optional[str]] = mapped_column(String(10))

	engagement: Mapped["Engagement"] = relationship(back_populates="engagements_phase")
	phase: Mapped["Phase"] = relationship(back_populates="engagements_phase")

	__table_args__ = (UniqueConstraint("id_engagement", "id_phase"),)


class Roster(Base):
	__tablename__ = "Roster"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_joueur: Mapped[int] = mapped_column(ForeignKey("Joueur.id"))
	id_engagement: Mapped[int] = mapped_column(ForeignKey("Engagement.id"))
	numero_bonnet: Mapped[Optional[int]] = mapped_column()
	poste: Mapped[Optional[str]] = mapped_column(String(25))
	est_capitaine: Mapped[Optional[bool]] = mapped_column()

	joueur: Mapped["Joueur"] = relationship(back_populates="rosters")
	engagement: Mapped["Engagement"] = relationship(back_populates="rosters")

	__table_args__ = (UniqueConstraint("id_joueur", "id_engagement"),)


class Engagement_Personnel(Base):
	__tablename__ = "Engagement_Personnel"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_engagement: Mapped[int] = mapped_column(ForeignKey("Engagement.id"))
	id_personnel: Mapped[int] = mapped_column(ForeignKey("Personnel_Technique.id"))
	role_code: Mapped[Optional[str]] = mapped_column(String(10))
	role_label: Mapped[Optional[str]] = mapped_column(String(100))

	engagement: Mapped["Engagement"] = relationship(back_populates="engagements_personnel")
	personnel: Mapped["Personnel_Technique"] = relationship(back_populates="engagements_personnel")

	__table_args__ = (UniqueConstraint("id_personnel", "id_engagement"),)


class Match(Base):
	__tablename__ = "Match"

	id: Mapped[int] = mapped_column(primary_key=True)
	date: Mapped[Optional[date]] = mapped_column()
	heure_debut: Mapped[Optional[time]] = mapped_column()
	heure_fin: Mapped[Optional[time]] = mapped_column()
	lieu: Mapped[Optional[str]] = mapped_column(String(150))
	id_phase: Mapped[int] = mapped_column(ForeignKey("Phase.id"))
	raw_code: Mapped[Optional[str]] = mapped_column(String(30), unique=True)
	statut: Mapped[Optional[str]] = mapped_column(String(20))
	reporte: Mapped[Optional[bool]] = mapped_column()
	retarde: Mapped[Optional[bool]] = mapped_column()
	interrompu: Mapped[Optional[bool]] = mapped_column()
	raison_incident: Mapped[Optional[str]] = mapped_column(String(200))
	duree_reglementaire: Mapped[Optional[str]] = mapped_column(String(10))

	phase: Mapped["Phase"] = relationship(back_populates="matchs")
	officiels: Mapped[list["Match_Officiel"]] = relationship(back_populates="match")
	engagements: Mapped[list["Match_Engagement"]] = relationship(back_populates="match")


class Match_Officiel(Base):
	__tablename__ = "Match_Officiel"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_match: Mapped[int] = mapped_column(ForeignKey("Match.id"))
	id_officiel: Mapped[int] = mapped_column(ForeignKey("Officiel.id"))
	role: Mapped[Optional[str]] = mapped_column(String(30))

	match: Mapped["Match"] = relationship(back_populates="officiels")
	officiel: Mapped["Officiel"] = relationship(back_populates="matchs_officies")

	__table_args__ = (UniqueConstraint("id_officiel", "id_match"),)


class Match_Engagement(Base):
	__tablename__ = "Match_Engagement"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_match: Mapped[int] = mapped_column(ForeignKey("Match.id"))
	id_engagement: Mapped[int] = mapped_column(ForeignKey("Engagement.id"))
	cote: Mapped[Optional[str]] = mapped_column(String(10))
	score: Mapped[Optional[int]] = mapped_column()
	possessions: Mapped[Optional[int]] = mapped_column()
	temps_possessions: Mapped[Optional[str]] = mapped_column(String(10))
	time_out: Mapped[Optional[int]] = mapped_column()

	match: Mapped["Match"] = relationship(back_populates="engagements")
	engagement: Mapped["Engagement"] = relationship(back_populates="matchs_engagements")
	periodes: Mapped[list["Match_Engagement_Periode"]] = relationship(back_populates="match_engagement")
	apparitions: Mapped[list["Apparition"]] = relationship(back_populates="match_engagement")

	__table_args__ = (UniqueConstraint("id_match", "id_engagement"),)


class Match_Engagement_Periode(Base):
	__tablename__ = "Match_Engagement_Periode"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_match_engagement: Mapped[int] = mapped_column(ForeignKey("Match_Engagement.id"))
	numero_periode: Mapped[Optional[int]] = mapped_column()
	score: Mapped[Optional[int]] = mapped_column()
	possessions_periode: Mapped[Optional[int]] = mapped_column()
	temps_possessions_periode: Mapped[Optional[str]] = mapped_column(String(10))
	time_out: Mapped[Optional[int]] = mapped_column()

	match_engagement: Mapped["Match_Engagement"] = relationship(back_populates="periodes")

	__table_args__ = (UniqueConstraint("id_match_engagement", "numero_periode"),)


class Apparition(Base):
	__tablename__ = "Apparition"

	id: Mapped[int] = mapped_column(primary_key=True)
	id_joueur: Mapped[int] = mapped_column(ForeignKey("Joueur.id"))
	id_match_engagement: Mapped[int] = mapped_column(ForeignKey("Match_Engagement.id"))
	numero_bonnet: Mapped[Optional[int]] = mapped_column()
	poste: Mapped[Optional[str]] = mapped_column(String(5))
	est_capitaine: Mapped[Optional[bool]] = mapped_column()
	minutes_jouees: Mapped[Optional[str]] = mapped_column(String(10))
	tirs_tentes: Mapped[Optional[int]] = mapped_column()
	tirs_reussis: Mapped[Optional[int]] = mapped_column()
	pourcentage_tir: Mapped[Optional[float]] = mapped_column()
	action_shots_tentes: Mapped[Optional[int]] = mapped_column()
	action_shots_reussis: Mapped[Optional[int]] = mapped_column()
	tirs_pointes_tentes: Mapped[Optional[int]] = mapped_column()
	tirs_pointes_reussis: Mapped[Optional[int]] = mapped_column()
	tirs_zp_tentes: Mapped[Optional[int]] = mapped_column()
	tirs_zp_reussis: Mapped[Optional[int]] = mapped_column()
	tirs_6m_tentes: Mapped[Optional[int]] = mapped_column()
	tirs_6m_reussis: Mapped[Optional[int]] = mapped_column()
	penalty_jeu_tentes: Mapped[Optional[int]] = mapped_column()
	penalty_jeu_reussis: Mapped[Optional[int]] = mapped_column()
	tirs_contre_attaque_tentes: Mapped[Optional[int]] = mapped_column()
	tirs_contre_attaque_reussis: Mapped[Optional[int]] = mapped_column()
	penalty_shootout_tentes: Mapped[Optional[int]] = mapped_column()
	penalty_shootout_reussis: Mapped[Optional[int]] = mapped_column()
	passes_decisives: Mapped[Optional[int]] = mapped_column()
	fautes_offensive: Mapped[Optional[int]] = mapped_column()
	interceptions: Mapped[Optional[int]] = mapped_column()
	contres: Mapped[Optional[int]] = mapped_column()
	sprint_engagement_gagne: Mapped[Optional[int]] = mapped_column()
	sprint_engagement_total: Mapped[Optional[int]] = mapped_column()
	exclusion_center: Mapped[Optional[int]] = mapped_column()
	exclusion_field: Mapped[Optional[int]] = mapped_column()
	double_exclusion: Mapped[Optional[int]] = mapped_column()
	penalty_foul: Mapped[Optional[int]] = mapped_column()
	EDA: Mapped[Optional[bool]] = mapped_column()
	EDAP4P: Mapped[Optional[bool]] = mapped_column()
	raw_gk_stats: Mapped[Optional[dict]] = mapped_column(JSONB)

	joueur: Mapped["Joueur"] = relationship(back_populates="apparitions")
	match_engagement: Mapped["Match_Engagement"] = relationship(back_populates="apparitions")

	__table_args__ = (UniqueConstraint("id_joueur", "id_match_engagement"),)