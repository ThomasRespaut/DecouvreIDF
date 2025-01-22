import requests
import json
from dotenv import load_dotenv
load_dotenv()
import os

class GooglePlace:
    def __init__(self, api_key, place_id):
        self.api_key = api_key
        self.place_id = place_id
        self.url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={self.place_id}&key={self.api_key}"
        self.reviews = []
        self.place_details = {}

    def fetch_place_details(self):
        """
        Cette méthode effectue une requête GET à l'API Google Places pour obtenir les détails du lieu.
        Elle extrait ensuite les avis et les détails du lieu de la réponse JSON.
        """
        response = requests.get(self.url)
        data = response.json()

        # Vérifier si la réponse contient des détails et des avis
        if "result" in data:
            self.place_details = data["result"]
            if "reviews" in self.place_details:
                self.reviews = self.place_details["reviews"]
        else:
            print("Aucun détail trouvé ou erreur dans la réponse de l'API.")

    def display_reviews(self, max_reviews=10):
        """
        Affiche les avis, limité au nombre spécifié (par défaut 10).
        """
        if not self.reviews:
            print("Aucun avis disponible.")
            return

        # Limiter à 'max_reviews' avis
        for i, review in enumerate(self.reviews[:max_reviews]):
            print(f"Avis {i + 1}:")
            print(f"  Auteur: {review['author_name']}")
            print(f"  Note: {review['rating']} / 5")
            print(f"  Commentaire: {review['text']}")
            print("-" * 40)

    def save_to_json(self, filename):
        """
        Sauvegarde les détails du lieu et les avis dans un fichier JSON.
        """
        data_to_save = {
            "place_details": self.place_details,
            "reviews": self.reviews
        }

        # Ouvrir le fichier en mode écriture et sauvegarder les données au format JSON
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data_to_save, json_file, ensure_ascii=False, indent=4)
        print(f"Les résultats ont été sauvegardés dans '{filename}'.")


# Utilisation de la classe
if __name__ == "__main__":
    API_KEY = os.getenv("PLACES_API")
    PLACE_ID = "ChIJjx37cOxv5kcRPWQuEW5ntdk"  # Place ID du lieu

    # Créer une instance de la classe GooglePlace
    google_place = GooglePlace(API_KEY, PLACE_ID)

    # Récupérer les détails du lieu et les avis
    google_place.fetch_place_details()

    # Afficher les 10 premiers avis
    google_place.display_reviews(10)

    # Sauvegarder les résultats dans un fichier JSON
    google_place.save_to_json("place_reviews.json")
