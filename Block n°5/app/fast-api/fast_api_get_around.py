from fastapi import FastAPI, Request
import uvicorn
from pydantic import BaseModel, validator
from typing import  Union
import joblib
import json
import pandas as pd 

app = FastAPI(
    title='GetAround API',
    description="""Voici l'API du projet Get Around pour prédire le prix d'un véhicule de location. 
    Cette API est basé sur le framework FastAPI et contient un dataset de 10k lignes et 9 colonnes :
    * `model_key` : Marque du véhicule emprunté
    * `mileage` : Nombre de kms
    * `engine_power` : Puissance du moteur
    * `fuel` : type de carburant
    * `paint_color` : couleur du véhicule
    * `car_type` : type de véhicule (sport, Van, coupé,...)
    * `private_parking_available` : si parking privé disponible (Oui ou Non)
    * `has_gps` : possède un GPS (Oui ou Non)
    * `has_air_conditioning` : possède un climatiseur (Oui ou Non)
    * `automatic_car` : le véhicule est il automatique (Oui ou Non)
    * `has_getaround_connect` : possède l'option GetAround Connect (permet un check-in sans rencontre entre proprio / locataire) (Oui ou Non)
    * `has_speed_regulator` : possède un régulateur de vitesse (Oui ou Non)
    * `winter_tires` : possède des pneus d'hiver (pour la neige) (Oui ou Non)
    * `rental_price_per_day` : prix de la location pour la journée (Target)
    
    Dans cette API, on peut trouver 6 endpoints:
    - **/preview**: renvoie une overview du dataset (sous forme de dictionnaire)
    - **/predict**: retourne le prix prédit d'une voiture
    - **/unique-values**: renvoie les valeurs uniques d'une colonne (sous forme de liste)
    - **/groupby**: renvoie les données groupées d'une colonne (sous forme de dictionnaire)
    - **/filter-by**: renvoie les données filtrées d'une colonne (sous forme de dictionnaire)
    - **/quantile**: renvoie le quantile d'une colonne (sous forme de flottant ou de chaîne)"""
)

@app.get("/")
async def root():
    message = """Bienvenue dans l'API Getaround. Ajoutez /docs à cette adresse pour voir la documentation de l'API sur le dataset contenant les prix des locations"""
    return message

