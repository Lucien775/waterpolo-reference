-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2026-08-22T14:48:34.252Z

CREATE TABLE "Equipe" (
  "id" integer PRIMARY KEY,
  "code" varchar(5) UNIQUE,
  "nom_pays" varchar(100),
  "categorie" varchar(20),
  "genre" varchar(10)
);

CREATE TABLE "Joueur" (
  "id" integer PRIMARY KEY,
  "code_federation" varchar(20) UNIQUE,
  "prenom" varchar(100),
  "nom" varchar(100),
  "date_naissance" date,
  "nationalite" varchar(5),
  "taille_cm" integer,
  "poids_kg" integer,
  "main_dominante" varchar(1)
);

CREATE TABLE "Officiel" (
  "id" integer PRIMARY KEY,
  "code_federation" varchar(20) UNIQUE,
  "prenom" varchar(100),
  "nom" varchar(100),
  "nationalite" varchar(5)
);

CREATE TABLE "Personnel_Technique" (
  "id" integer PRIMARY KEY,
  "code_federation" varchar(20) UNIQUE,
  "prenom" varchar(100),
  "nom" varchar(100),
  "nationalite" varchar(5),
  "date_naissance" date
);

CREATE TABLE "Competition" (
  "id" integer PRIMARY KEY,
  "nom" varchar(150),
  "sport_code" varchar(10),
  "lieu" varchar(150),
  "date_debut" date,
  "date_fin" date,
  "source_slug" varchar(100)
);

CREATE TABLE "Engagement" (
  "id" integer PRIMARY KEY,
  "id_equipe" integer,
  "id_competition" integer
);

CREATE TABLE "Phase" (
  "id" integer PRIMARY KEY,
  "id_competition" integer,
  "nom" varchar(100),
  "ordre" integer,
  "raw_code" varchar(20)
);

CREATE TABLE "Engagement_Phase" (
  "id" integer PRIMARY KEY,
  "id_engagement" integer,
  "id_phase" integer,
  "groupe" varchar(10)
);

CREATE TABLE "Roster" (
  "id" integer PRIMARY KEY,
  "id_joueur" integer,
  "id_engagement" integer,
  "numero_bonnet" integer,
  "poste" varchar(5),
  "est_capitaine" boolean
);

CREATE TABLE "Engagement_Personnel" (
  "id" integer PRIMARY KEY,
  "id_engagement" integer,
  "id_personnel" integer,
  "role_code" varchar(10),
  "role_label" varchar(100)
);

CREATE TABLE "Match" (
  "id" integer PRIMARY KEY,
  "date" date,
  "heure_debut" time,
  "heure_fin" time,
  "lieu" varchar(150),
  "id_phase" integer,
  "raw_code" varchar(30) UNIQUE,
  "statut" varchar(20),
  "reporte" boolean,
  "retarde" boolean,
  "interrompu" boolean,
  "raison_incident" varchar(200),
  "duree_reglementaire" varchar(10)
);

CREATE TABLE "Match_Officiel" (
  "id" integer PRIMARY KEY,
  "id_match" integer,
  "id_officiel" integer,
  "role" varchar(30)
);

CREATE TABLE "Match_Engagement" (
  "id" integer PRIMARY KEY,
  "id_match" integer,
  "id_engagement" integer,
  "cote" varchar(10),
  "score" integer,
  "possessions" integer,
  "temps_possession" varchar(10),
  "time_out" integer
);

CREATE TABLE "Match_Engagement_Periode" (
  "id" integer PRIMARY KEY,
  "id_match_engagement" integer,
  "numero_periode" integer,
  "possessions_periode" integer,
  "temps_possession_periode" varchar(10),
  "time_out" integer,
  "score" integer
);

CREATE TABLE "Apparition" (
  "id" integer PRIMARY KEY,
  "id_joueur" integer,
  "id_match_engagement" integer,
  "numero_bonnet" integer,
  "poste" varchar(5),
  "est_capitaine" boolean,
  "minutes_jouees" varchar(10),
  "tirs_tentes" integer,
  "tirs_reussis" integer,
  "pourcentage_tir" decimal,
  "action_shots_tentes" integer,
  "action_shots_reussis" integer,
  "tirs_pointes_tentes" integer,
  "tirs_pointes_reussis" integer,
  "tirs_zp_tentes" integer,
  "tirs_zp_reussis" integer,
  "tirs_6m_tentes" integer,
  "tirs_6m_reussis" integer,
  "penalty_jeu_tentes" integer,
  "penalty_jeu_reussis" integer,
  "tirs_contre_attaque_tentes" integer,
  "tirs_contre_attaque_reussis" integer,
  "penalty_shootout_tentes" integer,
  "penalty_shootout_reussis" integer,
  "passes_decisives" integer,
  "fautes_offensive" integer,
  "interceptions" integer,
  "contres" integer,
  "sprint_engagement_gagne" integer,
  "sprint_engagement_total" integer,
  "exclusion_center" integer,
  "exclusion_field" integer,
  "double_exclusion" integer,
  "penalty_foul" integer,
  "EDA" boolean,
  "EDAP4P" boolean,
  "raw_gk_stats" json
);

CREATE UNIQUE INDEX ON "Equipe" ("code", "categorie", "genre");

CREATE UNIQUE INDEX ON "Engagement" ("id_equipe", "id_competition");

CREATE UNIQUE INDEX ON "Engagement_Phase" ("id_engagement", "id_phase");

CREATE UNIQUE INDEX ON "Roster" ("id_joueur", "id_engagement");

CREATE UNIQUE INDEX ON "Match_Engagement" ("id_match", "id_engagement");

CREATE UNIQUE INDEX ON "Match_Engagement_Periode" ("id_match_engagement", "numero_periode");

COMMENT ON COLUMN "Equipe"."code" IS 'Code pays/selection, ex: GRE, MEX';

COMMENT ON COLUMN "Equipe"."categorie" IS 'ex: U16, U18, Senior';

COMMENT ON COLUMN "Equipe"."genre" IS 'Homme / Femme';

COMMENT ON COLUMN "Joueur"."code_federation" IS 'Champ cg du JSON, identifiant stable inter-competitions';

COMMENT ON COLUMN "Joueur"."main_dominante" IS 'm dans TeamRoster - R pour droitier, L pour gaucher';

COMMENT ON COLUMN "Personnel_Technique"."code_federation" IS 'Cod dans Staf[]';

COMMENT ON COLUMN "Competition"."nom" IS 'ex: World Championship U16W Croatia 2026';

COMMENT ON COLUMN "Competition"."sport_code" IS 'Category.Cod, ex: ASF';

COMMENT ON COLUMN "Competition"."source_slug" IS 'ex: CroatiaU16W, utilise pour reconstruire les URLs Microplus';

COMMENT ON COLUMN "Phase"."nom" IS 'ex: Qualification, Poules principales, Quarterfinal, Final';

COMMENT ON COLUMN "Phase"."ordre" IS 'Ordre chronologique dans la competition';

COMMENT ON COLUMN "Phase"."raw_code" IS 'Round.Cod brut, ex: A01, A06, A08';

COMMENT ON COLUMN "Engagement_Phase"."groupe" IS 'Poule au sein de cette phase, ex: A - peut differer d''une phase a l''autre pour la meme equipe';

COMMENT ON COLUMN "Roster"."poste" IS 'rc_en: GK, CF, D, W, CB, AR...';

COMMENT ON COLUMN "Roster"."est_capitaine" IS 'cap dans TeamRoster - designee pour toute la competition, pas rejouee par match';

COMMENT ON COLUMN "Engagement_Personnel"."role_code" IS 'RuoCod: D01 head coach, D03 assistant coach, D04 medecin, D08 manager, D11 officiel...';

COMMENT ON COLUMN "Engagement_Personnel"."role_label" IS 'RuoDescrEng';

COMMENT ON COLUMN "Match"."raw_code" IS 'Concatenation c0+c1+c2+c3+c4+c5, sert a reconstruire l''URL STA_*';

COMMENT ON COLUMN "Match"."statut" IS 'sch_st: FINISHED, SCHEDULED...';

COMMENT ON COLUMN "Match"."reporte" IS 'postponed';

COMMENT ON COLUMN "Match"."retarde" IS 'delayed';

COMMENT ON COLUMN "Match"."interrompu" IS 'interrupted';

COMMENT ON COLUMN "Match"."raison_incident" IS 'reason';

COMMENT ON COLUMN "Match"."duree_reglementaire" IS 'DurTReg';

COMMENT ON COLUMN "Match_Officiel"."role" IS 'arbitre_principal (a), delegue (a_d), officiel_table (a_t)...';

COMMENT ON COLUMN "Match_Engagement"."cote" IS '''equipe1'' ou ''equipe2'', pour reconstituer s1/s2 d''origine';

COMMENT ON COLUMN "Match_Engagement"."score" IS 'r1 ou r2 - score final de cette equipe';

COMMENT ON COLUMN "Match_Engagement"."possessions" IS 'pp1 ou pp2 - nombre de possessions';

COMMENT ON COLUMN "Match_Engagement"."temps_possession" IS 'tpp1 ou tpp2 - temps de possession cumule';

COMMENT ON COLUMN "Match_Engagement"."time_out" IS 't1 ou t2 nombre de temps morts pris par l''équipe';

COMMENT ON COLUMN "Match_Engagement_Periode"."numero_periode" IS '1 a 4, champ q[]';

COMMENT ON COLUMN "Match_Engagement_Periode"."possessions_periode" IS 'pp1 ou pp2 du quart';

COMMENT ON COLUMN "Match_Engagement_Periode"."temps_possession_periode" IS 'tpp1 ou tpp2 du quart';

COMMENT ON COLUMN "Match_Engagement_Periode"."time_out" IS 't1 ou t2 du quart';

COMMENT ON COLUMN "Match_Engagement_Periode"."score" IS 'r1 ou r2 du quart';

COMMENT ON COLUMN "Apparition"."numero_bonnet" IS 'nn - peut differer du Roster en theorie, on le fige ici pour ce match';

COMMENT ON COLUMN "Apparition"."poste" IS 'rc_en pour ce match precis';

COMMENT ON COLUMN "Apparition"."est_capitaine" IS 'cap = (C)';

COMMENT ON COLUMN "Apparition"."minutes_jouees" IS 's[0] MIN_, format mm:ss';

COMMENT ON COLUMN "Apparition"."tirs_tentes" IS 's[1] TOTAL, denominateur';

COMMENT ON COLUMN "Apparition"."tirs_reussis" IS 's[1] TOTAL, numerateur, i.e nb de but';

COMMENT ON COLUMN "Apparition"."pourcentage_tir" IS 's[2] %';

COMMENT ON COLUMN "Apparition"."action_shots_tentes" IS 's[3] A, denominateur';

COMMENT ON COLUMN "Apparition"."action_shots_reussis" IS 's[3] A, numerateur';

COMMENT ON COLUMN "Apparition"."tirs_pointes_tentes" IS 's[4] C - tirs en pointe, denominateur';

COMMENT ON COLUMN "Apparition"."tirs_pointes_reussis" IS 's[4] C, numerateur';

COMMENT ON COLUMN "Apparition"."tirs_zp_tentes" IS 's[5] X - tirs en zone plus, denominateur';

COMMENT ON COLUMN "Apparition"."tirs_zp_reussis" IS 's[5] X, numerateur';

COMMENT ON COLUMN "Apparition"."tirs_6m_tentes" IS 's[6] 6M - tirs a 6 metres, denominateur';

COMMENT ON COLUMN "Apparition"."tirs_6m_reussis" IS 's[6] 6M, numerateur';

COMMENT ON COLUMN "Apparition"."penalty_jeu_tentes" IS 's[7] PS - penalty dans le jeu, denominateur';

COMMENT ON COLUMN "Apparition"."penalty_jeu_reussis" IS 's[7] PS, numerateur';

COMMENT ON COLUMN "Apparition"."tirs_contre_attaque_tentes" IS 's[8] CA, denominateur';

COMMENT ON COLUMN "Apparition"."tirs_contre_attaque_reussis" IS 's[8] CA, numerateur';

COMMENT ON COLUMN "Apparition"."penalty_shootout_tentes" IS 's[9] PSO_ - penalty tir au but, denominateur';

COMMENT ON COLUMN "Apparition"."penalty_shootout_reussis" IS 's[9] PSO_, numerateur';

COMMENT ON COLUMN "Apparition"."passes_decisives" IS 's[10] AS';

COMMENT ON COLUMN "Apparition"."fautes_offensive" IS 's[11] TF - contre-faute';

COMMENT ON COLUMN "Apparition"."interceptions" IS 's[12] ST';

COMMENT ON COLUMN "Apparition"."contres" IS 's[13] BL_';

COMMENT ON COLUMN "Apparition"."sprint_engagement_gagne" IS 's[14] SP_, numérateur';

COMMENT ON COLUMN "Apparition"."sprint_engagement_total" IS 's[14] SP_, dénominateur';

COMMENT ON COLUMN "Apparition"."exclusion_center" IS 's[15] 18C, exclusion en pointe';

COMMENT ON COLUMN "Apparition"."exclusion_field" IS 's[16] 18F, exclusion dans le jeu';

COMMENT ON COLUMN "Apparition"."double_exclusion" IS 's[17] 2EX, exclusion de un joueur de chaque équipe';

COMMENT ON COLUMN "Apparition"."penalty_foul" IS 's[18] P, faute donnant un pénalty à l''équipe adverse';

COMMENT ON COLUMN "Apparition"."EDA" IS 's[19] EX, exlcut définitivement avec remplacement (S = true)';

COMMENT ON COLUMN "Apparition"."EDAP4P" IS 's[20] 4EX_';

COMMENT ON COLUMN "Apparition"."raw_gk_stats" IS 'Si gardien: tableau s_gk[] + labels s_gk_en, sinon null';

ALTER TABLE "Engagement" ADD FOREIGN KEY ("id_equipe") REFERENCES "Equipe" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Engagement" ADD FOREIGN KEY ("id_competition") REFERENCES "Competition" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Phase" ADD FOREIGN KEY ("id_competition") REFERENCES "Competition" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Engagement_Phase" ADD FOREIGN KEY ("id_engagement") REFERENCES "Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Engagement_Phase" ADD FOREIGN KEY ("id_phase") REFERENCES "Phase" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Roster" ADD FOREIGN KEY ("id_joueur") REFERENCES "Joueur" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Roster" ADD FOREIGN KEY ("id_engagement") REFERENCES "Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Engagement_Personnel" ADD FOREIGN KEY ("id_engagement") REFERENCES "Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Engagement_Personnel" ADD FOREIGN KEY ("id_personnel") REFERENCES "Personnel_Technique" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match" ADD FOREIGN KEY ("id_phase") REFERENCES "Phase" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match_Officiel" ADD FOREIGN KEY ("id_match") REFERENCES "Match" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match_Officiel" ADD FOREIGN KEY ("id_officiel") REFERENCES "Officiel" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match_Engagement" ADD FOREIGN KEY ("id_match") REFERENCES "Match" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match_Engagement" ADD FOREIGN KEY ("id_engagement") REFERENCES "Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Match_Engagement_Periode" ADD FOREIGN KEY ("id_match_engagement") REFERENCES "Match_Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Apparition" ADD FOREIGN KEY ("id_joueur") REFERENCES "Joueur" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "Apparition" ADD FOREIGN KEY ("id_match_engagement") REFERENCES "Match_Engagement" ("id") DEFERRABLE INITIALLY IMMEDIATE;
