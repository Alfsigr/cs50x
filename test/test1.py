import requests
import json

url = "https://twinword-word-associations-v1.p.rapidapi.com/associations/"

querystring = {"entry":"muppet"}

headers = {
    'x-rapidapi-key': "04c1a8be93msh30596fd533a7913p148671jsn7bebee3f1eed",
    'x-rapidapi-host': "twinword-word-associations-v1.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

assoc_dict = json.loads(response.text)

assoc_array = assoc_dict["associations_array"]

#####
print(assoc_dict)
print(assoc_array)