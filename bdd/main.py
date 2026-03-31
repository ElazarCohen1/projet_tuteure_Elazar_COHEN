import data_normalization as N
import data_insertion as I
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


if __name__== "__main__":
    d = csv_to_dict("./test.csv",',')
    normalize_d = []
    for i in d:
        res = N.normalize_data(i)
        normalize_d.append(res)

    I.insert_dataset(normalize_d)
