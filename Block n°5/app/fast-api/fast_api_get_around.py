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

# On definit une classe avec toutes les features pour faire les endpoints sur les predictions
class Features(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

# Pour toutes les colonnes (exceptées les Bools) on crée des fonctions qui vont tester si les valeurs en input sont correctes
    @validator('model_key')
    def model_key_is_valid(cls, v):
        assert v in ['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors','Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT','Subaru', 'Toyota', 'Suzuki', 'Yamaha'], \
        f"model_key doit être une des valeurs de cette liste: ['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford', \
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors','Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati', \
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT','Subaru', 'Toyota', 'Suzuki', 'Yamaha']"
        return v

    @validator('fuel')
    def fuel_is_valid(cls, v):
        assert v in ['diesel', 'petrol', 'hybrid_petrol', 'electro'], \
        f"fuel doit être une des valeurs de cette liste: ['diesel', 'petrol', 'hybrid_petrol', 'electro']"
        return v
    
    @validator('paint_color')
    def paint_color_is_valid(cls, v):
        assert v in ['black', 'white', 'red', 'silver', 'grey', 'blue', 'orange','beige', 'brown', 'green'], \
        f"paint_color doit être une des valeurs de cette liste: ['black', 'white', 'red', 'silver', 'grey', 'blue', 'orange','beige', 'brown', 'green']"
        return v
    
    @validator('car_type')
    def car_type_is_valid(cls, v):
        assert v in ['sedan', 'hatchback', 'suv', 'van', 'estate', 'convertible', 'coupe', 'subcompact'], \
        f"car_type doit être une des valeurs de cette liste: ['sedan', 'hatchback', 'suv', 'van', 'estate', 'convertible', 'coupe', 'subcompact']"
        return v

    @validator('mileage')
    def mileage_is_positive(cls, v):
        assert v >= 0, f"mileage doit être positif"
        return v
    
    @validator('engine_power')
    def engine_power_is_positive(cls, v):
        assert v >= 0, f"engine_power doit être positif"
        return v


# endpoint de la prediction du prix d'une voiture
@app.post("/predict")
async def predict(features:Features):
    """Prediction du prix d'une voiture. 
Exemple de données d'entrée:
{
  "model_key": "Citroën",
  "mileage": 140411,
  "engine_power": 100,
  "fuel": "diesel",
  "paint_color": "black",
  "car_type": "convertible",
  "private_parking_available": true,
  "has_gps": true,
  "has_air_conditioning": false,
  "automatic_car": false,
  "has_getaround_connect": true,
  "has_speed_regulator": true,
  "winter_tires": true
}
Devrait retourner : "prediction": 106

Toutes les entrées sont sensibles à la casse. 
La liste des valeurs possibles pour les colonnes catégorielles est disponible dans le endpoint /unique-values. 
Des valeurs erronées renverront un message d'erreur spécifique."""

    features = dict(features)
    input_df = pd.DataFrame(columns=['model_key', 'mileage', 'engine_power', 'fuel', 'paint_color','car_type', 'private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect','has_speed_regulator', 'winter_tires'])
    input_df.loc[0] = list(features.values())
    # Load the model & preprocessor
    model = joblib.load('gbr_model.pkl')
    prep = joblib.load('preprocessor.pkl')
    X = prep.transform(input_df)
    pred = model.predict(X)
    return {"prediction" : pred[0]}
