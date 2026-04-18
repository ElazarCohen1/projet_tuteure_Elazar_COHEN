from bdd.sql_request import SQL_requete
import ollama 


def search_similar(text_query: str, model ,top_k: int = 3):
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

    context_chunks = [row[1][:400] for row in search_results]
    full_context = "\n---\n".join(context_chunks)

    response = ollama.chat(
        model='mistral',
        messages=[
            {
                "role": "system",
                "content": "Tu es un chef. Réponds uniquement avec le contexte fourni. detail chaque étape!"
            },
            {
                "role": "user",
                "content": f"{full_context}\n\nQUESTION: {query}"
            }
        ]
    )

    return response['message']['content']