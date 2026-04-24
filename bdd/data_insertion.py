"""
    This module inserts data from a dataset into a given postgres database.
    Uses batch inserts (execute_values) for performance.
"""
import bdd.db as db
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values


def build_recipe_chunk(recipe: dict) -> str:
    """
    Construit une chaîne de texte unique représentant toute la recette.
    C'est ce texte qui sera embedé — il résume titre, ingrédients et étapes.
    Exemple :
        Recette : tarte aux pommes
        Ingrédients : 3 pommes, 200g farine, 100g beurre
        Étapes : Éplucher les pommes. Mélanger la farine et le beurre. ...
    """
    title = recipe.get("title", "")

    ingredients_parts = []
    for ing in recipe.get("ingredients", []):
        qty = f"{ing.get('quantity', '')} {ing.get('unit', '')}".strip()
        name = ing.get("name", "")
        ingredients_parts.append(f"{qty} {name}".strip() if qty else name)
    ingredients_str = ", ".join(ingredients_parts)

    steps_str = ". ".join(recipe.get("steps", []))

    return f"Recette : {title}\nIngrédients : {ingredients_str}\nÉtapes : {steps_str}"




def insert_recipes_batch(cur, recipes: list[dict]) -> list[int]:
    """Insère toutes les recettes d'un chunk, retourne leurs IDs dans l'ordre."""
    result = execute_values(
        cur,
        "INSERT INTO recipe(title) VALUES %s RETURNING id",
        [(r["title"],) for r in recipes],
        fetch=True
    )
    return [row[0] for row in result]


def insert_ingredients_batch(cur, recipes: list[dict]) -> dict[str, int]:
    """
    Insère tous les ingrédients uniques du chunk.
    Retourne un dict {name: id}.
    """
    all_names = list({
        ing["name"]
        for recipe in recipes
        for ing in recipe.get("ingredients", [])
        if ing.get("name")
    })

    if not all_names:
        return {}

    result = execute_values(
        cur,
        """
        INSERT INTO ingredients(name) VALUES %s
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id, name
        """,
        [(name,) for name in all_names],
        fetch=True
    )
    return {row[1]: row[0] for row in result}  
    


def insert_recipe_ingredients_batch(cur, recipes: list[dict], recipe_ids: list[int], ingredient_ids: dict[str, int]):
    """Insère toutes les liaisons recipe_ingredient du chunk en une seule requête."""
    rows = []
    for recipe, recipe_id in zip(recipes, recipe_ids):
        for ing in recipe.get("ingredients", []):
            name = ing.get("name")
            if name and name in ingredient_ids:
                rows.append((
                    recipe_id,
                    ingredient_ids[name],
                    ing.get("quantity"),
                    ing.get("unit"),
                    ing.get("preparation")
                ))

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO recipe_ingredient(recipe_id, ingredient_id, quantity, unit, particularity)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            rows
        )


def insert_steps_batch(cur, recipes: list[dict], recipe_ids: list[int]):
    """Insère toutes les étapes du chunk en une seule requête."""
    rows = [
        (recipe_id, i, step)
        for recipe, recipe_id in zip(recipes, recipe_ids)
        for i, step in enumerate(recipe.get("steps", []))
    ]

    if rows:
        execute_values(
            cur,
            "INSERT INTO steps(recipe_id, step_number, instruction) VALUES %s",
            rows
        )


def insert_embeddings_batch(cur, recipes: list[dict], recipe_ids: list[int], embeddings):
    """Insère tous les embeddings du chunk en une seule requête."""
    rows = [
        (recipe_id, build_recipe_chunk(recipe), emb.tolist(), "all-MiniLM-L6-v2")
        for recipe, recipe_id, emb in zip(recipes, recipe_ids, embeddings)
    ]

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO recipe_embeddings(recipe_id, chunk_text, embedding, model_version)
            VALUES %s
            ON CONFLICT (recipe_id) DO UPDATE
                SET chunk_text    = EXCLUDED.chunk_text,
                    embedding     = EXCLUDED.embedding,
                    model_version = EXCLUDED.model_version
            """,
            rows
        )


def insert_dataset(dataset: list[dict], model, chunk_size: int = 1000) -> bool:
    """
    Insère un dataset complet de recettes en batch.
    Args:
        dataset    : liste de recettes normalisées
        model      : SentenceTransformer déjà chargé
        chunk_size : nombre de recettes par batch (défaut 1000)
    Returns:
        True si succès, False sinon
    """
    try:
        total = len(dataset)
        with db.connect() as conn:
            conn.autocommit = False  
            register_vector(conn)

            with conn.cursor() as cur:
                for i in range(0, total, chunk_size):
                    chunk = dataset[i:i + chunk_size]
                    print(f"[{i + len(chunk)}/{total}] Insertion chunk {i // chunk_size + 1}...")

                    texts = [build_recipe_chunk(r) for r in chunk]
                    embeddings = model.encode(texts, batch_size=64, show_progress_bar=False)

                    recipe_ids     = insert_recipes_batch(cur, chunk)
                    ingredient_ids = insert_ingredients_batch(cur, chunk)

                    insert_recipe_ingredients_batch(cur, chunk, recipe_ids, ingredient_ids)
                    insert_steps_batch(cur, chunk, recipe_ids)
                    insert_embeddings_batch(cur, chunk, recipe_ids, embeddings)

                    conn.commit()
                    print(f"  → chunk commité.")

        return True

    except Exception as e:
        print("Erreur lors de l'insertion du dataset :", e)
        return False