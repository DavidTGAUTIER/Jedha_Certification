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

def remove_outliers(data, cols):
    for col in cols:
        if col == 'engine_power':
            outliers = 

def preprocessing(data):
