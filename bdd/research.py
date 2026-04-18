from sql_request import SQL_requete
import ollama 


def search_similar(text_query: str, model ,top_k: int = 5):
    query_emb = model.encode(text_query).tolist()
    rows = SQL_requete("""
            SELECT recipe_id, chunk_text,
                   1 - (embedding <=> %s::vector) AS score
            FROM recipe_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_emb, query_emb, top_k),True)

    if not rows :
        return None
    
    return rows


def ask_mistral_with_context(query, search_results):

    context_chunks = [row[1] for row in search_results] 
    full_context = "\n---\n".join(context_chunks)

    messages = [
        {
            'role': 'system',
            'content': (
                "Tu es un chef cuisinier virtuel. Réponds aux questions en utilisant "
                "uniquement les extraits de recettes fournis. Si tu ne trouves pas la "
                "réponse, arrange les recettes pour creer une nouvelle recette a partir de ce que tu as."
            ),
        },
        {
            'role': 'user',
            'content': f"CONTEXTE DES RECETTES :\n{full_context}\n\nQUESTION : {query}",
        },
    ]

    response = ollama.chat(model='mistral', messages=messages)
    
    return response['message']['content']