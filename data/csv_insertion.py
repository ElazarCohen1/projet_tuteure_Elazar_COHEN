"""
    This module inserts data from a dataset into a given postgres database.
    Uses batch inserts (execute_values) for performance.
"""
import time
import io
import csv
import bdd.db as db
from pgvector.psycopg2 import register_vector


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


def prepare_data(dataset: list[dict]):
    """
    Parcourt tout le dataset une seule fois et construit :
      - recipe_rows        : (id, title)
      - ingredient_map     : {name: id}
      - ingredient_rows    : (id, name)
      - recipe_ing_rows    : (recipe_id, ingredient_id, quantity, unit, particularity)
      - steps_rows         : (recipe_id, step_number, instruction)
      - chunks             : [str]  — textes à encoder
 
    Les IDs sont pré-assignés ici, pas par la DB.
    """
    recipe_rows = []
    ingredient_map: dict[str, int] = {}
    ingredient_rows = []
    recipe_ing_rows = []
    steps_rows = []
    chunks = []
 
    next_ing_id = 1
 
    for recipe_id, recipe in enumerate(dataset, start=1):
        title = recipe.get("title", "")
        recipe_rows.append((recipe_id, title))
        chunks.append(build_recipe_chunk(recipe))
 
        # ingrédients
        for ing in recipe.get("ingredients", []):
            name = ing.get("name")
            if not name:
                continue
 
            if name not in ingredient_map:
                ingredient_map[name] = next_ing_id
                ingredient_rows.append((next_ing_id, name))
                next_ing_id += 1
 
            recipe_ing_rows.append((
                recipe_id,
                ingredient_map[name],
                ing.get("quantity"),   # can be None
                ing.get("unit") or "",
                ing.get("preparation") or "",
            ))
 
        # steps
        for step_number, instruction in enumerate(recipe.get("steps", [])):
            steps_rows.append((recipe_id, step_number, instruction.replace('\n', ' ')))
 
    return recipe_rows, ingredient_rows, recipe_ing_rows, steps_rows, chunks
 
def copy_rows(cur, table: str, columns: tuple, rows: list):
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    buf.seek(0)
    cur.copy_from(buf, table, columns=columns, sep='\t', null='')


def encode_chunk(chunk,model):
    texts = [build_recipe_chunk(r) for r in chunk]
    return model.encode(texts, batch_size=512, show_progress_bar=False)

import time

def insert_dataset(dataset, model):

    timings = {}

    total_start = time.perf_counter()

    t = time.perf_counter()
    recipe_rows, ingredient_rows, recipe_ing_rows, steps_rows, chunks = prepare_data(dataset)
    timings["prepare_data"] = time.perf_counter() - t

    t = time.perf_counter()
    embeddings = model.encode(chunks, batch_size=1024, show_progress_bar=False)
    timings["embeddings"] = time.perf_counter() - t

    t = time.perf_counter()
    embedding_rows = [
        (
            recipe_id,
            chunk.replace('\n', '\\n'),
            "[" + ",".join(map(str, emb.tolist())) + "]",
            "all-MiniLM-L6-v2"
        )
        for recipe_id, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1)
    ]
    timings["build_embedding_rows"] = time.perf_counter() - t

    t = time.perf_counter()

    with db.connect() as conn:
        conn.autocommit = False
        register_vector(conn)

        with conn.cursor() as cur:

            t0 = time.perf_counter()
            copy_rows(cur, "recipe", ("id", "title"), recipe_rows)
            timings["insert_recipe"] = time.perf_counter() - t0

            t0 = time.perf_counter()
            copy_rows(cur, "ingredients", ("id", "name"), ingredient_rows)
            timings["insert_ingredients"] = time.perf_counter() - t0

            t0 = time.perf_counter()
            copy_rows(
                cur,
                "recipe_ingredient",
                ("recipe_id", "ingredient_id", "quantity", "unit", "particularity"),
                recipe_ing_rows
            )
            timings["insert_recipe_ingredient"] = time.perf_counter() - t0

            t0 = time.perf_counter()
            copy_rows(cur, "steps", ("recipe_id", "step_number", "instruction"), steps_rows)
            timings["insert_steps"] = time.perf_counter() - t0

            t0 = time.perf_counter()
            copy_rows(cur, "recipe_embeddings", ("recipe_id", "chunk_text", "embedding", "model_version"), embedding_rows)
            timings["insert_embeddings"] = time.perf_counter() - t0

        conn.commit()

    timings["db_total"] = time.perf_counter() - t

    timings["total"] = time.perf_counter() - total_start

    print("\n===== TIMINGS =====")
    for k, v in timings.items():
        print(f"{k:25s}: {v:.4f}s")

    return 1