from service.ParseService import *
import pandas as pd

parsing = ParsingService()

df = pd.read_csv('../analyse/user.csv')

df = df.loc[df["Donnez vous votre consentement à l'utilisation de vos réponses pour un traitement informatique ?"] == "J'accepte"]


df["Lieu d'habitation"] = df["Lieu d'habitation"].apply(
    lambda x: parsing.clean_string(parsing.replace_with_regex(x, r"\s*\([^)]*\)", ""))
)

df["Quel format de lecture / achats préférez-vous ?"] = df["Quel format de lecture / achats préférez-vous ?"].apply(
    lambda x: [parsing.clean_string(item) for item in parsing.split_string(x, delimiter=",")]
)

df["Quels sont vos centres d'intérêts ?"] = df["Quels sont vos centres d'intérêts ?"].apply(
    lambda x: [parsing.clean_string(item) for item in parsing.split_string(x, delimiter=",")]
)

df["Quel genre de livre préférez-vous ?"] = df["Quel genre de livre préférez-vous ?"].apply(
    lambda x: [parsing.clean_string(item) for item in parsing.split_string(x, delimiter=",")]
)

df["Dans quel cadre / objectif pratiquez-vous la lecture ?"] = df["Dans quel cadre / objectif pratiquez-vous la lecture ?"].apply(
    lambda x: [parsing.clean_string(item) for item in parsing.split_string(x, delimiter=",")]
)


print(df["Dans quel cadre / objectif pratiquez-vous la lecture ?"])
