# Script pour charger le fichier CSV dans le modèle Evenement
import pandas as pd
from app.models import Evenement

def load_csv():
    file_path = 'app/data/lefrenchguide_idf.csv'  # Remplacez par le chemin correct

    try:
        # Charger le fichier CSV avec gestion des erreurs de tokenisation
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip', sep=";")

        # Insérer les données dans la base
        for _, row in df.iterrows():
            Evenement.objects.create(
                categorie=row['Catégorie'],
                nom=row['Nom'],
                description=row['Description'],
                adresse=row['Adresse'],
                latitude=row['Latitude'],
                longitude=row['Longitude']
            )
        print("Données chargées avec succès depuis le fichier CSV.")

    except FileNotFoundError:
        print(f"Erreur : le fichier {file_path} est introuvable.")
    except ValueError as ve:
        print(f"Erreur de format : {ve}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Commandes finales
# python manage.py makemigrations
# python manage.py migrate
# python manage.py shell
# >>> from app.scripts.load_csv import load_csv
# >>> load_csv()
# >>> exit()

# python manage.py runserver
