# DecouvreIDF

## Contexte du projet

Le projet DecouvreIDF s'inscrit dans le cadre d'un défi académique visant à explorer les problématiques liées au tourisme en Île-de-France. La région est riche en patrimoine culturel, artistique et naturel, attirant des millions de visiteurs chaque année. Toutefois, l'abondance d'informations disponibles en ligne rend difficile la planification d'un itinéraire optimisé et personnalisé pour les visiteurs. L'objectif de DecouvreIDF est de proposer une solution intelligente permettant d'agréger, filtrer et recommander les meilleures expériences en fonction des préférences de l'utilisateur.

## Problématique

Les touristes et résidents rencontrent souvent des difficultés dans la recherche d'activités adaptées à leurs centres d'intérêt et contraintes de temps. Les problématiques identifiées sont :

- La dispersion des informations sur différents sites web, rendant la recherche longue et inefficace.
- L'absence d'une solution centralisée permettant une personnalisation avancée des itinéraires.
- Le manque d'informations précises sur les itinéraires optimaux en termes de temps et de distance.
- Le besoin d'une approche responsable et écologique pour limiter l'impact environnemental des déplacements.

## Solution proposée

DecouvreIDF est une application web Django qui répond à ces enjeux en offrant les fonctionnalités suivantes :

- **Scraping et agrégation des données** :

  - Extraction des données depuis différentes sources web via les techniques de scraping (API, BeautifulSoup, Selenium).
  - Nettoyage et homogénéisation des données pour garantir leur fiabilité.

- **Personnalisation des recommandations** :

  - Utilisation d'un modèle de machine learning basé sur le clustering et le KNN pour proposer des lieux en fonction des préférences de l'utilisateur.
  - Visualisation interactive des recommandations avec TensorBoard.

- **Planification d'itinéraires optimaux** :

  - Calcul des trajets optimisés en tenant compte des distances et des préférences.
  - Intégration avec l'API RATP pour proposer des itinéraires en transport en commun.

- **Interface utilisateur intuitive** :

  - Sélection des catégories d'événements à travers une interface conviviale.
  - Génération automatique d'un résumé touristique grâce à un chatbot basé sur OpenAI.

## Fonctionnalités principales

- **Recherche d'événements** :

  - Festivals
  - Monuments
  - Musées
  - Hôtels
  - Campings
  - Restaurants
  - Parcs et Jardins
  - Cinémas

- **Calcul d'itinéraires** :

  - Géolocalisation des événements
  - Itinéraire optimisé
  - Détails du trajet via l'API RATP

- **Chatbot intégré** :

  - Résumé personnalisé des lieux sélectionnés
  - Conseils et recommandations

- **Visualisation avec TensorBoard** :

  - Représentation des recommandations par embeddings
  - Exploration des relations entre lieux

## Technologies utilisées

- **Back-end** : Django (Python)
- **Front-end** : HTML, CSS, JavaScript
- **Base de données** : SQLite
- **Modélisation et visualisation** : TensorFlow, Folium, OpenAI

## Installation

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/votre-repo/decouvreidf.git
   cd decouvreidf
   ```

2. Créer un environnement virtuel et installer les dépendances :

   ```bash
   python -m venv env
   source env/bin/activate  # Linux/MacOS
   env\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

3. Configurer la base de données :

   ```bash
   python manage.py migrate
   ```

4. Lancer le serveur :

   ```bash
   python manage.py runserver
   ```

5. Accéder à l'application :

   - [http://localhost:8000](http://localhost:8000)

## Structure du projet

```
DecouvreIDF/
|-- app/
|   |-- static/
|   |-- templates/
|   |-- models.py
|   |-- views.py
|   |-- forms.py
|-- manage.py
|-- requirements.txt
```

## Configuration TensorBoard

L'application permet de visualiser les embeddings des lieux recommandés. Pour lancer TensorBoard :

```bash
python manage.py runserver
```

Puis accéder à [http://localhost:6010](http://localhost:6010).

## Utilisation

1. Sélectionner le nombre d'événements par catégorie.
2. Rechercher les lieux correspondants.
3. Obtenir un itinéraire optimal.
4. Visualiser les recommandations via TensorBoard.

## Auteurs

- **Thomas RESPAUT**
- **Edvin AHRATINA**

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

