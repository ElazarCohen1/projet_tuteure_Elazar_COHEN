"""
    This module normalizes recipe data coming from a dataset.
    @author Elazar COHEN
"""


# the main fonction 
def normalize(filename:str) -> list[dict]:
    """
        Normalize a file into a dataset with normalize data
        Args:
            - filename : the string of the file we want to normalize
        Returns : 
            - the dataset we have normalize 
    """


def dataset_normalization(dataset: dict) -> dict :
    """
        Transform a JSON-like dictionary containing recipes into a normalized dataset.

        Expected input format:

            [{
                "id": str,
                "title": str,
                "ingredients": list[str],
                "directions": list[str] | None
            },...]

        Args:
            - dataset (dict): Dictionary representing a recipe.

        Returns:
            - dict: Normalized recipe dictionary.
    """


def normalize_data(recipe:dict):
    """
        Normalize one recipe 
        Args : 
            - recipe : a dict for modelise a recipe 
        Returns :
            - a dict with the normalize data 
    """



def csv_to_dict(csv_name_file:str) -> list[dict]:
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

