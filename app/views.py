from django import forms
from .models import Evenement, GooglePlace
import math
import json
from datetime import datetime
import folium
import re
from .models import Evenement
from openai import OpenAI
import os
import subprocess
import threading
import requests
import joblib
import pandas as pd
import tensorflow as tf
from tensorboard.plugins import projector
from django.http import JsonResponse
from django.shortcuts import render
import time

# Définition des chemins vers les fichiers nécessaires
BASE_DIR = r"C:\Users\thoma\PycharmProjects\DecouvreIDF\app\model"
KNN_MODEL_PATH = os.path.join(BASE_DIR, "knn_model.pkl")
RECOMMENDATIONS_PATH = os.path.join(BASE_DIR, "recommendations.csv")
TENSORBOARD_LOG_DIR = os.path.join(BASE_DIR, "logs_embeddings")


# Fonction pour démarrer TensorBoard en arrière-plan
def start_tensorboard():
    """Lancer TensorBoard en arrière-plan."""
    # Nettoyer d'anciens processus TensorBoard en utilisant taskkill sur Windows
    subprocess.call("taskkill /F /IM tensorboard.exe", shell=True)

    cmd = f"tensorboard --logdir={TENSORBOARD_LOG_DIR} --host=localhost --port=6010"
    with open(os.path.join(BASE_DIR, "tensorboard_log.txt"), "w") as log_file:
        subprocess.Popen(cmd, shell=True, stdout=log_file, stderr=log_file)

    # Attendre quelques secondes pour s'assurer que TensorBoard démarre
    time.sleep(5)


# Fonction pour vérifier si TensorBoard est déjà lancé
def is_tensorboard_running():
    """Vérifie si TensorBoard est actif sur le port 6010."""
    try:
        response = requests.get("http://localhost:6010")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def tensorboard_view(request):
    """Vue Django pour afficher TensorBoard et charger les données."""

    # Charger le modèle KNN
    if not os.path.exists(KNN_MODEL_PATH):
        return JsonResponse({"error": "Fichier knn_model.pkl introuvable"}, status=500)

    model_knn = joblib.load(KNN_MODEL_PATH)
    print("Modèle KNN chargé avec succès.")

    # Charger les recommandations
    # Charger les recommandations
    if not os.path.exists(RECOMMENDATIONS_PATH):
        return JsonResponse({"error": "Fichier recommendations.csv introuvable"}, status=500)

    recommendations_df = pd.read_csv(RECOMMENDATIONS_PATH, encoding="utf-8")

    # Vérifier si les colonnes ont les bons noms et ajuster si nécessaire
    recommendations_df.columns = recommendations_df.columns.str.strip().str.replace(' ', '_')

    print("Fichier des recommandations chargé avec succès.")

    print(recommendations_df)



    # Vérification des colonnes attendues
    expected_columns = ['Lieu_ID', 'Lieu', 'Lieu_Proche_ID', 'Lieu_Proche', 'Distance']
    if not all(col in recommendations_df.columns for col in expected_columns):
        return JsonResponse({"error": "Les colonnes du fichier CSV ne sont pas conformes"}, status=500)

    # Ajouter des détails du lieu à partir du modèle GooglePlace
    places_info = {}
    for index, row in recommendations_df.iterrows():
        place = GooglePlace.objects.filter(place_id=row['Lieu_ID']).first()
        if place:
            places_info[row['Lieu_ID']] = {
                'name': place.name if place.name else 'Non disponible',
                'summary': place.editorial_summary if place.editorial_summary else 'Non disponible',
                'rating': place.rating if place.rating else 'Non disponible',
                'address': place.formatted_address if place.formatted_address else 'Non disponible',
                'phone': place.formatted_phone_number if place.formatted_phone_number else 'Non disponible',
                'website': place.website if place.website else '#',
                'reviews': place.reviews if place.reviews else 'Aucun avis',
            }
        else:
            places_info[row['Lieu_ID']] = {
                'name': 'Lieu inconnu',
                'summary': 'Non disponible',
                'rating': 'Non disponible',
                'address': 'Non disponible',
                'phone': 'Non disponible',
                'website': '#',
                'reviews': 'Aucun avis',
            }

    # Sauvegarde des colonnes spécifiques pour la visualisation
    META_FILE = "metadata.tsv"
    metadata_path = os.path.join(TENSORBOARD_LOG_DIR, META_FILE)
    recommendations_df[['Lieu_ID', 'Lieu', 'Lieu_Proche_ID', 'Lieu_Proche']].fillna('Inconnu').to_csv(
        metadata_path, index=False, header=False, encoding='utf-8'
    )

    # Générer des embeddings factices pour la visualisation
    embedding_var = tf.Variable(tf.random.normal([len(recommendations_df), 10]), name='place_embeddings')

    # Configuration de TensorBoard
    config = projector.ProjectorConfig()
    embedding = config.embeddings.add()
    embedding.tensor_name = embedding_var.name
    embedding.metadata_path = META_FILE

    # Sauvegarde des embeddings pour TensorBoard
    ckpt = tf.train.Checkpoint(embeddings=embedding_var)
    ckpt.save(os.path.join(TENSORBOARD_LOG_DIR, "embeddings_ckpt"))

    projector.visualize_embeddings(TENSORBOARD_LOG_DIR, config)
    print("Embeddings préparés pour TensorBoard.")

    # Vérifier si TensorBoard est déjà lancé et le démarrer si nécessaire
    if not is_tensorboard_running():
        thread = threading.Thread(target=start_tensorboard)
        thread.daemon = True
        thread.start()

    tensorboard_url = "http://localhost:6010"

    return render(request, 'trips/tensorboard.html', {
        'tensorboard_url': tensorboard_url,
        'recommendations': recommendations_df.to_dict(orient='records'),
        'places_info': json.dumps(places_info, ensure_ascii=False)
    })


# Formulaire pour les coordonnées et le rayon
class LocationForm(forms.Form):
    latitude = forms.FloatField(label="Latitude", initial=48.8566, required=True)
    longitude = forms.FloatField(label="Longitude", initial=2.3522, required=True)
    rayon = forms.FloatField(label="Rayon en kilomètres", initial=5, required=True)

class ChatbotForm(forms.Form):
    chat_message = forms.CharField(label="Message au chatbot", widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=True)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def fetch_ratp_journey(from_lat, from_lon, to_lat, to_lon):
    api_key = os.getenv('RATP_API_KEY')
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/journeys"

    params = {
        'from': f"{from_lon};{from_lat}",
        'to': f"{to_lon};{to_lat}",
        'datetime': datetime.now().strftime('%Y%m%dT%H%M%S'),
        'datetime_represents': 'departure',
        'max_nb_journeys': 1,
    }

    headers = {'Accept': 'application/json', 'apikey': api_key}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'journeys' in data and len(data['journeys']) > 0:
                journey = data['journeys'][0]
                return {
                    'duration': journey.get('duration', 'N/A'),
                    'departure_time': journey.get('departure_date_time', 'N/A'),
                    'arrival_time': journey.get('arrival_date_time', 'N/A'),
                }
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse RATP: {e}")
            return None

    print(f"Erreur API RATP: {response.status_code}")
    return None

def calculate_best_route(locations):
    """
    Trouver un itinéraire proche de l'optimal pour visiter tous les lieux donnés en utilisant une heuristique gloutonne.
    """
    if not locations:
        return [], 0

    # Démarrer depuis le premier point
    start = locations[0]
    unvisited = locations[1:]
    current_location = start
    route = [start]
    total_distance = 0

    while unvisited:
        # Trouver le point le plus proche parmi les non-visités
        next_location = min(unvisited, key=lambda loc: haversine(current_location[0], current_location[1], loc[0], loc[1]))
        total_distance += haversine(current_location[0], current_location[1], next_location[0], next_location[1])
        route.append(next_location)
        current_location = next_location
        unvisited.remove(next_location)

    # Retour au point de départ pour compléter le circuit
    total_distance += haversine(current_location[0], current_location[1], start[0], start[1])
    route.append(start)

    return route, total_distance


# Fonction pour récupérer la réponse du chatbot
def fetch_chatbot_response(client, user_message, session_messages):
    try:

        # Ajout de l'historique des messages dans la requête
        messages = session_messages
        messages.append(({"role": "user", "content": user_message}))

        # Appel à l'API OpenAI avec l'historique des messages
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Vous pouvez remplacer par un autre modèle si nécessaire
            messages=messages, # Nombre maximum de tokens dans la réponse
            temperature=0.7,
        )

        chatbot_response = response.choices[0].message.content

        print(chatbot_response)

        return chatbot_response, session_messages
    except Exception as e:
        print(f"Erreur : {e}")
        return "Désolé, je n'ai pas pu obtenir une réponse.", session_messages

def index(request):
    # Récupérer les messages de la session, sinon initialiser la liste vide
    if 'messages' in request.session:
        del request.session['messages']

    if 'messages' not in request.session:
        request.session['messages'] = [
            {"role": "developer", "content": "Tu es un assistant spécialisé dans l'organisation de road trips mémorables. Ton rôle est de fournir un résumé captivant du voyage de l'utilisateur, en mettant en avant les monuments et bâtiments qu'il explorera. Présente ce récapitulatif de manière inspirante, comme le ferait une office du tourisme, en insistant sur les aspects uniques et les expériences inoubliables qui l'attendent. Fais en sorte que l'utilisateur ressente l'excitation et l'envie de partir à la découverte de ces lieux. Il faut que le texte soit court, quelques phrases. Le planning ne doit pas être trés long."}
        ]

    messages = request.session['messages']

    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=openai_api_key)


    categorized_evenements = {}
    evenements_limites_par_categorie = {}
    categories = []
    route_details = []
    total_distance = 0

    colors = {
        "Festivals": "blue",
        "Monuments": "purple",
        "Musées": "orange",
        "Hôtels": "darkblue",
        "Campings": "darkgreen",
        "Restaurants": "red",
        "Parcs et Jardins": "green",
        "Cinémas": "pink",
    }

    # Initialiser les formulaires
    location_form = LocationForm(request.POST or None)
    chatbot_form = ChatbotForm(request.POST or None)

    if request.method == 'POST':

        if 'chatbot' in request.POST:
            user_message = request.POST.get('chat_message', '')
            chatbot_response, messages = fetch_chatbot_response(client, user_message, messages)

            # Sauvegarder l'historique des messages dans la session
            request.session['messages'] = messages

        if 'search' in request.POST and location_form.is_valid():
            # Récupération des catégories sélectionnées
            categories = {
                'Festivals': int(request.POST.get('categories[Festivals]', 0)),
                'Monuments': int(request.POST.get('categories[Monuments]', 0)),
                'Musées': int(request.POST.get('categories[Musées]', 0)),
                'Hôtels': int(request.POST.get('categories[Hôtels]', 0)),
                'Campings': int(request.POST.get('categories[Campings]', 0)),
                'Restaurants': int(request.POST.get('categories[Restaurants]', 0)),
                'Parcs et Jardins': int(request.POST.get('categories[Parcs et Jardins]', 0)),
                'Cinémas': int(request.POST.get('categories[Cinémas]', 0)),
            }

            latitude_centrale = location_form.cleaned_data['latitude']
            longitude_centrale = location_form.cleaned_data['longitude']
            rayon_km = location_form.cleaned_data['rayon']

            evenements = Evenement.objects.all()

            evenements_tries = sorted(
                evenements,
                key=lambda ev: haversine(latitude_centrale, longitude_centrale, ev.latitude, ev.longitude)
            )

            evenements_filtrés_par_categorie = [
                ev for ev in evenements_tries
                if haversine(latitude_centrale, longitude_centrale, ev.latitude, ev.longitude) <= rayon_km
                and categories.get(ev.categorie, 0) > 0
            ]

            categorized_evenements = {}
            for ev in evenements_filtrés_par_categorie:
                categorized_evenements.setdefault(ev.categorie, []).append(ev)

            evenements_limites_par_categorie = {
                cat: ev_list[:categories.get(cat, 0)]
                for cat, ev_list in categorized_evenements.items()
            }

            map_ = folium.Map(location=[latitude_centrale, longitude_centrale], zoom_start=12)

            user_message = str(evenements_limites_par_categorie)
            #print(client, user_message, messages)
            chatbot_response, messages = fetch_chatbot_response(client, user_message, messages)

            # Convertir chatbot_response en dictionnaire si ce n'est pas déjà le cas
            if isinstance(chatbot_response, str):
                try:
                    chatbot_response = json.loads(chatbot_response)  # Convertir la chaîne JSON en dict
                except json.JSONDecodeError:
                    chatbot_response = {"content": chatbot_response}  # Fallback si non JSON

            # Récupérer uniquement la partie "content"
            content = chatbot_response.get('content', '')
            # Nettoyage du texte
            content = re.sub(r'\s+', ' ',
                             content)  # Remplacer les espaces multiples et retours à la ligne par un espace

            # Nettoyage du texte
            content = re.sub(r'\n', ' ', content)  # Supprimer les retours à la ligne
            content = re.sub(r'\*\*', '', content)  # Supprimer les doubles astérisques **
            content = re.sub(r'\s+', ' ', content)  # Remplacer les espaces multiples par un seul espace
            content = re.sub(r'\s([?.!,;:])', r'\1', content)  # Supprimer les espaces avant la ponctuation
            content = re.sub(r'([?.!,;:])\1+', r'\1', content)  # Supprimer les répétitions de ponctuation
            content = content.strip()  # Supprimer les espaces de début et de fin

            message = {"role": "assistant", "content": chatbot_response}

            messages.append(message)

            # Sauvegarder l'historique des messages dans la session
            request.session['messages'] = messages

            coordonnees_filtrées = []
            for cat, ev_list in evenements_limites_par_categorie.items():
                for ev in ev_list:
                    coordonnees_filtrées.append((ev.latitude, ev.longitude))
                    folium.Marker(
                        location=[ev.latitude, ev.longitude],
                        popup=f"<b>{ev.nom}</b><br>{ev.description}",
                        icon=folium.Icon(color=colors.get(cat, "gray"))
                    ).add_to(map_)

            if coordonnees_filtrées:
                folium.PolyLine(
                    coordonnees_filtrées,
                    color="blue",
                    weight=2.5,
                    opacity=0.7
                ).add_to(map_)

                for i, (lat, lon) in enumerate(coordonnees_filtrées):
                    nom_evenement = next(
                        (ev.nom for ev in evenements_filtrés_par_categorie if ev.latitude == lat and ev.longitude == lon),
                        "Inconnu"
                    )
                    route_details.append({
                        "latitude": lat,
                        "longitude": lon,
                        "nom": nom_evenement
                    })

                    if i > 0:
                        lat_prev, lon_prev = coordonnees_filtrées[i - 1]
                        total_distance += haversine(lat_prev, lon_prev, lat, lon)

                legend_html = f"""
                <div style="
                    position: fixed;
                    bottom: 20px; left: 20px;
                    width: 250px; max-height: 40vh;
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid grey;
                    border-radius: 5px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                    z-index: 9999;
                    font-size: 14px;
                    overflow-y: auto;
                    padding: 15px;">
                    <b style="font-size: 16px; color: #333;">Légende</b><br>
                    {"".join([
                        f"<div style='display: flex; align-items: center; margin-bottom: 5px;'>"
                        f"<span style='display: inline-block; width: 20px; height: 20px; background-color: {color}; border-radius: 3px; margin-right: 10px;'></span>"
                        f"<span style='color: #555;'>{category}</span></div>"
                        for category, color in colors.items()
                    ])}
                </div>
                """

                # Ajouter la légende au rendu HTML de la carte
                map_.get_root().html.add_child(folium.Element(legend_html))

            request.session.update({
                'route': route_details,
                'total_distance': total_distance,
                'map_html': map_._repr_html_(),
                'categories': categories,
            })

        if 'fetch_ratp' in request.POST and 'route' in request.session:
            route_details = request.session['route']
            for i in range(len(route_details) - 1):
                travel_info = fetch_ratp_journey(
                    route_details[i]['latitude'], route_details[i]['longitude'],
                    route_details[i + 1]['latitude'], route_details[i + 1]['longitude']
                )
                route_details[i]['travel_info'] = {
                    'duration': travel_info.get('duration', 0) // 60 if travel_info else 'N/A',
                    'departure_time': datetime.strptime(travel_info.get('departure_time', 'N/A'), '%Y%m%dT%H%M%S').strftime('%Y-%m-%d %H:%M') if travel_info and travel_info.get('departure_time') != 'N/A' else 'N/A',
                    'arrival_time': datetime.strptime(travel_info.get('arrival_time', 'N/A'), '%Y%m%dT%H%M%S').strftime('%Y-%m-%d %H:%M') if travel_info and travel_info.get('arrival_time') != 'N/A' else 'N/A',
                }
            request.session['route'] = route_details

    return render(request, 'trips/index.html', {
        'location_form': location_form,
        'chatbot_form': chatbot_form,
        'map': request.session.get('map_html'),
        'categorized_evenements': evenements_limites_par_categorie,
        'route_details': request.session.get('route', []),
        'total_distance': request.session.get('total_distance', 0),
        'messages': messages,
        'categories': categories,
    })
