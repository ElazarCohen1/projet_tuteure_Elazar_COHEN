# projet_tuteure_Elazar_COHEN


---

## Prérequis

- Python 3.11+
- PostgreSQL avec l'extension [pgvector](https://github.com/pgvector/pgvector) installée
- [Ollama](https://ollama.com/) installé et le modèle Mistral téléchargé
- Un bot Discord créé sur le [portail développeur Discord](https://discord.com/developers/applications)

---

## Installation

### 1. Cloner le projet

```bash
git clone git@github.com:ElazarCohen1/projet_tuteure_Elazar_COHEN.git
cd projet_tuteure_Elazar_COHEN
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
DB_PASSWORD=ton_mot_de_passe_postgres
TOKEN=ton_token_discord
```

```bash
psql -U elazar -d tuteure -f bdd/dump.sql
```

Activer l'extension pgvector si ce n'est pas déjà fait :

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Télécharger le modèle Mistral via Ollama

```bash
ollama pull mistral
```

## Insertion des données

Placer le fichier `recipes_data.csv` dans le dossier `bdd/`, puis lancer :

```bash
python3 -m bdd.main
```

Cela normalise et insère les recettes par batch de 10 000, avec génération des embeddings.

---

---

## Lancer le bot Discord

```bash
python3 -m bot.bot
```

---

# Organisation

## À faire

### Semaine 1 : 12 février - 19 février
- Organisation et clarification du travail demandé
- Recherche des données
- Création du schéma relationnel et création du dump de la base de données relationnelle

### Semaine 2 : 19 février - 26 février
- Création du bot Discord
- Automatisation pour rentrer les données dans la base et vérification des données
- Automatisation de la recherche des données par index dans la base de données
- Téléchargement du LLM local

### Semaine 3 : 26 février - 4 mars
- Joindre les 3 parties (données, LLM et Bot)
- Lancement du bot pour avoir des feedbacks
- Possiblement finir si une partie n’est pas terminée

## Fait

### Semaine 1 : 12 février - 19 février
- Organisation et clarification du travail demandé  
- Recherche des données
- Création du schéma relationnel et création du dump de la base de données relationnelle

### Semaine 2,3,4 : 19 février - 5 mars
- Création du bot Discord
- normalisation des données 

### Semaine 5,6,7 : 5 mars - 26 mars
- insertion des données normaliser dans la base
- transformer les données en embeddings et création d'une nouvelle table recipe_embeddings
- utilisation et comprehension de pgvector et de la recherche par cosine similarité


### semaine 6,7 : 26 mars - 9 avril
- installation du llm(ollama mistral) en local 
- joindre les 3 parties (données , LLM et Bot)
- création de la commande /recette pour discord en appelant le programme final

### semaine 8,9 : 9 avril - 23 avril 
- lancement du bot dans le groupe discord privée entre amis pour avoir des feedbacks 
- amélioration drastique de la performance de l'insertion dans la base de donnée (10 000 recettes en 2h 30 -> 10 000 recettes en 2 min)
- amelioration de la normalisation des données (pas tout d'un coup mais petit a petit)




