"""
    This module normalizes recipe data coming from a dataset using the parse ingredient nlp
    @author Elazar COHEN
"""
from ingredient_parser import parse_ingredient
import re
from fractions import Fraction


def parse_string(chaine:str):
    try:
        return parse_ingredient(chaine.lower())
    except Exception:
        return parse_ingredient("")
   

import re

def normalize_word(word: str) -> str:
    if not word:
        return ""

    word = word.lower()

    word = re.sub(r"[^a-z0-9\s\./\-]", " ", word)

    word = word.replace("\\", " ")

    word = re.sub(r"\s+", " ", word)

    return word.strip()

def normalize_quantity(quantity:str):
    if not quantity :
        return ""
    
    quantity = quantity.replace("\\","/")
    quantity = quantity.replace("'", "")
    return quantity.strip()
    

def parse_list_ingredients(ingredients: list[str]) -> list:
    safe = [str(ing) for ing in (ingredients or []) if ing is not None]
    liste_parse = [parse_string(normalize_quantity(ing)) for ing in safe]
    return transform_parse_ingredient_to_dict(liste_parse)


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
        name = ing.name[0].text if ing.name else ""
        preparation = ing.preparation.text if ing.preparation else ""

        if check_in_liste(liste, name):
            continue

        if not ing.amount:
            liste.append({
                "name": name,
                "quantity": None,
                "unit": "",
                "preparation": preparation
            })
            continue

        comp = ing.amount[0]

        if hasattr(comp, "amounts"):
            quantities = [safe_quantity(a.quantity) for a in comp.amounts if a.quantity]
            q = round(sum(quantities), 1) if quantities else None
            u = str(comp.amounts[0].unit) if comp.amounts and comp.amounts[0].unit else ""   
        else:
            q = safe_quantity(comp.quantity)
            u = str(comp.unit) if comp.unit else ""

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


    