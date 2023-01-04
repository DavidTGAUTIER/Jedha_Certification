import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import copy
import boto3
import os

st.set_page_config(
    page_title = "Get Around Project",
    page_icon = " ",
    layout = "wide"
)

st.title("Analyse des retards")

st.markdown("""Dashboard pour le projet GetAround.

Il contient une analyse des durées de deplacements des chauffeurs utilisant l'application GetAround. 
Comme certains chauffeurs rendent les véhicules en retard, le but de ce projet est de mettre en place un **délai minimum entre deux locations** : \n
un véhicule ne s'affichera pas dans les résultats de recherche si les heures d'enregistrement ou de départ demandées sont trop proches d'une location déjà réservée **sans que cela pénalise financièrement les propriétaires de ces véhicules**.

Nous avons choisi de diviser en deux parties cette analyse:
la première partie concerne les retards des chauffeurs alors que la seconde partie couvre les types de véhicules et le prix d'une location.""")

st.sidebar.write("Dashboard made by [@DavidT](https://github.com/DavidTGAUTIER)")
st.sidebar.success("Navigation")

st.markdown("""
    ------------------------
""")

st.header("Chargement des données")


aws=False
local=True

if aws:
    @st.cache
    # Importation des données depuis AWS s3
    def import_data():

        client = boto3.client(
            "s3",
            aws_access_key_id = os.getenv("s3_key"),
            aws_secret_access_key=os.getenv("s3_secret")
        )

        response = client.get_object(Bucket = "app-getaround",
                                    Key = "get_around_delay_analysis.csv")
            
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status != 200:
            return f"Erreur de connexion avec AWS s3 - Status code :{status}"

        else:
            return pd.read_csv(response.get("Body"))

if local:
    @st.cache
    # Importation des données depuis environnement local
    def import_data():
        data = pd.read_csv('./src/delays_cleaned.csv')
        return data

data_load_state = st.text('Chargement des données...')
data = import_data()
data_load_state.text("Données disponibles")

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)


