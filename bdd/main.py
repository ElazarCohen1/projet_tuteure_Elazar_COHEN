import data.data_normalization as N
import data.csv_insertion as I
import csv
import os
import ast
import time
os.environ["HF_HUB_OFFLINE"] = "1"


def csv_to_dict(csv_name_file: str, separator: str = ',') -> list[dict]:
    """Charge tout le CSV en mémoire d'un coup."""
    dataset = []

    with open(csv_name_file, encoding='utf-8', errors='replace') as file:
        reader = csv.DictReader(file, delimiter=separator)
        print("Chargement du CSV...")

        for row in reader:
            row_dict = {}
            for key, value in row.items():
                if value is None:
                    row_dict[key] = None
                    continue

                v_strip = value.strip()

                if v_strip.startswith('[') and v_strip.endswith(']'):
                    try:
                        row_dict[key] = ast.literal_eval(v_strip)
                        continue
                    except (ValueError, SyntaxError):
                        pass

                row_dict[key] = v_strip

            dataset.append(row_dict)

    print(f"{len(dataset)} lignes chargées.")
    return dataset


import time

if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")

    total_start = time.perf_counter()

    try:
        t_load = time.perf_counter()
        raw_data = csv_to_dict("./bdd/recipes_data.csv")
        print(f"Chargement terminé en {time.perf_counter() - t_load:.4f}s")

        print("Normalisation des données...")
        t_norm = time.perf_counter()

        normalized_data = [
            N.normalize_data(row, i)
            for i, row in enumerate(raw_data)
        ]

        print(f"{len(normalized_data)} recettes normalisées en {time.perf_counter() - t_norm:.4f}s")

        print("Insertion dans la base...")
        t_insert = time.perf_counter()

        success = I.insert_dataset(normalized_data, model)

        insert_time = time.perf_counter() - t_insert

        if success:
            print(f"Dataset inséré avec succès en {insert_time:.4f}s")
        else:
            print("Échec de l'insertion.")
            exit(1)

        total_time = time.perf_counter() - total_start
        print(f"Temps total: {total_time:.4f}s")

    except Exception as e:
        print("ERREUR :", e)
        exit(1)