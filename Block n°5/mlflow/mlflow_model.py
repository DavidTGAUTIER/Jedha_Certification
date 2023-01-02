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

def train_test_splitting(data, test_size=0.2, random_state=123):
    df = data.copy()
    y = df.pop('rental_price_per_day')
    X = df

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test

def preprocessing(data):
    X = data.iloc[:,:-1]
    numerical_features, categorical_features = [], []

    for col in X.columns:
        if col in X.select_dtypes(include=['float64','int64']):
            numerical_features.append(col)
        else:
            categorical_features.append(col)

    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])

    return preprocessor

def mlflow_tracking(name="getaround-preds"):
    EXPERIMENT_NAME = name
    mlflow.set_experiment(EXPERIMENT_NAME)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    print("ID de l'experience :", experiment)
    return experiment

def mlflow_training(data, experiment, preprocessor, model_test_name='XGBOOST_testing', model_prod_name='XGBOOST_production'):
    df = data.copy()
    y = df.pop('rental_price_per_day')
    X = df
    X_train, X_test, y_train, y_test = train_test_splitting(data)
    xgboost = XGBRegressor(eta=0.1, n_estimators=150, min_child_weight=2, gamma=0.7, colsample_bytree=0.4)
    pipeline = Pipeline([('preprocessing', preprocessor),('prediction', model)])

    mlflow.sklearn.autolog(registered_model_name=model_name)
    with mlflow.start_run(experiment_id=experiment.experiment_id):
        model = xgboost
        pipe1 = pipeline
        pipe1.fit(X_train, y_train)
        y_test_pred = pipe1.predict(X_test)
        score_r2 = r2_score(y_test, y_test_pred)
        print('score R2 sur le test set :', score_r2)
        mlflow.log_metric('r2_score_test_set', score_r2)

    mlflow.sklearn.autolog(log_input_examples=True, registered_model_name=model_prod_name)
    with mlflow.start_run(experiment_id=experiment.experiment_id):
        model = xgboost
        pipe2 = pipeline
        pipe2.fit(X, y)
        y_test_pred = pipe2.predict(X_test)
        score_r2 = r2_score(y_test, y_test_pred)
        print('score R2 sur le test set :', score_r2)
        mlflow.log_metric('r2_score_test_set', score_r2)




