import bdd.data_normalization as N
import bdd.data_insertion as I
import bdd.research as R
import csv
from sentence_transformers import SentenceTransformer
import os
os.environ["HF_HUB_OFFLINE"] = "1"
import ast 
import asyncio # transform to async
from typing import Iterator, List, Dict


model = SentenceTransformer("all-MiniLM-L6-v2")

def csv_to_dict(csv_name_file: str, separator: str, size: int = 10000):
    batch = []
    i = 0

    with open(csv_name_file, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=separator)

        for row in reader:
            row_dict = dict(row)

            for key, value in row_dict.items():
                if value:
                    v_strip = value.strip()
                    if v_strip.startswith('[') and v_strip.endswith(']'):
                        try:
                            row_dict[key] = ast.literal_eval(v_strip)
                        except (ValueError, SyntaxError):
                            pass

            batch.append(row_dict)
            i += 1

            if i >= size:
                yield batch, i
                batch = []
                i = 0

        if batch:
            yield batch, len(batch)

async def generate_recipe(request: str):
    loop = asyncio.get_event_loop()
    
    results = await loop.run_in_executor(None, R.search_similar, request, model, 5)
    result = await loop.run_in_executor(None, R.ask_mistral_with_context, request, results)
    
    return result


if __name__ == "__main__":

    total_inserted = 0

    try:
        for batch, batch_size in csv_to_dict("./bdd/recipes_data.csv", ',', size=10000):

            normalized_data = []

            for row in batch:
                normalized_data.append(N.normalize_data(row))

            I.insert_dataset(normalized_data, model)

            total_inserted += batch_size

            print(f"{total_inserted} lignes insérées...")

    except Exception as e:
        print("ERREUR INSERTION :", e)
        exit(1)

    print("Dataset inséré avec succès !")