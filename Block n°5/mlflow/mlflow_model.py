import mlflow
import os

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline

from xgboost import XGBRegressor

link = os.environ["APP_URI"]
mlflow.set_tracking_uri(link)
print(f'Lien du site mlflow : {link}')

def loading():
    print('Importation des données')
    data = pd.read_csv('../src/get_around_pricing_project.csv')
    data = data.iloc[:,1:]
    return data

def remove_outliers(data, cols, std=2):
    for col in cols:
        if col == 'engine_power':
            abs_mean_difference = abs(data['engine_power'] - data['engine_power'].mean())
            std_mean_difference = abs_mean_difference <= std*data['engine_power'].std()
            min_values = data['engine_power'] > 50
            non_outliers = (std_mean_difference) & (min_values)
            data = data[non_outliers]
        if col == 'mileage':
            abs_mean_difference = abs(data['mileage'] - data['mileage'].mean())
            std_mean_difference = abs_mean_difference <= std*data['mileage'].std()
            min_values = data['engine_power'] >= 0
            non_outliers = (std_mean_difference) & (min_values)
            data = data[non_outliers]
    return data

def preprocessing(data):
    y = data.pop('rental_price_per_day')
    X = data
