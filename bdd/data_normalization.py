"""
    This module normalizes recipe data coming from a dataset using the parse ingredient nlp
    @author Elazar COHEN
"""
from ingredient_parser import parse_ingredient
import re
from fractions import Fraction


def parse_string(chaine:str):
    return parse_ingredient(chaine.lower())
   

def normalize_word(word: str) -> str:

    temp = ''.join([c.lower() if c.isalpha() or c.isnumeric() else ' ' for c in word])
    temp = re.sub(r'\s+', ' ', temp)

    return temp.strip()




def parse_list_ingredients(ingredients:list[str])-> list:
    liste_parse =  [parse_string(ing) for ing in (ingredients or [])]
    liste_parse = transform_parse_ingredient_to_dict(liste_parse)

    return liste_parse


def safe_quantity(q):
    """Convertit quantity en float si possible, sinon None."""
    if q is None or q == '':
        return None
    if isinstance(q, Fraction):
        return round(float(q),1)
    try:
        return round(float(q),1)
    except ValueError:
        return None


def check_in_liste(l:list[dict],elm:str)->bool:
    for d in l:
        for value in d.values():
            if value == elm:
                return True
    return False
    
def transform_parse_ingredient_to_dict(parse_ing) -> list[dict]:
    liste = []

    for ing in parse_ing:
        # Nom et préparation de base
        name = ing.name[0].text if ing.name else ""
        preparation = ing.preparation.text if ing.preparation else ""
        if check_in_liste(liste,name):
            continue
        if not ing.amount:
            liste.append({
                "name": name,
                "quantity": None,
                "unit": "",
                "preparation": preparation
            })
            continue
        else :
            q = safe_quantity(ing.amount[0].quantity)
            u = str(ing.amount[0].unit) if ing.amount[0].unit else ""
            liste.append({
                "name": name,
                "quantity": q,
                "unit": u,
                "preparation": preparation
            })
            
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


    
import csv
import json


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
if __name__=="__main__":
    d = csv_to_dict("./test.csv",',')
    normalize_d = []
    for i in d:
        res = normalize_data(i)
        normalize_d.append(res)
        print(res["ingredients"])

