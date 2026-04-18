import bdd.data_normalization as N
import bdd.data_insertion as I
import bdd.research as R
import csv
# import json
from sentence_transformers import SentenceTransformer
import os
os.environ["HF_HUB_OFFLINE"] = "1"
import ast 
import asyncio # transform to async
model = SentenceTransformer("all-MiniLM-L6-v2")

def csv_to_dict(csv_name_file: str, separator: str) -> list[dict]:
    result = []
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
                            continue
            result.append(row_dict)
    return result


async def generate_recipe(request: str):
    loop = asyncio.get_event_loop()
    
    results = await loop.run_in_executor(None, R.search_similar, request, model, 5)
    result = await loop.run_in_executor(None, R.ask_mistral_with_context, request, results)
    
    return result


if __name__ == "__main__":
    data = csv_to_dict("./test.csv", ',')
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # normalized_data = []
    # for row in data:
    #     normalized_row = N.normalize_data(row)
    #     normalized_data.append(normalized_row)

    # try:
    #     I.insert_dataset(normalized_data, model)
    # except Exception as e:
    #     print("ERREUR INSERTION :", e)
    #     exit(1)  

    # print("Dataset inséré avec succès !")

    query = "plat avec des carrotes"
    results = R.search_similar(query, model, top_k=5)
    result = R.ask_mistral_with_context(query, results)
    print(result)