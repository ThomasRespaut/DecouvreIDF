# Script pour charger le fichier Excel dans le modèle Evenement
import pandas as pd
from app.models import Evenement

def load_excel():
    import os
    print(os.path.abspath('app/data/lefrenchguide_idf.csv'))
