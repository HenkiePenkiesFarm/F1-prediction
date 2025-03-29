import streamlit as st
import pandas as pd
import numpy as np
import requests
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt

st.title("F1 Predictor: Volgende Race (API-gevoed)")

# -------------------------
# STAP 1: Aankomende race ophalen uit Ergast API
# -------------------------
@st.cache_data
def get_next_race():
    url = "https://ergast.com/api/f1/current.json"
    response = requests.get(url)
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    today = pd.Timestamp.today().date()
    for race in races:
        race_date = pd.to_datetime(race["date"]).date()
        if race_date >= today:
            return race
    return None

next_race = get_next_race()
if next_race:
    st.subheader(f"Aankomende race: {next_race['raceName']} ({next_race['date']})")
    round_number = int(next_race["round"])
    season = int(next_race["season"])
    circuit_name = next_race["Circuit"]["circuitName"]
    country = next_race["Circuit"]["Location"]["country"]
    st.markdown(f"**Circuit:** {circuit_name} - {country}")
else:
    st.warning("Geen aankomende race gevonden.")
    st.stop()


# -------------------------
# STAP 2: Haal lijst met deelnemende coureurs op in deze race
# -------------------------
@st.cache_data
def get_race_drivers(season, round_number):
    url = f"https://ergast.com/api/f1/{season}/{round_number}/results.json"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    results = r.json()["MRData"]["RaceTable"]["Races"]
    if not results:
        return []
    drivers = results[0]["Results"]
    driver_list = []
    for d in drivers:
        code = d["Driver"].get("code", d["Driver"]["driverId"])
        driver_list.append({
            "id": d["Driver"]["driverId"],
            "name": f"{d['Driver']['givenName']} {d['Driver']['familyName']} ({code})"
        })
    return driver_list

driver_list = get_race_drivers(season, round_number)
if not driver_list:
    st.warning("Geen coureurs gevonden voor deze race.")
    st.stop()

selected_driver_id = st.selectbox("Kies een coureur voor voorspelling", [d["name"] for d in driver_list])

# -------------------------
# COUREURSECTIE BOVENAAN MET FOTO
# -------------------------
st.markdown("## Geselecteerde coureur")

driver_info = next((d for d in driver_list if d["name"] == selected_driver_id), None)
if driver_info:
    img_url = f"https://cdn.racingnews365.com/2022/Drivers/{selected_driver_code.upper()}.jpg"
    st.image(img_url, width=120, caption=selected_driver_id)
    st.markdown(f"### {selected_driver_id}")

selected_driver_code = [d["id"] for d in driver_list if d["name"] == selected_driver_id][0]

# -------------------------
# STAP 3: Haal kwalificatiegegevens op voor deze race
# -------------------------
@st.cache_data
def get_qualifying_data(season, round_number):
    url = f"https://ergast.com/api/f1/{season}/{round_number}/qualifying.json"
    r = requests.get(url)
    if r.status_code != 200:
        return pd.DataFrame()
    races = r.json()["MRData"]["RaceTable"]["Races"]
    if not races:
        return pd.DataFrame()
    quals = races[0]["QualifyingResults"]
    rows = []
    for q in quals:
        driver_id = q["Driver"]["driverId"]
        pos = int(q["position"])
        rows.append({"driverId": driver_id, "qualifyingPosition": pos})
    return pd.DataFrame(rows)

qual_df = get_qualifying_data(season, round_number)

# -------------------------
# STAP 4: Voorspelling op basis van kwalificatiepositie
# -------------------------
if qual_df.empty:
    st.warning("Kwalificatiegegevens nog niet beschikbaar.")
    st.stop()

if selected_driver_code not in qual_df["driverId"].values:
    st.warning("Geselecteerde coureur heeft nog geen kwalificatie gereden.")
    st.stop()

# Dummy voorspelling (plaatsvervanger voor ML-model op basis van positie)
driver_qual_pos = int(qual_df[qual_df["driverId"] == selected_driver_code]["qualifyingPosition"].values[0])
st.subheader("Voorlopige voorspelling (op basis van kwalificatie)")
voorspelling = round(driver_qual_pos * np.random.uniform(0.9, 1.3), 1)
st.metric("Verwachte finishpositie", f"{voorspelling}")

st.caption("Zodra trainingsdata beschikbaar is, kunnen die worden toegevoegd aan het model.")

