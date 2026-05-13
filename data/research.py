from bdd.sql_request import SQL_requete
import ollama 

SCORE_MIN = 0.3

def search_similar(text_query: str, model, top_k: int = 5):
    query_emb = model.encode(text_query).tolist()
    rows = SQL_requete("""
        SELECT recipe_id, chunk_text,
               1 - (embedding <=> %s::vector) AS score
        FROM recipe_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_emb, query_emb, top_k), True)

    if not rows:
        return None

    filtered = [row for row in rows if row[2] >= SCORE_MIN]
    return filtered if filtered else rows[:2]


def ask_mistral_with_context(query, search_results):
    context_parts = []
    for row in search_results:
        recipe_id, chunk_text, score = row[0], row[1], row[2]
        context_parts.append(f"[Recette ID {recipe_id} — score {score:.2f}]\n{chunk_text}")

    full_context = "\n\n---\n\n".join(context_parts)

    response = ollama.chat(
        model='mistral',
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un chef cuisinier expert francophone. "
                    "Tu réponds TOUJOURS exclusivement en français, sans exception. "
                    "Traduis tous les mots anglais en français (ingrédients, unités, noms de recettes). "
                    "Convertis toutes les unités anglo-saxonnes en métriques : "
                    "ounce → grammes, cup → ml/cl, fahrenheit → celsius, pound → grammes. "
                    "Structure ta réponse ainsi :\n"
                    "1. **Nom de la recette**\n"
                    "2. **Ingrédients** : liste complète avec quantités métriques\n"
                    "3. **Étapes** : chaque étape détaillée et précise\n"
                    "4. **Conseil du chef** : une astuce pour réussir\n"
                    "Ne propose qu'une seule recette, la plus pertinente par rapport à la demande."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Voici les recettes disponibles :\n\n{full_context}\n\n"
                    f"Demande : {query}\n\n"
                    "Choisis la recette la plus adaptée et présente-la complètement."
                )
            }
        ]
    )

    return response['message']['content']