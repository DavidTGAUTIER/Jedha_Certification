import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy
import plotly.figure_factory as ff
import plotly.io as pio
import copy
import boto3
import os

st.set_page_config(
    page_title = "Get Around Project",
    page_icon = " ",
    layout = "wide"
)

st.sidebar.write("Dashboard made by [@DavidT](https://github.com/DavidTGAUTIER)")

st.header("Analyse des prix des locations")

st.subheader("A la recherche du seuil optimal pour optimiser la rentabilité des courses")

st.markdown("""Pour améliorer l'expérience de l'utilisateur, nous devons répondre à ces questions :

* Combien d'argent perd un propriétaire de véhicule à cause des retards ?
* Comment quantifier le ratio risques/bénéfices ?
* Quel seuil devrions nous utiliser pour améliorer le ratio risques/bénéfices ?

Nous allons prendre une durée de location égale à 24h.

Nous avons le choix de prendre la median ou la moyenne pour connaitre le prix (moyen ou median) d'une course. Regardons la distribution de cette variable""")

st.markdown("""
    ------------------------
""")

st.subheader("Chargement des données")

aws=False
local=True

data_load_state = st.text('Chargement des données...')

if aws:

    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = storage.Client(credentials=credentials)
    # permet de memorizer les executions de fonctions (cad les mettre en cache pour eviter d'avoir besoin de les relancer : on choisit une valeur de 900s, cad que si pendant 15min il y a un changement, charge auto la fonction)
    @st.experimental_memo(ttl=600)
    def import_data(bucket_name, file_path):
        bucket = client.bucket(bucket_name)
        content = bucket.blob(file_path).download_as_string().decode('utf-8')
        return content

    bucket_name = "get_around_data"
    file_path_pricing = "pricing_cleaned.csv"
    file_path_delays = "delays_cleaned.csv"

    data_pricing = import_data(bucket_name, file_path_pricing)
    data_delays = import_data(bucket_name, file_path_delays)
    data_pricing = pd.read_csv(io.StringIO(data_pricing))
    data_delays = pd.read_csv(io.StringIO(data_delays))


if local:
    # Importation des données depuis environnement local
    @st.cache(allow_output_mutation=True)
    def import_data(path):
        data = pd.read_csv(path)
        return data

    path_pricing = './src/pricing_cleaned.csv'
    path_delays = './src/delays_cleaned.csv'

    data_pricing = import_data(path_pricing)
    data_delays = import_data(path_delays)

data_load_state.text("Données disponibles")

fig = px.histogram(data_pricing['rental_price_per_day'], color_discrete_sequence=['cyan','royalblue'])
st.plotly_chart(fig, use_container_width=True)
   
