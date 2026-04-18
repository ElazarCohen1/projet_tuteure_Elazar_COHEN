from pgvector.psycopg2 import register_vector
import bdd.db as db


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
        register_vector(conn)
        with conn.cursor() as cur:

            if params:
                cur.execute(requete, params)
            else:
                cur.execute(requete)

            if fetch:
                return cur.fetchall()  

            conn.commit()
            return True


