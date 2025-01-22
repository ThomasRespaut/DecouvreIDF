import pandas as pd
import json

# Exemple : si votre JSON est dans un fichier "data.json"
# Sinon, remplacez par data = <votre_variable_python_contenant_le_JSON>
with open("place_reviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# On aplatit le JSON en un DataFrame unique
df_all = pd.json_normalize(data, sep="_")

# On vérifie rapidement les colonnes générées
print(df_all.columns)
print(df_all.head(1))

# Sauvegarder dans un CSV
df_all.to_csv("output.csv", index=False, encoding="utf-8")

print("Les données ont été enregistrées dans 'output.csv'.")
