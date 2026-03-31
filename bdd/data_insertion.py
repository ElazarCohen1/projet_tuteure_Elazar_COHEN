"""
    This module insert data from a dataset into a given postgres database 
"""
import db 




def SQL_requete(requete: str, params: tuple = None, fetch: bool = False):
    """
    Exécute une requête SQL.
    Args:
        requete (str): La requête SQL
        params (tuple, optional): Paramètres SQL
        fetch (bool): True si on veut récupérer les résultats
    Returns:
        list[namedtuple] si fetch=True, sinon True
    """
    with db.connect() as conn:
        with conn.cursor() as cur:
            if params:
                cur.execute(requete, params)
            else:
                cur.execute(requete)

            if fetch:
                return cur.fetchall()  

            conn.commit()
            return True



def insert_recipe(recipe: dict) -> int:
    """
    Insère une recette et retourne son ID.
    """
    #insert the recipe 
    result = SQL_requete(
        "INSERT INTO recipe(title) VALUES (%s) RETURNING id",
        (recipe["title"],),
        fetch=True
    )
    recipe_id = result[0].id

    # all the ingredients for this recipe
    ingredient_ids = {}
    for ing in recipe["ingredients"]:
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

    # all the steps for the recipe
    for i in range(len(recipe["steps"])) :
        SQL_requete(
            """
                INSERT INTO steps(recipe_id,step_number,instruction) 
                VALUES (%s,%s,%s)
            """,
            (
               recipe_id,
               i,
               recipe["steps"][i]
            )
        )

    return recipe_id


def insert_dataset(dataset: list[dict]) -> bool:
    """
    Insère un dataset complet de recettes.
    Args:
        dataset (list[dict]): dataset normalisé
    Returns:
        bool: True si succès, False sinon
    """
    try:
        for recipe in dataset:
            insert_recipe(recipe)
        return True
    except Exception as e:
        print("Erreur lors de l'insertion du dataset :", e)
        return False


  