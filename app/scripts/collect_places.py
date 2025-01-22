import pandas as pd
import requests
import time
import json

# Initialiser le DataFrame vide avant de commencer
df_places = pd.DataFrame(columns=[
    "place_id", "name", "editorial_summary", "latitude", "longitude",
    "types", "rating", "url", "reviews", "current_opening_hours",
    "formatted_address", "formatted_phone_number", "opening_hours",
    "photos", "user_ratings_total", "vicinity", "website"
])

def fetch_place_details(place_id, api_key):
    """
    Fetch place details from Google Places API and return a new DataFrame row.

    Parameters:
    - place_id (str): The Place ID of the location.
    - api_key (str): Your Google Places API key.

    Returns:
    - dict: A dictionary representing a new row for the DataFrame.
    """
    # Vérifier si place_id existe déjà dans le DataFrame
    if place_id in df_places["place_id"].values:
        print(f"Place ID {place_id} already exists in the DataFrame. Skipping...")
        return None  # Retourne None pour indiquer qu'il ne faut pas ajouter cette entrée

    # Construire l'URL de l'API
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&language=fr&key={api_key}"

    # Récupérer les données de l'API
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        results = json_data.get("result", {})

        # Extraire les champs requis
        data = {
            "place_id": results.get("place_id"),
            "name": results.get("name"),
            "editorial_summary": results.get("editorial_summary", {}).get("overview"),
            "latitude": results.get("geometry", {}).get("location", {}).get("lat"),
            "longitude": results.get("geometry", {}).get("location", {}).get("lng"),
            "types": results.get("types"),
            "rating": results.get("rating"),
            "url": results.get("url"),
            "reviews": results.get("reviews"),
            "current_opening_hours": results.get("current_opening_hours", {}).get("open_now"),
            "formatted_address": results.get("formatted_address"),
            "formatted_phone_number": results.get("formatted_phone_number"),
            "opening_hours": results.get("opening_hours", {}).get("weekday_text"),
            "photos": results.get("photos"),
            "user_ratings_total": results.get("user_ratings_total"),
            "vicinity": results.get("vicinity"),
            "website": results.get("website"),
        }

        return data
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}, Error: {response.text}")

def fetch_places(query, api_key):
    """
    Fetch all place IDs for places in a specific query using the Google Places API.

    Parameters:
    - query (str): Search query for places.
    - api_key (str): Your Google Places API key.

    Returns:
    - list: A list of place IDs.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    places_data = []
    next_page_token = None

    while True:
        # Construire l'URL avec ou sans le token de page suivante
        if next_page_token:
            url = f"{base_url}?pagetoken={next_page_token}&key={api_key}"
        else:
            url = f"{base_url}?query={query}&language=fr&key={api_key}"

        # Récupérer les données de l'API
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            results = json_data.get("results", [])
            places_data.extend(results)  # Collecter tous les résultats

            # Vérifier s'il y a un token pour la page suivante
            next_page_token = json_data.get("next_page_token")
            if not next_page_token:
                break  # Sortie de la boucle si pas de pages supplémentaires

        else:
            raise Exception(f"Failed to fetch data. Status code: {response.status_code}, Error: {response.text}")

        # L'API de Google nécessite un délai avant d'utiliser le token suivant
        time.sleep(2)

    places_id = [place.get('place_id') for place in places_data]
    return places_id

def fetch_details_for_query(query, api_key):
    """
    Fetch place details for all places matching the query.

    Parameters:
    - query (str): The search query (e.g., "restaurants in Paris").
    - api_key (str): Your Google Places API key.

    Returns:
    - pd.DataFrame: A DataFrame containing details for all places.
    """
    global df_places  # Utiliser la variable globale pour éviter de réinitialiser à chaque appel

    # Obtenir les place IDs pour la requête
    place_ids = fetch_places(query, api_key)

    # Récupérer les détails pour chaque place_id unique
    for place_id in place_ids:
        try:
            place_details = fetch_place_details(place_id, api_key)
            if place_details is not None:  # Ajouter seulement si non None (évite les doublons)
                df_places = pd.concat([df_places, pd.DataFrame([place_details])], ignore_index=True)
        except Exception as e:
            print(f"Failed to fetch details for Place ID {place_id}: {e}")

    return df_places



# Exemple d'utilisation
api_key = "AIzaSyBV9UMNw83F7UN9bZSle8lAbaA1mID8ya0"  # Remplacer par votre vraie clé API
query = "Monunements à Paris"

# Catégories à rechercher
categories = [
    "monuments", "restaurants", "hotels", "parcs", "musées", "cafés", "bars", "bibliothèques", "théâtres", "cinémas"
]

# Liste des arrondissements de Paris
arrondissements = [f"{i}e arrondissement de Paris" for i in range(1, 21)]

# Boucle sur toutes les catégories et arrondissements
for category in categories:
    for arrondissement in arrondissements:
        query = f"{category} {arrondissement}"
        try:
            print(f"Recherche en cours pour : {query}")
            df_places = fetch_details_for_query(query, api_key)
            print(f"Nombre de lieux collectés : {df_places.shape[0]}")
        except Exception as e:
            print(f"Erreur pour {query}: {e}")

# Sauvegarde des données dans un fichier CSV pour une analyse ultérieure
df_places.to_csv("google_maps_paris_data.csv", index=False, encoding="utf-8")
print("Les données ont été enregistrées dans 'google_maps_paris_data.csv'")
