
import streamlit as st
import requests
import pandas as pd
import numpy as np

st.title("🏁 F1 Predictor App - 2025")

# Ophalen van races met fallback-optie
def get_races(year):
    url = f"https://ergast.com/api/f1/{year}.json"
    r = requests.get(url).json()
    races = r["MRData"]["RaceTable"]["Races"]
    return races

# Automatische volgende race ophalen of fallback selectie
def select_race():
    races = get_races(2025)
    today = pd.Timestamp.today().date()
    future_races = [race for race in races if pd.to_datetime(race['date']).date() >= today]

    if future_races:
        return future_races[0]
    else:
        st.warning("Geen automatische aankomende race gevonden. Kies handmatig:")
        race_names = [f"{race['raceName']} ({race['date']})" for race in races]
        selected_race = st.selectbox("Selecteer race", race_names)
        return races[race_names.index(selected_race)]

next_race = select_race()
st.subheader(f"Aankomende race: {next_race['raceName']} op {next_race['date']}")

# Hier gaat jouw bestaande code verder (coureurs ophalen, kwalificatie, voorspellingen etc.)
st.markdown("_(Voeg hier jouw bestaande voorspellingen en data-analyse toe.)_")
