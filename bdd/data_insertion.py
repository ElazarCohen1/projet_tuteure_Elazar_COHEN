"""
    This module insert data from a dataset into a given postgres database 
"""
from sql_request import SQL_requete


def insert_recipe(recipe: dict) -> int:
    """
    Insert a recipe in the db .
    RETURNS : the recipe_id 
    """
    result = SQL_requete(
        "INSERT INTO recipe(title) VALUES (%s) RETURNING id",
        (recipe["title"],),
        fetch=True
    )
    recipe_id = result[0].id
    return recipe_id

def insert_ingredients(recipe_id,ingredients:dict):
    ingredient_ids = {}
    for ing in ingredients:
        res = SQL_requete(
            """
            INSERT INTO ingredients(name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (ing["name"],),
            fetch=True
        )
        ingredient_ids[ing["name"]] = res[0].id
    
        check = SQL_requete(
            "SELECT recipe_id,ingredient_id FROM recipe_ingredient WHERE recipe_id = %s AND ingredient_id = %s",
            (recipe_id,
            ingredient_ids[ing["name"]])
        )
        if not check :
            continue

        SQL_requete(
            """
            INSERT INTO recipe_ingredient(recipe_id, ingredient_id, quantity, unit, particularity)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                recipe_id,
                ingredient_ids[ing["name"]],
                ing.get("quantity"),
                ing.get("unit"),
                ing.get("preparation")
            )
        )    

def insert_steps(recipe_id:int, steps:dict):
    for i in range(len(steps)) :
        SQL_requete(
            """
                INSERT INTO steps(recipe_id,step_number,instruction) 
                VALUES (%s,%s,%s)
            """,
            (
               recipe_id,
               i,
               steps[i]
            )
        )


def insert_embeddings(recipe:dict,model,recipe_id):
    chunks = []
    for i, step in enumerate(recipe["steps"]):
        chunks.append({"chunk_text": step, "chunk_index": i, "chunk_type": "step"})

    # ingredients
    for i, ing in enumerate(recipe["ingredients"]):
        text = f"{ing.get('quantity','')} {ing.get('unit','')} {ing['name']}".strip()
        if text:
            chunks.append({"chunk_text": text, "chunk_index": i, "chunk_type": "ingredient"})
    
    for c in chunks:
        emb = model.encode(c["chunk_text"]).tolist()
        SQL_requete(
            "INSERT INTO recipe_embeddings(recipe_id, chunk_index, chunk_text, chunk_type, embedding, model_version) "
            "VALUES (%s,%s,%s,%s,%s,%s)"
            "ON CONFLICT (recipe_id, chunk_index, chunk_type) DO UPDATE "
            "SET chunk_text = EXCLUDED.chunk_text, embedding = EXCLUDED.embedding, model_version = EXCLUDED.model_version",
            
            (recipe_id, c["chunk_index"], c["chunk_text"], c["chunk_type"], emb, "all-MiniLM-L6-v2")
        )


def insert_dataset(dataset: list[dict],model) -> bool:
    """
    Insère un dataset complet de recettes.
    Args:
        dataset (list[dict]): dataset normalisé
    Returns:
        bool: True si succès, False sinon
    """
    try:
        for recipe in dataset:
            recipe_id = insert_recipe(recipe)
            insert_ingredients(recipe_id,recipe["ingredients"])
            insert_steps(recipe_id,recipe["steps"])
            insert_embeddings(recipe,model,recipe_id)
        return True
    except Exception as e:
        print("Erreur lors de l'insertion du dataset :", e)
        return False




  