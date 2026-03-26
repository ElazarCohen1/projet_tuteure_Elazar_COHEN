"""
    This module normalizes recipe data coming from a dataset using the parse ingredient nlp
    @author Elazar COHEN
"""
import csv
import json
from ingredient_parser import parse_ingredient
import re

def parse_string(chaine:str):
    return parse_ingredient(chaine.lower())
   

def normalize_word(word: str) -> str:

    temp = ''.join([c.lower() if c.isalpha() or c.isnumeric() else ' ' for c in word])
    temp = re.sub(r'\s+', ' ', temp)

    return temp.strip()

def csv_to_dict(csv_name_file:str,separator:str) -> list[dict]:
    """ 
        transform a csv file into a dict 
        Args :
            - A filename for a csv file 
        Returns: 
            - the list of dict with the csv data 
            - Output format :  [{
                "id": str,
                "title": str,
                "ingredients": list[str],
                "directions": list[str] | None
            },...]
        Warning :
            - the first row of the file need to have the name of the columns
    """
    result = []
    with  open(csv_name_file) as file:
        reader = csv.DictReader(file,delimiter=separator)
        for row in reader:
            row_dict = dict(row)
            for key, value in row_dict.items():
                if value and value[0] == '[':
                    row_dict[key] = json.loads(value)
            result.append(row_dict)
    return result


def parse_list_ingredients(ingredients:list[str])-> list:
    liste_parse =  [parse_string(ing) for ing in (ingredients or [])]
    liste_parse = transform_parse_ingredient_to_dict(liste_parse)

    return liste_parse

def transform_parse_ingredient_to_dict(parse_ing) -> dict:
    liste = []
    for ing in parse_ing:
        res = {}
        res["name"] = ing.name[0].text
        res["quantity"] = float(ing.amount[0].quantity)
        res["unit"] = ing.amount[0].unit
        res["preparation"] = ing.preparation.text if ing.preparation else ""
        liste.append(res)
    return liste


def normalize_data(recipe:dict) -> dict:
    """
        Normalize one recipe 
        Args : 
            - recipe : a dict for modelise a recipe 
        Returns :
            - a dict with the normalize data 
    """ 
    list_ing = []
    list_steps = []
    res = {}
    for key,value in recipe.items():
        key = str(key).lower()
        if key.startswith("name") or key.startswith("title") :
            res["title"] = normalize_word(value)

        if key.startswith("ingredient"):
            list_ing += parse_list_ingredients(value)

        if key.startswith("direction") or key.startswith("step"):
            list_steps += [normalize_word(i) for i in value]

    res["ingredients"] = list_ing
    res["steps"] = list_steps
    return res

if __name__ == "__main__":
    d = csv_to_dict("./test.csv",',')
    print(d[1])
    normalize_d = normalize_data(d[1])

    for key,value in normalize_d.items():
        print(f"{key} : {value}\n")

