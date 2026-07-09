# Texte de présentation — Soutenance L3
## Bot Discord de recommandation de recettes
**Durée cible : 20 minutes**

---

## PARTIE 1 — Introduction (3 min)

*[Slide titre]*

Bonjour, je m'appelle Elazar Cohen et je vais vous présenter mon projet tuteuré :
un bot Discord de recommandation de recettes.

Tout est parti d'une idée simple : aider les gens à cuisiner en fonction de leur budget.
Au départ, je voulais faire une application mobile, mais ce n'était pas dans les
compétences qu'on apprend à la fac, et ça avait déjà été fait par d'autres étudiants.

Mon professeur m'a donc orienté vers une autre approche : créer un bot pour un groupe,
qui proposerait des recettes à plusieurs personnes en même temps.
J'ai choisi Discord parce que c'est une plateforme où il est facile de créer un bot,
et que c'est naturellement une expérience de groupe.

L'idée finale est simple : un utilisateur tape une commande dans un salon Discord,
par exemple "/recette poulet pas cher", et le bot lui répond avec une recette complète,
adaptée à sa demande.

Pour faire ça, j'avais besoin de trois composants :
une base de données de recettes, un modèle de langage pour générer les réponses,
et un bot pour faire le lien avec Discord.
J'ai choisi de faire tourner le LLM en local — avec Ollama et le modèle Mistral —
pour ne pas dépendre d'une API payante et pour garder le contrôle sur le système.

---

## PARTIE 2 — Architecture technique (4 min)

*[Slide architecture globale]*

Voici comment le système fonctionne de bout en bout.

Quand un utilisateur envoie une commande, le bot Discord la reçoit.
Cette requête est transformée en vecteur numérique — ce qu'on appelle un embedding —
grâce au modèle SentenceTransformer all-MiniLM-L6-v2.

Ce vecteur est ensuite comparé à tous les vecteurs des recettes stockés dans ma base
de données PostgreSQL, grâce à l'extension pgvector.
La comparaison se fait par similarité cosinus : on cherche les recettes dont le vecteur
est le plus "proche" de la question posée.

On récupère les 5 recettes les plus pertinentes, et on les donne en contexte à Mistral,
qui génère une réponse complète avec les ingrédients et les étapes.

*[Slide schéma BDD]*

Ma base de données est organisée en cinq tables :
"recipe" pour les recettes, "ingredients" pour les ingrédients,
"recipe_ingredient" pour la relation entre les deux avec les quantités,
"steps" pour les étapes de préparation,
et "recipe_embeddings" qui stocke le vecteur de chaque recette sous forme de colonne
de type vector(384).

C'est ce pipeline qu'on appelle RAG — Retrieval-Augmented Generation :
on récupère d'abord du contexte pertinent, et on le donne au LLM pour qu'il génère
une réponse de qualité.

---

## PARTIE 3 — Le problème de performance (5 min) ← LE CŒUR

*[Slide état initial : 2h30]*

Je vais maintenant vous parler de ce qui m'a pris le plus de temps et que j'ai trouvé
le plus intéressant techniquement : le problème de performance lors de l'insertion
des données.

J'avais un fichier CSV de 9 Go avec environ 2 millions de recettes.
Pour commencer, j'ai inséré les données recette par recette,
ligne par ligne dans chaque table.

Résultat : 2h30 pour insérer seulement 10 000 recettes.
C'est catastrophique pour un dataset de 2 millions de lignes.

*[Slide les deux goulots d'étranglement]*

J'ai analysé le problème et j'ai trouvé deux coupables principaux.

Le premier : j'ouvrais une transaction à chaque insertion.
Pour 10 000 recettes avec plusieurs tables chacune, ça fait des dizaines de milliers
d'aller-retours avec la base de données. C'est extrêmement coûteux.

Le deuxième — et c'est celui qui prenait le plus de temps, environ 90 à 95% —
c'était la transformation en embeddings.
J'appelais le modèle une recette à la fois, en faisant un appel CPU pour chaque recette.
Le modèle n'est pas optimisé pour travailler sur un seul texte à la fois :
il est bien plus efficace quand on lui donne un batch entier.

*[Slide solutions appliquées]*

Première amélioration : j'ai regroupé les embeddings en batch de 1024 recettes.
Au lieu de faire 10 000 appels individuels au modèle, j'en fais une dizaine.
Ça a drastiquement réduit le temps de calcul.

Deuxième amélioration, conseillée par mon professeur :
au lieu d'insérer les données ligne par ligne avec des INSERT,
j'ai utilisé la commande COPY de PostgreSQL.
Le principe : je prépare des fichiers CSV en mémoire, un par table,
et je les envoie d'un coup à PostgreSQL.
PostgreSQL est optimisé pour ça — l'insertion se fait en quelques millisecondes
au lieu de plusieurs minutes.

*[Slide tableau comparatif]*

Résultat final :
- État initial : 2h30 pour 10 000 recettes
- Après batch des embeddings : environ 10 minutes
- Après COPY PostgreSQL : 3 à 5 minutes, dont 90% pris par les embeddings

L'insertion en base est passée de plusieurs minutes à quelques millisecondes.
Le seul vrai problème restant c'est le calcul des embeddings, qui se fait sur CPU.
Sur GPU, ce serait encore 10 à 50 fois plus rapide, mais je n'avais pas accès à
une machine avec pgvector et GPU en même temps.

---

## PARTIE 4 — Organisation du travail (3 min)

*[Slide frise chronologique]*

En termes d'organisation, j'ai travaillé en trois grandes phases.

La première phase, environ un mois, c'était tout ce qui touche aux données :
trouver le bon dataset, créer le schéma relationnel, normaliser les données brutes.
La normalisation était plus complexe que prévu : les données étaient en anglais,
avec des unités américaines comme les cups et les ounces, et mal formatées.
J'ai utilisé la bibliothèque ingredient-parser pour parser automatiquement chaque
ingrédient et en extraire le nom, la quantité et l'unité.

La deuxième phase, environ 5 semaines, c'était les embeddings et le RAG :
comprendre comment fonctionnent les embeddings, créer la table pgvector,
et connecter la recherche vectorielle au LLM.

La troisième phase, c'était l'intégration finale et les tests :
connecter les trois parties — données, LLM, bot Discord —
et lancer le bot dans un serveur Discord privé entre amis pour avoir de vrais retours.

*[Slide retours utilisateurs]*

Les retours ont été utiles : la qualité des recettes générées était parfois trop
approximative parce que Mistral local est moins puissant qu'un GPT-4.
Ça m'a permis d'affiner le prompt système pour forcer une réponse structurée :
nom de la recette, ingrédients avec quantités en unités métriques, étapes numérotées,
et un conseil du chef à la fin.

---

## PARTIE 5 — Bilan et améliorations (3 min)

*[Slide forces et limites]*

Ce projet fonctionne en conditions réelles. Le bot répond, les recettes sont cohérentes,
et le pipeline RAG fait son travail : la recherche vectorielle permet de trouver
des recettes pertinentes même avec des formulations vagues.

Les vraies limites sont au nombre de trois.
Premièrement, Mistral en local est moins puissant qu'un LLM cloud :
les réponses sont parfois génériques ou imprécises.
Deuxièmement, la qualité du résultat dépend beaucoup de la qualité du dataset :
des données mal normalisées donnent de mauvaises recettes.
Troisièmement, les embeddings sur CPU restent le goulot d'étranglement principal.

*[Slide améliorations possibles]*

Si je devais continuer ce projet, je ferais trois choses.

Ensuite, calculer les embeddings sur GPU pour réduire le temps d'insertion
de plusieurs heures à quelques minutes sur le dataset complet.

Puis, ajouter un filtrage par contraintes — budget, régime alimentaire, allergies —
en enrichissant la requête vectorielle avec des filtres SQL classiques.

Enfin, remplacer Mistral par un modèle plus puissant, ou utiliser une API cloud
pour la génération, tout en gardant la recherche vectorielle en local.

---

*[Slide conclusion — merci]*

Pour conclure, ce projet m'a permis de construire un système complet de bout en bout,
en touchant à des problématiques très différentes : bases de données relationnelles,
recherche vectorielle, LLM, et développement bot.

Ce qui m'a le plus appris, c'est probablement le débogage de performance :
passer de 2h30 à 3 minutes m'a obligé à vraiment comprendre ce qui se passait
sous le capot, et pas juste faire fonctionner le code.

Merci pour votre attention, je suis disponible pour vos questions.