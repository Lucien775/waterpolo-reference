# Water Polo Reference

> Une base de données statistiques pour le water polo international, inspirée de sites comme Basketball-Reference — pensée pour être étendue à plusieurs compétitions au fil du temps.

Le projet part d'un constat simple : contrairement au basket, au football ou au baseball, le water polo n'a pas d'équivalent à Basketball-Reference — un endroit centralisé pour consulter l'historique des compétitions, comparer des équipes et des joueuses, et explorer des statistiques détaillées match par match.

Ce dépôt contient le pipeline complet de collecte et de structuration de ces données : du scraping des résultats officiels jusqu'à une base relationnelle interrogeable, conçue pour tenir sur plusieurs compétitions et plusieurs années sans devoir être repensée à chaque fois.

**État actuel** : le pipeline de données (scraping → base PostgreSQL) est fonctionnel pour la Coupe du Monde U16 Femmes 2026. La partie visualisation/site web n'est pas encore développée.

---

## Ce que ce projet illustre

- **Rétro-ingénierie d'une API non documentée** : identification et reproduction du format d'export JSON utilisé par le prestataire de chronométrage officiel (Microplus), sans documentation publique.
- **Modélisation relationnelle réfléchie** : distinction entre entités stables dans le temps (joueuse, équipe) et entités ponctuelles (participation à une compétition, match), pour permettre un suivi de carrière cohérent malgré des effectifs qui changent chaque édition.
- **Schéma versionné et reproductible** : le schéma de base vit dans un fichier DBML lisible en texte, à partir duquel le SQL est généré automatiquement — aucune modification manuelle de la structure de la base.
- **Pipeline de chargement idempotent** : chaque script peut être relancé sans dupliquer ou corrompre les données déjà présentes (pattern *get-or-create* systématique).
- **Environnement reproductible** : base de données conteneurisée (Docker), configuration séparée du code (`.env`), schéma versionné indépendamment du code applicatif.

---

## Architecture du pipeline

```
Site Microplus (JSON)
        │
        ▼
   scraping/          ──►  cache/ (JSON bruts, un fichier par jour/match)
        │
        ▼
   loading/
   ├── create_competition.py   (metadata de la competition)
   ├── load_roster.py          (equipes, staff technique, joueuses)
   ├── load_schedule.py        (calendrier, matchs)
   └── load_stats.py           (stats detaillees par match, arbitrage)
        │
        ▼
   PostgreSQL (15 tables, cf. db/schema.dbml)
```

Le fichier `orchestrate.py` enchaîne l'ensemble de ces étapes dans l'ordre requis par les dépendances (une équipe doit exister avant qu'on lui associe un match, un match avant qu'on lui associe des stats détaillées, etc.), avec une tolérance aux erreurs différenciée : un fichier de match corrompu est signalé et ignoré sans interrompre le chargement des autres, alors qu'une erreur sur une étape fondatrice (création de la compétition, chargement du roster) arrête le pipeline.

---

## Modèle de données

Quelques choix de conception qui ont guidé le schéma (détail complet dans `db/schema.dbml`) :

- **`Equipe` ≠ pays seul** — une équipe est définie par la combinaison pays + catégorie d'âge + genre (ex: *Grèce U16 Femmes*), pour permettre des comparaisons cohérentes entre éditions successives d'une même sélection.
- **`Engagement`** fait le lien entre une équipe stable et une compétition précise — c'est cette table qui porte tout ce qui est propre à une participation donnée (effectif, staff, poule).
- **Trois niveaux de composition d'équipe**, chacun avec son propre rôle : `Roster` (l'effectif de 15 déclaré pour le tournoi), `Match_Engagement` (les 2 équipes d'un match donné, avec le score), `Apparition` (le détail statistique d'une joueuse sur un match précis).
- **`raw_code`** sur `Match` conserve l'identifiant Microplus d'origine, ce qui permet de reconstruire l'URL source à tout moment sans avoir à tout re-scraper.

```
Equipe ──┐
         ▼
    Engagement ── Engagement_Phase ── Phase ── Competition
         │                                        │
         ▼                                        ▼
      Roster                                    Match ── Match_Officiel ── Officiel
         │                                        │
      Joueur                              Match_Engagement ── Match_Engagement_Periode
                                                    │
                                              Apparition
```

---

## Stack technique

| Composant | Choix |
|---|---|
| Langage | Python 3 |
| Base de données | PostgreSQL (conteneurisé via Docker Compose) |
| ORM | SQLAlchemy 2.0 (syntaxe déclarative `Mapped`) |
| Schéma de base | DBML → SQL généré (`@dbml/cli`) |
| Scraping | `requests` |

---

## Structure du projet

```
waterpolo-reference/
├── db/
│   ├── schema.dbml          # source de verite du schema
│   └── generate_sql.sh      # regenere le SQL depuis le .dbml
├── data/
│   ├── database.py          # engine SQLAlchemy
│   ├── models.py            # modeles ORM
│   ├── scraping/            # recuperation des JSON source
│   └── loading/             # chargement en base
├── cache/                   # JSON bruts scrapes (non versionne)
├── docker-compose.yml
├── orchestrate.py           # pipeline complet, bout en bout
└── requirements.txt
```

---

## Installation et utilisation

### Prérequis
- Docker
- Python 3.10+
- Node.js (pour `@dbml/cli`)

### Mise en place

```bash
# Dependances Python
pip install -r requirements.txt

# Outil de generation SQL depuis le schema DBML
npm install -g @dbml/cli

# Copier et completer le fichier d'environnement
cp .env.example .env

# Lancer la base et appliquer le schema
docker compose up -d
./db/generate_sql.sh db/schema.dbml
```

### Lancer le pipeline complet pour une compétition

```bash
python orchestrate.py \
  --source-slug CroatiaU16W --categorie U16 --genre Femme \
  --nom "World Championship U16W 2026" --sport-code ASF \
  --lieu Zagreb --date-debut 25/07/2026 --date-fin 31/07/2026
```

---

## Pistes d'évolution

- [ ] Généraliser le scraper à n'importe quelle compétition (actuellement paramétré en dur pour une seule édition)
- [ ] Migrations de schéma (Alembic) plutôt que recréation complète à chaque changement
- [ ] Couche de visualisation (site web ou tableaux de bord) exploitant les données déjà structurées
- [ ] Extension à d'autres compétitions et catégories d'âge pour permettre des comparaisons historiques

---

## Licence

MIT — voir [LICENSE](LICENSE).