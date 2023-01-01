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

