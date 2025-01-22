from django.db import models
import csv

class RoadTrip(models.Model):
    name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Evenement(models.Model):
    categorie = models.CharField(max_length=100)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    adresse = models.CharField(max_length=300)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.nom

class GooglePlace(models.Model):
    place_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    editorial_summary = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    types = models.JSONField(blank=True, null=True)  # List of place types
    rating = models.FloatField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    reviews = models.JSONField(blank=True, null=True)  # Store reviews as JSON
    current_opening_hours = models.JSONField(blank=True, null=True)
    formatted_address = models.CharField(max_length=300, blank=True, null=True)
    formatted_phone_number = models.CharField(max_length=50, blank=True, null=True)
    opening_hours = models.JSONField(blank=True, null=True)  # Weekly opening hours
    photos = models.JSONField(blank=True, null=True)  # Store photo references
    user_ratings_total = models.IntegerField(blank=True, null=True)
    vicinity = models.CharField(max_length=300, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


def load_places_from_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:  # Use utf-8-sig to handle BOM
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            GooglePlace.objects.update_or_create(
                place_id=row['place_id'],
                defaults={
                    'name': row.get('name'),
                    'editorial_summary': row.get('editorial_summary'),
                    'latitude': float(row['latitude']) if row.get('latitude') else None,
                    'longitude': float(row['longitude']) if row.get('longitude') else None,
                    'types': eval(row['types']) if row.get('types') else None,
                    'rating': float(row['rating']) if row.get('rating') else None,
                    'url': row.get('url'),
                    'reviews': eval(row['reviews']) if row.get('reviews') else None,
                    'current_opening_hours': row.get('current_opening_hours') == 'VRAI',
                    'formatted_address': row.get('formatted_address'),
                    'formatted_phone_number': row.get('formatted_phone_number'),
                    'opening_hours': eval(row['opening_hours']) if row.get('opening_hours') else None,
                    'photos': eval(row['photos']) if row.get('photos') else None,
                    'user_ratings_total': int(float(row['user_ratings_total'])) if row.get('user_ratings_total') else None,
                    'vicinity': row.get('vicinity'),
                    'website': row.get('website'),
                }
            )


from django.db import models

class Recommendation(models.Model):
    lieu_id = models.CharField(max_length=255)
    lieu_name = models.CharField(max_length=255)
    lieu_proche_id = models.CharField(max_length=255)
    lieu_proche_name = models.CharField(max_length=255)
    similitude = models.FloatField()

    def __str__(self):
        return f"{self.lieu_name} -> {self.lieu_proche_name} ({self.similitude})"
